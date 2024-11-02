from langchain_core.messages import HumanMessage
from util import AgentState, router, create_agent, agent_node, python_repl, neo4j_tool
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from db import LangGraphInput, GraphState
import functools

class LangGraph():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o")

        # chart_generator
        neo4j_agent = create_agent(
            self.llm,
            [neo4j_tool],
            system_message="Query the database and provide accurate data for the chart_generator to use.",
        )

        self.research_node = functools.partial(agent_node, agent=neo4j_agent, name="Researcher")

        # chart_generator
        chart_agent = create_agent(
            self.llm,
            [python_repl],
            system_message="Any charts you display will be visible by the user.",
        )
        self.chart_node = functools.partial(agent_node, agent=chart_agent, name="chart_generator")
        self.graph = self.create_graph()
        tools = [neo4j_agent, python_repl]
        self.tool_node = ToolNode(tools)

    def create_graph(self):

        
        # Research agent and node
        

        workflow = StateGraph(AgentState)
        

        workflow.add_node("Researcher", self.research_node)
        workflow.add_node("chart_generator", self.chart_node)
        workflow.add_node("call_tool", self.tool_node)

        workflow.add_conditional_edges(
            "Researcher",
            router,
            {"continue": "chart_generator", "call_tool": "call_tool", END: END},
        )
        workflow.add_conditional_edges(
            "chart_generator",
            router,
            {"continue": "Researcher", "call_tool": "call_tool", END: END},
        )

        workflow.add_conditional_edges(
            "call_tool",
            # Each agent node updates the 'sender' field
            # the tool calling node does not, meaning
            # this edge will route back to the original agent
            # who invoked the tool
            lambda x: x["sender"],
            {
                "Researcher": "Researcher",
                "chart_generator": "chart_generator",
            },
        )
        workflow.add_edge(START, "Researcher")
        graph = workflow.compile()
        return graph

    def run_graph(self, input_data: LangGraphInput):
        initial_state = GraphState(input=input_data)

        events = self.graph.stream(
            initial_state.model_dump(),
            {"recursion_limit": 150},
        )

        for s in events:
            print(s)
            print("----")
