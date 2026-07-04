from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable

from agents.state import TravelState
from config import get_llm


@traceable(name="Itinerary Agent", run_type="chain")
def itinerary_agent(state: TravelState):
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = get_llm().invoke(
        [
            SystemMessage(content="You are an expert travel planner."),
            HumanMessage(content=prompt),
        ],
        config={
            "run_name": "Generate Draft Itinerary",
            "tags": ["trip-pilot", "itinerary-agent"],
        },
    )

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
