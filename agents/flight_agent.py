from langchain_core.messages import AIMessage
from langsmith import traceable

from agents.state import TravelState
from tools.flight_tool import search_flights


@traceable(name="Flight Agent", run_type="chain")
def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0),
    }
