from .util import router, create_agent, agent_node, folium_tool, plotly_tool, dummy_tool, chart_generation_template, chart_selection_template
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from db import LangGraphInput, GraphState
from config import settings
import functools

class LangGraph():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=settings.OPENAI_API_KEY)

        select_chart_agent = create_agent(
            self.llm,
            [dummy_tool],
            system_message=chart_selection_template,
            include_input=True
        )
        self.selector_node = functools.partial(agent_node, agent=select_chart_agent, name="chart_selector")

        # chart_generator
        chart_agent = create_agent(
            self.llm,
            [plotly_tool, folium_tool],
            system_message=chart_generation_template,
        )
        self.generator_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")
        tools = [plotly_tool, folium_tool, dummy_tool]
        self.tool_node = ToolNode(tools)
        self.graph = self.create_graph()

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
            initial_state,
            {"recursion_limit": 10},
        )

        return events
