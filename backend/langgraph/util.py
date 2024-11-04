from langchain_core.messages import ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langgraph.graph import END
from typing import Annotated, List
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import io
import base64
from db import LangGraphInput, DocumentNode
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)

@tool
def folium_tool(input: LangGraphInput):
    try:
        docs: List[DocumentNode] = input.documents

        lats = [doc.latitude for doc in docs if doc.latitude is not None]
        lons = [doc.longitude for doc in docs if doc.longitude is not None]

        if not lats or not lons:
            return "Error: No valid coordinates found in the documents."

        center = [sum(lats) / len(lats), sum(lons) / len(lons)]
            
        m = folium.Map(location=center, zoom_start=4)

        marker_cluster = MarkerCluster().add_to(m)

        for doc in docs:
            if doc.latitude is not None and doc.longitude is not None:
                # Create popup content
                popup_content = f"""
                <b>{doc.title}</b><br>
                Location: {doc.location}<br>
                Country: {doc.country}<br>
                Event Type: {doc.event_type}<br>
                Sub-event Type: {doc.sub_event_type}<br>
                Fatalities: {doc.fatalities}<br>
                Actor 1: {doc.actor1}<br>
                Actor 2: {doc.actor2}<br>
                Timestamp: {doc.timestamp}
                """

                # Create marker
                folium.Marker(
                    location=[doc.latitude, doc.longitude],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{doc.event_type} in {doc.location}"
                ).add_to(marker_cluster)

        # Add a choropleth layer for fatalities by country
        country_fatalities = {}
        for doc in docs:
            if doc.country in country_fatalities:
                country_fatalities[doc.country] += doc.fatalities
            else:
                country_fatalities[doc.country] = doc.fatalities

        folium.Choropleth(
            geo_data='countries.geo.json',  # You need to provide a GeoJSON file for world countries
            name='Fatalities by Country',
            data=country_fatalities,
            columns=['Country', 'Fatalities'],
            key_on='feature.properties.name',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Fatalities'
        ).add_to(m)

        # Save the map
        img_data = io.BytesIO()
        m.save(img_data, close_file=False)
        img_data.seek(0)
        return {
            "type": "folium_map",
            "content": base64.b64encode(img_data.getvalue()).decode('utf-8')
        }
    except Exception as e:
        return {"type": "error", "content": str(e)}
    
@tool
def plotly_tool(input: LangGraphInput) -> str:
    try:
        docs: List[DocumentNode] = input.documents

        # Create a DataFrame from the documents
        df = pd.DataFrame([doc.model_dump() for doc in docs])

        # Create a scatter plot
        fig = px.scatter(df, 
                         x='longitude', 
                         y='latitude', 
                         color='event_type',
                         size='fatalities',
                         hover_name='title',
                         hover_data=['country', 'location', 'timestamp'],
                         title='Event Distribution and Fatalities',
                         labels={'longitude': 'Longitude', 
                                 'latitude': 'Latitude', 
                                 'event_type': 'Event Type',
                                 'fatalities': 'Fatalities'},
                         size_max=50)  # Adjust the maximum bubble size

        # Update layout for better readability
        fig.update_layout(
            legend_title_text='Event Type',
            xaxis_title='Longitude',
            yaxis_title='Latitude'
        )

        # Save the plot as an HTML file
        img_data = io.BytesIO()
        fig.save(img_data, close_file=False)
        img_data.seek(0)
        return {
            "type": "plotly_map",
            "content": base64.b64encode(img_data.getvalue()).decode('utf-8')
        }
    except Exception as e:
        return {"type": "error", "content": str(e)}

def router(state):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return "continue"

def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }