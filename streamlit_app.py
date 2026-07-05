import logging

import streamlit as st

from backend import run_travel_agent

logger = logging.getLogger(__name__)

QUICK_PROMPTS = {
    "Japan Trip": "Plan a complete 7 days Japan trip from Delhi including flights, hotels and sightseeing under 2 lakhs.",
    "Dubai Trip": "Plan a 5 days Dubai trip from Delhi with flights, hotels and sightseeing.",
    "Thailand Trip": "Plan a 7 days Thailand trip from India with budget hotels and sightseeing.",
    "Global Flights": "Give me all country flight info.",
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --trip-bg: #07111f;
            --trip-panel: rgba(15, 23, 42, 0.78);
            --trip-border: rgba(148, 163, 184, 0.28);
            --trip-text: #f8fafc;
            --trip-muted: #94a3b8;
            --trip-blue: #2563eb;
            --trip-teal: #14b8a6;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(37, 99, 235, 0.34), transparent 30%),
                radial-gradient(circle at 88% 16%, rgba(20, 184, 166, 0.24), transparent 28%),
                linear-gradient(135deg, #07111f 0%, #0f172a 48%, #111827 100%);
            color: var(--trip-text);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 3rem;
            padding-bottom: 2rem;
        }

        .trip-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.55rem 1rem;
            border: 1px solid var(--trip-border);
            border-radius: 999px;
            background: rgba(15, 23, 42, 0.72);
            color: #bfdbfe;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .trip-hero h1 {
            margin: 0 0 0.8rem;
            font-size: clamp(2.35rem, 7vw, 4.8rem);
            line-height: 0.95;
            color: #ffffff;
        }

        .trip-hero p {
            color: #cbd5e1;
            font-size: 1.08rem;
            line-height: 1.7;
            max-width: 780px;
        }

        .trip-panel {
            border: 1px solid var(--trip-border);
            background: var(--trip-panel);
            border-radius: 24px;
            padding: 1.35rem;
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            margin-top: 1.25rem;
        }

        .trip-panel h2 {
            color: #ffffff;
            margin: 0;
            font-size: 1.35rem;
        }

        .trip-subtle {
            color: var(--trip-muted);
            line-height: 1.5;
        }

        .stTextArea textarea {
            min-height: 150px;
            border-radius: 18px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: rgba(2, 6, 23, 0.72);
            color: #ffffff;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            font-weight: 800;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--trip-blue), var(--trip-teal));
            border: none;
        }

        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3 {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session() -> None:
    st.session_state.setdefault("thread_id", None)
    st.session_state.setdefault("travel_request", "")
    st.session_state.setdefault("latest_answer", "")


def set_prompt(prompt: str) -> None:
    st.session_state.travel_request = prompt


def render_header() -> None:
    st.markdown(
        """
        <section class="trip-hero">
            <div class="trip-badge">TripPilot AI - Multi-Agent Travel Planner</div>
            <h1>Plan Your Perfect Trip with AI</h1>
            <p>
                Search flights, discover hotels, and generate a complete travel itinerary
                using your LangGraph multi-agent backend.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_prompt_buttons() -> None:
    cols = st.columns(len(QUICK_PROMPTS))

    for col, (label, prompt) in zip(cols, QUICK_PROMPTS.items()):
        with col:
            st.button(label, on_click=set_prompt, args=(prompt,), use_container_width=True)


def generate_plan(message: str) -> None:
    with st.spinner("TripPilot agents are planning your trip..."):
        result = run_travel_agent(
            user_input=message,
            thread_id=st.session_state.thread_id,
        )

    st.session_state.thread_id = result["thread_id"]
    st.session_state.latest_answer = result["answer"]
    st.session_state.flight_results = result.get("flight_results", "")
    st.session_state.hotel_results = result.get("hotel_results", "")
    st.session_state.itinerary = result.get("itinerary", "")
    st.session_state.llm_calls = result.get("llm_calls", 0)


def render_result() -> None:
    if not st.session_state.latest_answer:
        return

    st.markdown('<section class="trip-panel">', unsafe_allow_html=True)
    st.subheader("Your AI Travel Plan")
    st.caption(f"Thread ID: {st.session_state.thread_id}")
    st.markdown(st.session_state.latest_answer)

    st.download_button(
        "Download Markdown",
        data=st.session_state.latest_answer,
        file_name="trip-pilot-plan.md",
        mime="text/markdown",
        use_container_width=True,
    )

    with st.expander("Agent Details"):
        st.metric("LLM Calls", st.session_state.get("llm_calls", 0))
        st.markdown("**Flight Results**")
        st.text(st.session_state.get("flight_results", "") or "No flight data.")
        st.markdown("**Hotel Results**")
        st.text(st.session_state.get("hotel_results", "") or "No hotel data.")
        st.markdown("**Draft Itinerary**")
        st.text(st.session_state.get("itinerary", "") or "No itinerary draft.")

    st.markdown("</section>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="TripPilot AI",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    initialize_session()
    apply_theme()
    render_header()

    st.markdown('<section class="trip-panel">', unsafe_allow_html=True)
    st.subheader("Where do you want to go?")
    st.caption("Example: Plan a complete 7 days Japan trip from Delhi under 2 lakhs.")

    message = st.text_area(
        "Travel request",
        key="travel_request",
        label_visibility="collapsed",
        placeholder="Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2 lakhs...",
    )

    render_prompt_buttons()

    generate_clicked = st.button(
        "Generate Plan",
        type="primary",
        use_container_width=True,
    )
    st.markdown("</section>", unsafe_allow_html=True)

    if generate_clicked:
        cleaned_message = message.strip()

        if not cleaned_message:
            st.error("Please enter your travel request first.")
        else:
            try:
                generate_plan(cleaned_message)
                st.success("Travel plan generated.")
            except Exception:
                logger.exception("Streamlit travel planner request failed.")
                st.error("Travel planner failed. Please check your API keys and try again.")

    render_result()

    st.caption("Built with Streamlit, LangGraph, Groq, PostgreSQL, Tavily and AviationStack")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
