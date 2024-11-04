from util import router, create_agent, agent_node, folium_tool, plotly_tool
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from db import LangGraphInput, GraphState
import functools

class LangGraph():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")

        select_chart_agent = create_agent(
            self.llm,
            [],
            system_message="""Given a List[EntityNode], use the labels on the EntityNodes and the event_type and sub_event_type to determine what the
              best graphs would be to display. For instance, consider maps showing various events and bar graphs showing fatalities, but be creative.
              Return the output as a string""",
        )
        self.selector_node = functools.partial(agent_node, agent=select_chart_agent, name="chart_selector")

        # chart_generator
        chart_agent = create_agent(
            self.llm,
            [plotly_tool, folium_tool],
            system_message="Any charts you display will be visible by the user.",
        )
        self.generator_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")
        self.graph = self.create_graph()
        tools = [plotly_tool, folium_tool]
        self.tool_node = ToolNode(tools)

    def create_graph(self):
        workflow = StateGraph(GraphState)
        
        workflow.add_node("chart_selector", self.selector_node)
        workflow.add_node("chart_generator", self.generator_node)
        workflow.add_node("call_tool", self.tool_node)

        workflow.add_conditional_edges(
            "chart_selector",
            router,
            {"continue": "chart_generator", "call_tool": "call_tool", END: END},
        )
        workflow.add_conditional_edges(
            "chart_generator",
            router,
            {"continue": "chart_selector", "call_tool": "call_tool", END: END},
        )

        workflow.add_conditional_edges(
            "call_tool",
            # Each agent node updates the 'sender' field
            # the tool calling node does not, meaning
            # this edge will route back to the original agent
            # who invoked the tool
            lambda x: x["sender"],
            {
                "chart_selector": "chart_selector",
                "chart_generator": "chart_generator",
            },
        )
        workflow.add_edge(START, "chart_selector")
        graph = workflow.compile()
        return graph

    def stream_events(self, input_data: LangGraphInput):
        initial_state = GraphState(
            input=input_data,
            messages = [],
            sender = ""
        )

        events = self.graph.stream(
            initial_state.model_dump(),
            {"recursion_limit": 150},
        )

        return events
