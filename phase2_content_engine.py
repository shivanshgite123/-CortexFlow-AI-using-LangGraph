from typing import TypedDict
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from config import llm, BOT_PERSONAS



# 1. Mock Tool

@tool
def mock_searxng_search(query: str) -> str:
    """Return mock news based on keywords"""
    
    q = query.lower()

    if "crypto" in q:
        return "Bitcoin hits new all-time high amid regulatory ETF approvals."
    elif "ai" in q:
        return "OpenAI releases new model surpassing human reasoning."
    elif "ev" in q:
        return "Tesla reports record EV sales but faces battery issues."

    return "Global markets remain unstable due to inflation concerns."



# 2. Output Schema (STRICT JSON)

class FinalPost(BaseModel):
    bot_id: str
    topic: str
    post_content: str



# 3. Graph State

class State(TypedDict):
    bot_id: str
    persona: str
    query: str
    results: str
    output: dict



# Node 1: Decide Search

def decide_search(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        """You are:
{persona}

Decide ONE topic to post about today.
Return only a short search query."""
    )

    chain = prompt | llm
    res = chain.invoke({"persona": state["persona"]})

    state["query"] = res.content.strip()
    return state



# Node 2: Web Search

def web_search(state: State) -> State:
    result = mock_searxng_search.invoke(state["query"])

    state["results"] = result
    return state

# Node 3: Draft Post

def draft_post(state: State) -> State:
    structured_llm = llm.with_structured_output(FinalPost)

    prompt = ChatPromptTemplate.from_template(
        """You are:
{persona}

Context:
{results}

Write a strong, opinionated post (max 280 characters).

Return JSON in this format:
{{
  "bot_id": "{bot_id}",
  "topic": "<topic>",
  "post_content": "<post>"
}}
"""
    )

    chain = prompt | structured_llm

    response = chain.invoke({
        "persona": state["persona"],
        "results": state["results"],
        "bot_id": state["bot_id"]
    })

    state["output"] = response.model_dump()
    return state



# Build Graph

def build_engine():
    graph = StateGraph(State)

    graph.add_node("decide", decide_search)
    graph.add_node("search", web_search)
    graph.add_node("write", draft_post)

    graph.add_edge(START, "decide")
    graph.add_edge("decide", "search")
    graph.add_edge("search", "write")
    graph.add_edge("write", END)

    return graph.compile()



# Run Function

def run_phase2(bot_id: str):
    state = {
        "bot_id": bot_id,
        "persona": BOT_PERSONAS[bot_id]["persona"],
        "query": "",
        "results": "",
        "output": {}
    }

    engine = build_engine()
    result = engine.invoke(state)

    return result["output"]