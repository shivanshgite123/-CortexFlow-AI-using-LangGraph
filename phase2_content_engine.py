from typing import TypedDict
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from config import llm
import json



# Mock Search Tool


@tool
def mock_searxng_search(query: str):

    query = query.lower()

    if "crypto" in query:
        return "Bitcoin hits new all-time high amid ETF approvals"

    elif "ai" in query:
        return "AI replaces junior developers in multiple startups"

    elif "market" in query:
        return "Federal Reserve may reduce interest rates next quarter"

    return "No major news found"


# LangGraph State


class GraphState(TypedDict):
    bot_id: str
    persona: str
    topic: str
    search_results: str
    post_content: str



# Node 1: Decide Search


def decide_search(state: GraphState):

    prompt = f"""
    You are this persona:

    {state['persona']}

    Decide a trending topic to post about.
    Return only a short search query.
    """

    response = llm.invoke(prompt)

    return {
        "topic": response.content
    }



# Node 2: Web Search


def web_search(state: GraphState):

    result = mock_searxng_search.invoke(state["topic"])

    return {
        "search_results": result
    }



# Node 3: Draft Post


def draft_post(state: GraphState):

    prompt = f"""
    Persona:
    {state['persona']}

    Topic:
    {state['topic']}

    Search Results:
    {state['search_results']}

    Generate a highly opinionated 280-character social media post.

    Return JSON only.
    """

    response = llm.invoke(prompt)

    return {
        "post_content": response.content
    }



# Build Graph


workflow = StateGraph(GraphState)

workflow.add_node("decide_search", decide_search)
workflow.add_node("web_search", web_search)
workflow.add_node("draft_post", draft_post)

workflow.set_entry_point("decide_search")

workflow.add_edge("decide_search", "web_search")
workflow.add_edge("web_search", "draft_post")
workflow.add_edge("draft_post", END)

app = workflow.compile()



# Run Example


if __name__ == "__main__":

    initial_state = {
        "bot_id": "bot_a",
        "persona": "I believe AI and crypto will solve all human problems.",
        "topic": "",
        "search_results": "",
        "post_content": ""
    }

    result = app.invoke(initial_state)

    final_output = {
        "bot_id": result["bot_id"],
        "topic": result["topic"],
        "post_content": result["post_content"]
    }

    print(json.dumps(final_output, indent=2))