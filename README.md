# 🎓 AI Learning & Study Assistant

**An Intelligent Personalized AI Learning and Study Assistant**

---

## 1. Project Title

AI Learning & Study Assistant — a Python + Streamlit application that helps students learn subjects,
understand study materials, generate quizzes and flashcards, build personalized study plans, summarize
notes, and track learning progress, powered by an AI Agent with RAG, Memory, and Tool Calling.

## 2. Abstract

Students today juggle multiple subjects, scattered notes, and limited time before exams. This project
builds a single, intelligent study companion that acts as an **AI Agent** — not just a chatbot — capable
of understanding a student's request, retrieving relevant context from uploaded study material using
**Retrieval-Augmented Generation (RAG)**, calling calculation **tools** when numbers are involved (like
exam countdowns or schedule generation), remembering the flow of conversation, and producing a
personalized, structured response. The system works fully even without any paid AI API key, via a
built-in **Demo Mode** that still uses real RAG search, real quiz logic, and a bundled offline knowledge
base — making it ideal for classroom demonstration.

## 3. Introduction

Traditional study help — tuition, generic search engines, or static PDFs — is not personalized and often
does not adapt to an individual student's pace, weak areas, or available time. This project addresses that
gap using freely available, open-source AI tooling: Sentence-Transformers for embeddings, a vector
database for retrieval, and a configurable LLM backend for generation, wrapped in an agentic
architecture and a friendly Streamlit interface.

## 4. Problem Statement

Students need a single tool that can: (a) answer academic questions in a simple, structured way,
(b) answer questions specifically from *their own* uploaded notes without hallucinating,
(c) build a realistic, prioritized study schedule before an exam, (d) generate practice quizzes and
track weak areas, and (e) do all of this reliably, even without constant internet/API access.

## 5. Objectives

- Build a working AI Agent that identifies intent and decides between RAG, tools, and direct generation.
- Implement a complete RAG pipeline: extraction → cleaning → chunking → embeddings → vector storage → retrieval.
- Implement conversational and learning-preference memory.
- Implement safe, predefined tool-calling for calculations (study hours, exam countdown, quiz scoring, schedule generation, topic progress).
- Track quiz performance and detect weak topics automatically.
- Provide a demo mode that works with zero configuration and never crashes.

## 6. Existing System

Most existing "AI study help" tools are either (a) generic chatbots with no access to a student's own
material and no memory of the conversation, or (b) static flashcard/quiz apps with no AI-generated,
personalized content, or (c) require constant paid API access with no offline fallback for demonstration.

## 7. Proposed System

The proposed system combines an AI Agent, a local RAG pipeline over the student's own uploaded material,
predefined calculation tools, session memory, and a SQLite-backed progress tracker — all wrapped in a
Streamlit UI, and fully configurable to run with **Anthropic Claude**, **OpenAI**, or entirely offline in
**Demo Mode**.

## 8. System Architecture

```
Student
   ↓
Streamlit UI
   ↓
AI Learning Agent (agent/study_agent.py)
   ↓
Intent Detection → RAG (rag/) → Memory (memory/) → Tools (tools/) → LLM (agent/llm_client.py)
   ↓
Personalized Response
   ↓
Progress Tracking → Database (database/database.py, SQLite)
```

## 9. Modules

| Module | Folder | Responsibility |
|---|---|---|
| Config | `config/` | Environment variables, constants, Demo Mode detection |
| Agent | `agent/` | Intent detection, orchestration, LLM client, demo fallback data |
| RAG | `rag/` | Document loading, cleaning, chunking, embeddings, vector store, retriever |
| Tools | `tools/` | Predefined calculation tools (study hours, exam countdown, quiz score, schedule, progress) |
| Memory | `memory/` | Conversation memory & learning preferences |
| Database | `database/` | SQLite schema and CRUD operations |
| Knowledge Base | `knowledge_base/` | Offline study notes (Python, DSA, DBMS, OS, Networks, ML) |
| Pages | `pages/` | Streamlit pages: materials, planner, quiz, summarizer, flashcards, progress, history, about |

## 10. Technologies Used

- **Language:** Python 3.11+
- **Frontend:** Streamlit
- **AI:** Configurable LLM (Anthropic Claude / OpenAI), with offline Demo Mode
- **RAG:** Sentence-Transformers, FAISS (with automatic NumPy fallback)
- **Database:** SQLite
- **Configuration:** python-dotenv
- **Data Processing:** pandas

## 11. Hardware Requirements

- Any modern laptop/desktop (Windows, macOS, or Linux)
- Minimum 8 GB RAM recommended (for local embedding model)
- ~2 GB free disk space (for Python packages + embedding model cache)

## 12. Software Requirements

- Python 3.11 or higher
- pip (Python package manager)
- Internet connection (only needed the first time, to download the embedding model and, optionally, to call a real LLM API)

