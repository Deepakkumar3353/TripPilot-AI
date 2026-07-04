import os

from dotenv import load_dotenv
from langsmith import traceable
from tavily import TavilyClient

load_dotenv()


def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return None

    return TavilyClient(api_key=api_key)


@traceable(name="Tavily Web Search", run_type="tool")
def tavily_search(query):
    """
    Search the web with Tavily and return a short, readable results summary.

    Args:
        query: The search phrase to send to Tavily.

    Returns:
        A formatted string containing up to five search results, each with a
        title, URL, and trimmed content snippet.
    """
    client = get_tavily_client()

    if client is None:
        return (
            "Tavily search unavailable: TAVILY_API_KEY is missing. "
            "Add it to your environment or .env file."
        )

    try:
        response = client.search(
            query=query,
            max_results=5
        )
    except Exception as e:
        return f"Tavily search failed: {e}"

    result = []

    for i, r in enumerate(response.get("results", []), 1):
        title = r.get("title", "Unknown")
        url = r.get("url", "")
        snippet = r.get("content", "").strip()

        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."
        
        result.append(f"{i}. **{title}**\n  {url}\n  {snippet}")

    if not result:
        return "No Tavily search results found."

    return "\n\n".join(result)
