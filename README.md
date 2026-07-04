# TripPilot-AI

TripPilot-AI is a FastAPI and LangGraph multi-agent travel planner. It combines:

- Flight status lookup through AviationStack
- Hotel and web research through Tavily
- Itinerary and final response generation through Groq-hosted LLMs
- Optional LangGraph checkpoint persistence through PostgreSQL

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create your local `.env` from `.env.example` and fill in your keys:

```text
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DEFAULT_ORIGIN_IATA=DEL
```

`DATABASE_URL` is optional for local development. If it is missing, TripPilot uses in-memory LangGraph checkpoints. For production, configure PostgreSQL so conversations survive process restarts.

## Run

FastAPI UI:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

Streamlit UI:

```powershell
streamlit run streamlit_app.py
```

Health check:

```text
GET /health
```

Travel planner API:

```text
POST /api/travel
```

Example body:

```json
{
  "message": "Plan a 5 day Japan trip from Delhi",
  "thread_id": "optional-user-thread-id"
}
```
