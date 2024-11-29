from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import END
from typing import Annotated, Optional
import pandas as pd
import folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.io as pio
from s3_client import S3Client
import io
from db import LangGraphInput
from langchain_core.tools import tool


def create_agent(llm, tools, system_message: str, include_input: Optional[bool] = False):
    """Create an agent."""

    input_placeholder = PromptTemplate.from_template("{input}")
    
    base_system_message = (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        " You have access to the following tools: {tool_names}.\n{system_message}"
    )
    
    if include_input:
        base_system_message += "\nHere is the input data: " + input_placeholder.template
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", base_system_message),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

@tool
def folium_tool(input: Annotated[LangGraphInput, "The input data and specifications to create a folium map"]):
    """Create various types of maps using Folium based on the provided specifications."""
    try:
        s3_client = S3Client()
        docs = input.documents
        spec = input.chart_spec
        entity = input.entity

        m = folium.Map(location=[0, 0], zoom_start=2)  # Default world view

        if spec.chart_type == "scatter_map":
            for doc in docs:
                folium.CircleMarker(
                    [doc.latitude, doc.longitude],
                    radius=5,
                    popup=doc.title,
                    color="red",
                    fill=True
                ).add_to(m)
        elif spec.chart_type == "heatmap":
            heat_data = [[doc.latitude, doc.longitude] for doc in docs]
            HeatMap(heat_data).add_to(m)
        elif spec.chart_type == "choropleth":
            # Assuming one of the data_fields is the country code
            country_data = {getattr(doc, spec.data_fields[0]): getattr(doc, spec.data_fields[1]) for doc in docs}
            folium.Choropleth(
                geo_data='countries.geo.json',
                name=spec.title,
                data=country_data,
                key_on='feature.id',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=spec.description
            ).add_to(m)
        else:
            return {"type": "error", "content": f"Unsupported chart type for Folium: {spec.chart_type}"}
    
    
        # Save map to a PNG image
        img_data = m._to_png(5)

        # Generate a unique filename
        filename = f"{entity.id}.png"

        # Upload to S3
        s3_client.upload_fileobj(
            io.BytesIO(img_data),
            s3_client.S3_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": "image/png"}
        )

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_client.S3_BUCKET_NAME, 'Key': filename},
        )

        print("done running folium tool")
        return {
            "type": "folium_chart",
            "content": {
                "s3_key": filename,
                "url": url  # Include this if you're using pre-signed URLs
            }
        }
    except Exception as e:
        return {"type": "error", "content": str(e)}

@tool
def plotly_tool(input: Annotated[LangGraphInput, "The input data and specifications to create a plotly graph"]):
    """Create various types of charts using Plotly based on the provided specifications."""
    try:
        s3_client = S3Client()
        docs = input.documents
        spec = input.chart_spec
        entity = input.entity

        df = pd.DataFrame([doc.model_dump() for doc in docs])

        if spec.chart_type == "scatter_map":
            fig = px.scatter_geo(df, 
                                 lat='latitude', 
                                 lon='longitude',
                                 color=spec.data_fields[0] if spec.data_fields else None,
                                 hover_name='title',
                                 title=spec.title)
        elif spec.chart_type == "bar_chart":
            fig = px.bar(df, 
                         x=spec.data_fields[0], 
                         y=spec.data_fields[1],
                         title=spec.title)
        elif spec.chart_type == "line_chart":
            fig = px.line(df, 
                          x=spec.data_fields[0], 
                          y=spec.data_fields[1],
                          title=spec.title)
        elif spec.chart_type == "heatmap":
            fig = px.density_heatmap(df, 
                                     x=spec.data_fields[0], 
                                     y=spec.data_fields[1],
                                     title=spec.title)
        elif spec.chart_type == "bubble_chart":
            fig = px.scatter(df, 
                             x=spec.data_fields[0], 
                             y=spec.data_fields[1],
                             size=spec.data_fields[2] if len(spec.data_fields) > 2 else None,
                             color=spec.data_fields[3] if len(spec.data_fields) > 3 else None,
                             hover_name='title',
                             title=spec.title)
        else:
            return {"type": "error", "content": f"Unsupported chart type for Plotly: {spec.chart_type}"}

        fig.update_layout(title=spec.title)
        # Save the figure as a PNG in memory
        img_buffer = io.BytesIO()
        fig.write_image(img_buffer, format='png')
        img_buffer.seek(0)

        # Generate a unique filename
        filename = f"{entity.id}.png"
        # Upload to S3
        s3_client.upload_fileobj(
            img_buffer,
            s3_client.S3_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": "image/png"}
        )

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_client.S3_BUCKET_NAME, 'Key': filename}
        )

        print("done running plotly tool")
        return {
            "type": "plotly_chart",
            "content": {
                "s3_key": filename,
                "url": url # Include this if you're using pre-signed URLs
            }
        }
    except Exception as e:
        return {"type": "error", "content": str(e)}
    
