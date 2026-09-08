"""
app.py
--------
Main entry point for the AI Learning & Study Assistant Streamlit app.

Run with:
    streamlit run app.py
"""

import streamlit as st

from config import config
from database.database import Database
from rag.retriever import Retriever
from memory.conversation_memory import ConversationMemory
from agent.study_agent import StudyAgent

from pages import (
    study_materials,
    planner,
    quiz,
    summarizer,
    flashcards,
    progress,
    history,
    about,
)

st.set_page_config(
    page_title="AI Learning & Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------
# Shared singletons (cached across reruns within a session)
# ------------------------------------------------------------------
@st.cache_resource
def get_database() -> Database:
    return Database()


@st.cache_resource
def get_retriever() -> Retriever:
    retriever = Retriever()
    retriever.ingest_knowledge_base()
    return retriever


def get_memory() -> ConversationMemory:
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationMemory()
    return st.session_state.memory


def get_agent() -> StudyAgent:
    db = get_database()
    retriever = get_retriever()
    memory = get_memory()
    if "agent" not in st.session_state:
        st.session_state.agent = StudyAgent(db=db, retriever=retriever, memory=memory)
    return st.session_state.agent


db = get_database()
retriever = get_retriever()
memory = get_memory()
agent = get_agent()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ------------------------------------------------------------------
# Sidebar navigation
# ------------------------------------------------------------------
st.sidebar.markdown(f"## {config.APP_TITLE}")
st.sidebar.caption(config.APP_SUBTITLE)

if config.DEMO_MODE:
    st.sidebar.warning("🟡 DEMO MODE — no LLM API key configured. Offline/demo logic is active.")
else:
    st.sidebar.success(f"🟢 LIVE MODE — connected to {config.LLM_PROVIDER.title()} ({config.LLM_MODEL})")

PAGES = {
    "🏠 Dashboard": "dashboard",
    "💬 AI Study Assistant": "chat",
    "📚 Study Materials": "materials",
    "📅 Study Planner": "planner",
    "📝 Quiz Generator": "quiz",
    "📄 Summarizer": "summarizer",
    "🧠 Flashcards": "flashcards",
    "📊 Progress": "progress",
    "📜 History": "history",
    "ℹ️ About": "about",
}

selected_label = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
selected_page = PAGES[selected_label]

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit · Sentence-Transformers · SQLite")


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
def render_dashboard():
    st.title(config.APP_TITLE)
    st.caption(config.APP_SUBTITLE)

    stats = db.get_dashboard_stats()
    weak_topics = db.get_weak_topics()
    strong_topics = db.get_strong_topics()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📚 Study Materials", stats["materials_count"])
    col2.metric("🧠 Topics Studied", stats["topics_studied"])
    col3.metric("📝 Quiz Score (avg)", f"{stats['average_score']}%")
    col4.metric("⏱️ Study Hours", stats["study_hours"])
    col5.metric("🎯 Quizzes Completed", stats["quizzes_completed"])
    col6.metric("⚠️ Weak Topics", len(weak_topics))

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("📌 Recommended for Today")
        if weak_topics:
            for wt in weak_topics[:5]:
                st.warning(f"Revise **{wt['topic']}** ({wt['subject']}) — avg score {wt['avg_score']:.1f}%")
        else:
            st.info("No weak topics detected yet. Take a quiz to get personalized recommendations!")

        st.subheader("🏆 Strongest Topics")
        if strong_topics:
            for st_topic in strong_topics[:5]:
                st.success(f"**{st_topic['topic']}** ({st_topic['subject']}) — avg score {st_topic['avg_score']:.1f}%")
        else:
            st.info("Complete some quizzes to see your strongest topics here.")

    with right:
        st.subheader("📅 Today's Study Tasks")
        tasks = db.get_study_tasks()
        pending = [t for t in tasks if t["status"] == "pending"][:6]
        completed_count = len([t for t in tasks if t["status"] == "completed"])

        if tasks:
            st.caption(f"{completed_count} completed / {len(tasks)} total tasks in your current plan")
            for t in pending:
                st.write(f"• Day {t['day_number']}: **{t['topic']}** ({t['subject']}) — {t['start_time']}–{t['end_time']}")
        else:
            st.info("No study plan yet. Create one on the '📅 Study Planner' page.")

    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("💬 Ask a Question"):
        st.session_state["_nav_hint"] = "chat"
        st.rerun()
    if qa2.button("📝 Generate a Quiz"):
        st.session_state["_nav_hint"] = "quiz"
        st.rerun()
    if qa3.button("📅 Create Study Plan"):
        st.session_state["_nav_hint"] = "planner"
        st.rerun()
    if qa4.button("🧠 Make Flashcards"):
        st.session_state["_nav_hint"] = "flashcards"
        st.rerun()


# ------------------------------------------------------------------
# AI Study Assistant chat page
# ------------------------------------------------------------------
def render_chat():
    st.title("💬 AI Study Assistant")
    st.caption("Ask anything about your subjects — I'll explain, quiz, plan, or summarize for you.")

    example_questions = [
        "Explain Operating System simply",
        "Give me 10 DBMS MCQs",
        "Summarize my uploaded notes",
        "Create a study plan",
        "What is normalization?",
    ]
    cols = st.columns(len(example_questions))
    clicked_example = None
    for col, question in zip(cols, example_questions):
        if col.button(question, key=f"ex_{question}"):
            clicked_example = question

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.caption("📚 Sources Used: " + ", ".join(msg["sources"]))

    user_input = st.chat_input("Type your study question here...")
    final_input = clicked_example or user_input

    if final_input:
        st.session_state.chat_messages.append({"role": "user", "content": final_input})
        with st.chat_message("user"):
            st.markdown(final_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = agent.chat(final_input)
            st.markdown(result["answer"])
            if result["sources"]:
                st.caption("📚 Sources Used: " + ", ".join(result["sources"]))

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })


# ------------------------------------------------------------------
# Router
# ------------------------------------------------------------------
nav_hint = st.session_state.pop("_nav_hint", None)
if nav_hint:
    selected_page = nav_hint

if selected_page == "dashboard":
    render_dashboard()
elif selected_page == "chat":
    render_chat()
elif selected_page == "materials":
    study_materials.render(db, retriever)
elif selected_page == "planner":
    planner.render(db, agent)
elif selected_page == "quiz":
    quiz.render(db, agent)
elif selected_page == "summarizer":
    summarizer.render(agent)
elif selected_page == "flashcards":
    flashcards.render(db, agent)
elif selected_page == "progress":
    progress.render(db, agent)
elif selected_page == "history":
    history.render(db)
elif selected_page == "about":
    about.render()
