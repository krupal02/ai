# 🛫 AeroGuide: AI Airport Companion - Project Context

This document serves as the full architectural and operational context for AeroGuide, intended to bring any new AI assistant or developer up to speed instantly.

## 🌟 Project Overview
AeroGuide is a **privacy-first, local-AI driven airport assistant** designed to personalize the traveler experience. It moves away from generic airport apps by providing context-aware guidance based on user profiles (travel frequency, age, diet, accessibility needs).

## 🛠️ Tech Stack
- **Frontend:** React (Vite) + Vanilla CSS (Glassmorphism design).
- **Backend:** FastAPI (Python 3.14).
- **AI Engine:** 
  - **LLM:** Qwen 2.5 (0.5B) running locally via **Ollama**.
  - **RAG:** Custom Python Keyword Matching algorithm (bypasses heavy vector DBs for stability).
  - **TTS:** Windows Native SAPI5 (Microsoft Speech API).
  - **STT:** Google Web Speech API (configured for `hi-IN` to support Hinglish).
- **Database:** SQLite (for persistent user profiles).

## 🏗️ Core Architecture & Business Logic

### 1. Dynamic Personalization (`Backend/Chatbot.py`)
The system doesn't just pass queries to the AI. It builds a **Dynamic System Prompt** based on:
- **Travel Frequency:** Changes the complexity of instructions (First-time vs. Frequent).
- **Dietary Preferences:** Filters restaurant recommendations (Veg, Jain, Vegan).
- **Accessibility:** Prioritizes routes for wheelchair users or seniors.

### 2. Stability-Optimized RAG (`Backend/RAGService.py`)
Due to C-level memory access violations in `ChromaDB` on Windows/Python 3.14, we replaced the heavy vector DB with a **Pure Python Keyword Scorer**.
- **Data Source:** Real OpenStreetMap (OSM) coordinates mapped into `airport_knowledge.json`.
- **Logic:** Scores document relevance based on query word intersection and exact substring matching.

### 3. Integrated Components
- **Onboarding Modal:** Captures PNR and user preferences, storing them in `aeroguide.db`.
- **Food Finder:** Interactive React panel with live dietary filtering.
- **Security Dashboard:** Tabbed interface for prohibited items and protocol tips.

## 🚀 Setup & Execution (New Environment)
1. **Ollama:** 
   - Download from [ollama.com](https://ollama.com).
   - Run: `ollama pull qwen2.5:0.5b`.
2. **Python Environment:**
   - Install dependencies: `pip install fastapi uvicorn requests python-multipart pywin32 SpeechRecognition`.
3. **Run Backend:**
   - Command: `python main.py`.
   - *Note: If Hub errors occur, use `$env:HF_HUB_OFFLINE=1; python main.py`.*
4. **Run Frontend:**
   - Command: `npm install` then `npm run dev`.

## ⚠️ Critical Bug Fix History
- **Access Violation Fix:** We removed `langchain-chroma` and `sentence-transformers` because they caused "NotImplementedError" and "Access Violation" crashes on Windows. **Do not re-add them.**
- **Threadpool Deadlock:** The `chat_endpoint` was changed back to `async def` to prevent OpenMP deadlocks in the FastAPI threadpool during local inference.
- **TTS Blocking:** TTS is implemented using `threading.Thread` to prevent the SAPI voice from blocking the FastAPI response.

## 📈 Current Status
The project is a **Production-Ready MVP**. All core features (Chat, Personalization, RAG, Food, Security) are 100% functional and tested. It is currently optimized for a local demonstration to evaluators.

---
*Created for the Hackathon Finalization Stage.*
