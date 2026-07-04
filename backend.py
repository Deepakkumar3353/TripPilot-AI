import logging
import uuid
from functools import lru_cache

import psycopg
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from psycopg.rows import dict_row

from agents import TravelState, final_agent, flight_agent, hotel_agent, itinerary_agent
from config import get_settings

logger = logging.getLogger(__name__)


def _database_url_with_ssl(database_url: str) -> str:
    if "sslmode=" in database_url:
        return database_url

    separator = "&" if "?" in database_url else "?"
    return f"{database_url}{separator}sslmode=require"




def build_graph() -> StateGraph:
    graph = StateGraph(TravelState)

    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("final_agent", final_agent)

    graph.add_edge(START, "flight_agent")
    graph.add_edge("flight_agent", "hotel_agent")
    graph.add_edge("hotel_agent", "itinerary_agent")
    graph.add_edge("itinerary_agent", "final_agent")
    graph.add_edge("final_agent", END)

    return graph


@lru_cache(maxsize=1)
def get_checkpointer():
    settings = get_settings()

    if not settings.database_url:
        logger.warning("DATABASE_URL is not configured. Using in-memory LangGraph checkpoints.")
        return MemorySaver()

    database_url = _database_url_with_ssl(settings.database_url)
    conn = psycopg.connect(
        database_url,
        autocommit=True,
        row_factory=dict_row,
    )

    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return checkpointer


@lru_cache(maxsize=1)
def get_travel_graph():
    return build_graph().compile(checkpointer=get_checkpointer())



# =========================
# Function for FastAPI
# =========================

def run_travel_agent(user_input: str, thread_id: str | None = None):
    user_input = user_input.strip()

    if not user_input:
        raise ValueError("User input cannot be empty.")

    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = get_travel_graph().invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }
