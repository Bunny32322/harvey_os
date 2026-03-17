# ⚖️ HARVEY OS – Hybrid Strategic AI Command Center

A private, modular AI strategist inspired by Harvey Specter. Not a chatbot — a structured decision-analysis and life-strategy system.

## Features

| Module | What it does |
|---|---|
| **Strategic Engine** | Full situation analysis with vector memory + leverage scoring |
| **Hybrid Brain** | Seamlessly switch between local LLM (LM Studio) and OpenAI |
| **Personality Modes** | Strategic / Aggressive / Diplomatic / Long-Term prompting |
| **Vector Memory** | FAISS-powered semantic memory for strategic context |
| **Leverage Scorer** | Composite lifestyle score (learning, deep work, health, etc.) |
| **Psychology Analyzer** | Detects cognitive patterns from daily reflections |
| **Decision Tracker** | Log, score, and learn from your strategic decisions |
| **Decision Learning** | Self-improving strategy analysis from historical data |
| **Scenario Simulator** | Aggressive / balanced / passive strategy generation |
| **Board of Directors** | 5 AI personas analyze a situation, then synthesize |
| **Trajectory Forecast** | 1 / 3 / 5-year best & worst case predictions |
| **Report Engine** | Weekly/monthly performance reports (markdown + PDF) |
| **Conversation Training** | Extract insights from past conversations into memory |
| **Voice Interface** | Optional speech input/output via SpeechRecognition + pyttsx3 |
| **FastAPI Backend** | REST API for mobile apps and external integrations |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Set up LM Studio for offline mode

1. Download and install [LM Studio](https://lmstudio.ai/).
2. Load a model (e.g. Mistral, Llama 3, Phi-3).
3. Start the local server — it runs at `http://localhost:1234` by default.

### 3. (Optional) Configure OpenAI for online mode

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Run the Streamlit dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

### 5. Run the FastAPI backend (for mobile/API access)

```bash
uvicorn api.server:app --reload
```

API docs at `http://localhost:8000/docs`.

---

## Switching Modes

Use the **sidebar radio button** inside the app to toggle between:

- **Offline** → Uses LM Studio's local OpenAI-compatible API
- **Online** → Uses the OpenAI API (requires `OPENAI_API_KEY`)

You can also set the default mode via environment variable:

```
HARVEY_MODE=online
```

---

## Personality Modes

Control the AI's strategic style via the sidebar:

| Mode | Behaviour |
|------|-----------|
| **Strategic** | Balanced long-game analysis, calculated risk |
| **Aggressive** | Bold, decisive, maximum momentum |
| **Diplomatic** | Relationship-aware, consensus-building |
| **Long-Term** | 5-year horizon, compounding advantages |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Full strategic analysis |
| POST | `/decision` | Log a new decision |
| GET | `/decision` | List all decisions |
| GET | `/habits` | Get current habits |
| PUT | `/habits` | Update habits |
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update user profile |
| GET | `/report` | Generate markdown report |
| GET | `/report/pdf` | Download PDF report |

---

## Project Structure

```
harvey_os/
├── app.py                          # Streamlit 10-tab dashboard
├── harvey_brain.txt                # System prompt
├── requirements.txt
├── README.md
├── api/
│   └── server.py                   # FastAPI backend
├── mobile/
│   └── api_client.py               # Mobile/external API client
├── config/
│   └── settings.py                 # All configuration
├── core/
│   ├── brain.py                    # Hybrid LLM brain
│   ├── engine.py                   # Strategic orchestrator
│   ├── memory.py                   # User profile (JSON)
│   ├── vector_store.py             # FAISS vector memory
│   ├── leverage.py                 # Leverage score engine
│   ├── psychology.py               # Pattern analyzer
│   ├── scoring.py                  # Decision tracker
│   ├── learning.py                 # Self-improving decision learning
│   ├── simulation.py               # Scenario simulator
│   ├── board.py                    # Board of Directors
│   ├── trajectory.py               # Trajectory predictor
│   ├── personality.py              # Personality modes
│   ├── reporting.py                # Report engine (markdown + PDF)
│   └── conversation_training.py    # Conversation insight extractor
├── assets/
│   └── styles.css                  # Custom CSS
└── data/
    ├── memory.json
    ├── habits.json
    ├── decisions.json
    ├── conversations.json
    └── learning_history.json
```

---

## Future Scaling

This architecture is designed to evolve into a SaaS product:

- **Database**: Replace JSON files with PostgreSQL (schema-compatible fields)
- **Vector DB**: Replace local FAISS with Pinecone / Weaviate / Qdrant
- **Auth**: Add JWT authentication layer to FastAPI
- **Users**: Multi-tenant user accounts
- **Cloud**: Deploy via Docker + Cloud Run / ECS

---

## License

Private project. All rights reserved.