## 13. Installation

```bash
cd AI_Learning_Study_Assistant
python -m venv venv
```

## 14. Virtual Environment Setup (Windows)

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 15. API Key Setup

1. Copy `.env.example` to `.env`
2. Open `.env` and set your key:
   ```
   LLM_API_KEY=your_real_api_key_here
   LLM_PROVIDER=anthropic
   LLM_MODEL=claude-3-5-sonnet-20241022
   ```
3. Save the file. The app will automatically detect the key on next launch.

**Never commit your `.env` file or share your API key.**

## 16. Demo Mode

If `LLM_API_KEY` is missing or left as the placeholder value, the app automatically shows a
**🟡 DEMO MODE** banner and switches to offline logic:
- RAG-based answers still work using the bundled knowledge base and real similarity search.
- Quizzes are generated from a curated demo question bank.
- Study plans, summaries, and flashcards use rule-based/template logic.
- The application never crashes due to a missing or invalid API key.

## 17. RAG Explanation

RAG (Retrieval-Augmented Generation) grounds AI answers in real documents instead of relying purely on
the model's memory. Pipeline: **Document → Text Extraction → Cleaning → Chunking → Embeddings
(Sentence-Transformers) → Vector Store (FAISS) → Similarity Search → Relevant Context → LLM → Answer.**
If no relevant context is found, the system explicitly says so instead of guessing.

## 18. AI Agent Explanation

`agent/study_agent.py` implements the `StudyAgent` class, which: detects intent (question, quiz request,
planning request, etc.), decides whether RAG or a tool is needed, retrieves context, calls tools safely,
uses memory to resolve references like "explain it more simply", generates a response (via LLM or Demo
Mode), and stores history — the defining behaviors of an **agent** versus a plain chatbot.

## 19. Memory Explanation

`memory/conversation_memory.py` keeps a rolling window of recent conversation turns and the last
discussed topic, so follow-up questions are understood in context, plus tracks session-level learning
preferences (explanation style, difficult topics, recently studied topics).

## 20. Tool Calling Explanation

`tools/study_tools.py` defines five pure, testable functions: `calculate_study_hours`,
`calculate_days_until_exam`, `calculate_quiz_score`, `generate_study_schedule`, and
`calculate_topic_progress`. The agent detects when a request contains the right signals (e.g. a date, an
hours figure) and calls the matching tool automatically.

## 21. Database

SQLite (`database/database.py`) with tables: `session`, `chat_history`, `study_materials`,
`quiz_results`, `study_progress`, `study_tasks`, `feedback`, and `flashcards`. No sensitive personal
information is stored.

## 22. How to Run

```bash
streamlit run app.py
```
Then open the URL shown in the terminal (typically `http://localhost:8501`).

## 23. Example Questions

- "Explain Operating System simply"
- "What is normalization in DBMS?"
- "Give me 10 DBMS MCQs"
- "My exam is in 10 days and I can study 4 hours a day"
- "Summarize my uploaded notes"
- "What is process scheduling?" (after uploading OS notes)

## 24. Testing

See `docs/TEST_CASES.md` for 15+ documented test cases covering normal use, edge cases, and error handling.

## 25. Advantages

- Works fully offline/without an API key (Demo Mode)
- Grounded, source-cited answers from the student's own material
- Personalized scheduling that prioritizes weak/difficult topics
- Modular, well-commented, beginner-friendly codebase suitable for a viva

## 26. Limitations

- Demo Mode question generation is less varied than a live LLM
- Local embedding model requires a one-time download (needs internet the first time)
- OCR for scanned/image-only PDFs is not implemented

## 27. Future Enhancements

- Voice-based Q&A
- Multi-user accounts with authentication
- Mobile app version
- Integration with calendar apps for study reminders
- Support for more document formats (PPTX, images with OCR)

## 28. Conclusion

This project demonstrates a complete, practical AI Agent system combining RAG, memory, and tool calling
to deliver a genuinely useful, personalized study assistant — while remaining fully explainable, modular,
and runnable in a classroom/viva setting with or without live AI API access.

---

## 📁 Project Structure

```
AI_Learning_Study_Assistant/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── config/
├── agent/
├── rag/
├── tools/
├── memory/
├── database/
├── knowledge_base/
├── data/
├── pages/
└── docs/            (report, viva questions, test cases, PPT content, demo procedure)
```

## 📚 Additional Documents

See the `docs/` folder for:
- `PROJECT_REPORT.md` — full college project report content
- `VIVA_QUESTIONS.md` — 20 viva questions with simple English & Tanglish answers
- `TEST_CASES.md` — 15 documented test cases
- `PPT_CONTENT.md` — 10-slide presentation content
- `DEMO_PROCEDURE.md` — step-by-step live demo script
