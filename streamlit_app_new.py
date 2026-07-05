
# app.py
import logging
import streamlit as st
from backend import run_travel_agent

logger = logging.getLogger(__name__)

QUICK_PROMPTS = {
    "🇯🇵 Japan": "Plan a complete 7 days Japan trip from Delhi including flights, hotels and sightseeing under 2 lakhs.",
    "🇦🇪 Dubai": "Plan a 5 days Dubai trip from Delhi with flights, hotels and sightseeing.",
    "🇹🇭 Thailand": "Plan a 7 days Thailand trip from India with budget hotels and sightseeing.",
    "🌍 Flights": "Give me all country flight info.",
}

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html,body,[class*="css"]{font-family:Inter,sans-serif;}
    .stApp{
      background:radial-gradient(circle at top right,#dcfce7,transparent 30%),
                 radial-gradient(circle at bottom left,#bbf7d0,transparent 25%),#f7fcf8;}
    .block-container{max-width:1150px;padding-top:2rem;padding-bottom:2rem;}
    .hero{padding:1rem 0 2rem;}
    .badge{display:inline-block;background:#ecfdf5;border:1px solid #bbf7d0;color:#047857;
      padding:.55rem 1rem;border-radius:999px;font-weight:700;}
    .hero h1{font-size:3.6rem;line-height:1.05;color:#111827;margin:.8rem 0;}
    .hero p{font-size:1.1rem;color:#4b5563;max-width:720px;}
    .card{background:#fff;border:1px solid #e5e7eb;border-radius:24px;padding:1.5rem;
      box-shadow:0 8px 30px rgba(0,0,0,.06);margin-top:1.2rem;}
    footer,#MainMenu{visibility:hidden;}
    </style>
    """, unsafe_allow_html=True)

def init():
    for k,v in {"thread_id":None,"travel_request":"","latest_answer":"","flight_results":"","hotel_results":"","itinerary":"","llm_calls":0}.items():
        st.session_state.setdefault(k,v)

def set_prompt(p): st.session_state.travel_request=p

def header():
    st.markdown("""
    <div class="hero">
      <div class="badge">✈️ TripPilot AI</div>
      <h1>Plan Your Dream Trip<br>with AI</h1>
      <p>Search flights, hotels and attractions and receive a personalized itinerary powered by your LangGraph multi-agent backend.</p>
    </div>""",unsafe_allow_html=True)

def quick():
    cols=st.columns(4)
    for c,(l,p) in zip(cols,QUICK_PROMPTS.items()):
        with c: st.button(l,use_container_width=True,on_click=set_prompt,args=(p,))

def generate(msg):
    with st.spinner("Planning your trip..."):
        r=run_travel_agent(msg,thread_id=st.session_state.thread_id)
    for k in ["thread_id","answer","flight_results","hotel_results","itinerary","llm_calls"]:
        if k=="answer":
            st.session_state.latest_answer=r.get("answer","")
        else:
            st.session_state[k]=r.get(k)

def result():
    if not st.session_state.latest_answer: return
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.subheader("🧳 Your Personalized Travel Plan")
    st.caption(f"Session • {st.session_state.thread_id}")
    st.markdown(st.session_state.latest_answer)
    st.download_button("📄 Download Markdown",st.session_state.latest_answer,"trip-plan.md","text/markdown",use_container_width=True)
    with st.expander("🔍 Agent Details"):
        st.metric("LLM Calls",st.session_state.llm_calls)
        st.markdown("### ✈ Flights"); st.text(st.session_state.flight_results or "No data")
        st.markdown("### 🏨 Hotels"); st.text(st.session_state.hotel_results or "No data")
        st.markdown("### 🗓 Draft Itinerary"); st.text(st.session_state.itinerary or "No data")
    st.markdown("</div>",unsafe_allow_html=True)

def main():
    st.set_page_config("TripPilot AI","✈️",layout="wide",initial_sidebar_state="collapsed")
    init(); apply_theme(); header()
    st.markdown('<div class="card">',unsafe_allow_html=True)
    st.subheader("🌍 Where do you want to go?")
    msg=st.text_area("Travel Request",key="travel_request",label_visibility="collapsed",
                     placeholder="Plan a 7-day Japan trip from Delhi under ₹2 lakh...")
    quick()
    if st.button("🚀 Generate Travel Plan",type="primary",use_container_width=True):
        if msg.strip():
            try:
                generate(msg.strip()); st.success("Travel plan generated.")
            except Exception:
                logger.exception("failed"); st.error("Travel planner failed.")
        else:
            st.error("Enter a travel request.")
    st.markdown("</div>",unsafe_allow_html=True)
    result()
    st.caption("Built with Streamlit • LangGraph • Groq • PostgreSQL • Tavily • AviationStack")

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO)
    main()