@tool
def dummy_tool(input: Annotated[str, "Any input string"]) -> str:
    """
    This is a dummy tool that doesn't perform any significant action.
    It's used to satisfy the API requirement for at least one tool.
    """
    return "Dummy tool was called."

def router(state):
    # This is the router
    messages = state["messages"]
    print("Sender: " + state['sender'])
    last_message = messages[-1]
    print("Last message: " + str(last_message))
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return "continue"

def agent_node(state, agent, name):
    print("Running agent node: " + name)
    # Prepare the input for the agent
    agent_input = {
        "messages": state.get("messages", []),
        "input": state.get("input")
    }
    result = agent.invoke(agent_input)
    # We convert the agent output into a format that is suitable to append to the global state

    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "input": state.get("input", None),
        "sender": name,
    }

chart_generation_template = """You are a chart generation expert. You will receive instructions for
    creating charts in a specific JSON format. Your task is to interpret these instructions
    and use the appropriate tool (folium or plotly) to generate the specified chart. You are also
    given a LangGraphInput object with fields of EntityNode and List[DocumentNode] as state. Pass
    this data onto the chart tools to create the appropriate charts.
    
    The input will be in the following format:
    "input": {
        "entity": EntityNode,
        "documents": List[DocumentNode],
    }

    You MUST use the specified library and chart type. Create a ChartSpec object from the input and call the appropriate tool.
    If you encounter any issues or need clarification, ask for help."""

chart_selection_template = """
    You will receive input data in the following structure:
    {
        "messages": [],
        "input": {
            "entity": EntityNode,
            "documents": List[DocumentNode],
        }
        "sender": str
    }

    Use the "input" field from the data to get the relevant information. From this, analyze the EntityNode and List[DocumentNode]
    to determine the best graph to display. Consider maps showing various events, bar graphs showing fatalities, and other relevant visualizations.
    Use the labels on the EntityNodes and the event_type and sub_event_type fields on DocumentNode
    to determine the best graphs to display. Consider maps showing various events, bar graphs showing fatalities,
    and other relevant visualizations.
    
    You MUST return your response in the following JSON format:
    {
        "chart_type": "<chart_type>",
        "library": "<library>",
        "data_fields": ["<field1>", "<field2>", ...],
        "title": "<chart_title>",
        "description": "<brief_description_of_why_this_chart_was_chosen>"
    }
    
    Where:
    - <chart_type> is one of: "scatter_map", "bar_chart", "line_chart", "heatmap", "bubble_chart"
    - <library> is either "folium" or "plotly"
    - <field1>, <field2>, etc. are the relevant fields from the EntityNodes to be used in the chart
    - <chart_title> is a descriptive title for the chart
    - <brief_description_of_why_this_chart_was_chosen> explains the reasoning behind this choice
    
    You can suggest at most 1 chart by returning a JSON object."""