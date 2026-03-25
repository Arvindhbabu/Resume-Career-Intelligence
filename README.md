# 🧠 ResumeIQ — AI-Powered Career Intelligence System

> **Beyond ATS Scoring.** ResumeIQ combines NLP parsing, ML job matching, Career DNA mapping, real-time market pulse, resume evolution tracking, and an AI interview coach — all in one platform.

---

## ✨ Novelty Features

| Feature | Description | Tech |
|---|---|---|
| 🧬 **Career DNA Map** | Maps your skills to 8 career archetypes on a radar chart | Custom TF-IDF + Chart.js |
| 📈 **Resume Evolution Tracker** | Tracks score improvement across resume versions | SQLAlchemy + Line Chart |
| 📊 **Real-time Market Pulse** | Shows live demand trends vs your current skill set | REST API + Bar/Line Charts |
| 🎤 **AI Interview Coach** | Generates tailored interview questions from your resume | Gemini/OpenAI API + Fallback |

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────────┐
                    │         User Browser (Frontend)      │
                    │  index.html → dashboard → coach →    │
                    │  market (Chart.js + vanilla JS)      │
                    └────────────┬────────────────────────┘
                                 │ HTTP / REST API
                    ┌────────────▼────────────────────────┐
                    │        Flask Application             │
                    │  /api/upload  /api/results           │
                    │  /api/coach   /api/evolution         │
                    │  /api/market  /api/gap               │
                    └──┬──────────┬────────────┬──────────┘
                       │          │            │
              ┌────────▼──┐  ┌───▼────┐  ┌───▼──────────┐
              │  NLP Stack │  │ML Stack│  │  AI Coach    │
              │ pdfplumber │  │TF-IDF  │  │ Gemini/OAI   │
              │ spaCy NER  │  │Cosine  │  │ Rule-based   │
              │ ATS Scorer │  │Sim.    │  │ fallback     │
              └────────────┘  └───┬────┘  └──────────────┘
                                  │
                    ┌─────────────▼──────────────────────┐
                    │     SQLAlchemy ORM + PostgreSQL      │
                    │  Resume │ Analysis │ JobMatch       │
                    │  EvolutionSnapshot │ InterviewSess  │
                    └────────────────────────────────────┘
```

---

## 📁 Project Structure

```
resumeiq/
├── backend/
│   ├── app.py                    # Flask factory
│   ├── api/
│   │   ├── routes.py             # REST API endpoints
│   │   └── views.py              # HTML page routes
│   ├── parser/
│   │   ├── pdf_parser.py         # PDF/DOCX parser + 500-skill taxonomy
│   │   └── ats_scorer.py         # ATS scorer + Career DNA mapper
│   ├── ml/
│   │   └── recommender.py        # TF-IDF cosine similarity recommender
│   ├── ai_coach/
│   │   └── coach.py              # AI interview question generator
│   └── database/
│       └── models.py             # SQLAlchemy models
├── frontend/templates/
│   ├── index.html                # Upload page (dark grid UI)
│   ├── dashboard.html            # Results + DNA + Evolution + Jobs
│   ├── market.html               # Real-time Market Pulse
│   └── coach.html                # AI Interview Coach
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── wsgi.py                       # Gunicorn entry
├── render.yaml                   # Render.com deploy config
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone and setup
git clone <your-repo>
cd resumeiq
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Configure environment
cp .env.example .env
# Edit .env — add GEMINI_API_KEY if you have one

# 4. Run
python wsgi.py
# Open http://localhost:5000
```

---

## 🐳 Docker (Local)

```bash
cd docker
docker-compose up --build
# Open http://localhost:5000
```

---

## ☁️ Deploy to Render (Free Tier)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo — Render reads `render.yaml` automatically
4. Add env var `GEMINI_API_KEY` (optional) in the Render dashboard
5. Click **Deploy** — live in ~5 minutes

---

## 🔌 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload resume → returns full analysis |
| `GET` | `/api/results/<id>` | Get analysis by ID |
| `GET` | `/api/evolution/<resume_id>` | Resume version history |
| `POST` | `/api/coach/<resume_id>` | Generate interview questions |
| `POST` | `/api/gap` | Skill gap roadmap for target role |
| `GET` | `/api/market` | Market pulse trend data |
| `GET` | `/api/health` | Health check |

### Example: Upload Resume
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "resume=@my_resume.pdf" \
  -F "note=Added AWS certification"
```

### Example: Generate Interview Questions
```bash
curl -X POST http://localhost:5000/api/coach/1 \
  -H "Content-Type: application/json" \
  -d '{"target_role": "Data Scientist", "num_questions": 10}'
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python, Flask, SQLAlchemy, Gunicorn |
| **NLP/Parsing** | spaCy, pdfplumber, python-docx, regex |
| **ML** | TF-IDF, Cosine Similarity, scikit-learn |
| **GenAI** | Google Gemini 1.5 Flash / OpenAI GPT-4o-mini |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Frontend** | HTML5, CSS3, Vanilla JS, Chart.js 4 |
| **DevOps** | Docker, Docker Compose, Render |

---

## 🧬 Career DNA Archetypes

ResumeIQ maps your skills to 8 archetypes and renders a radar chart:

- 🏗️ **The Builder** — Backend & API specialist
- 🧙 **The Data Wizard** — ML & statistical modelling
- ☁️ **The Cloud Architect** — AWS/GCP/Azure & IaC
- ⚙️ **The Data Engineer** — Pipelines & warehousing
- 📖 **The Storyteller** — Visualisation & BI
- 🤖 **The AI Whisperer** — LLMs, RAG & GenAI
- 🖥️ **The Full-Stack Engineer** — React, Node, APIs
- 🔧 **The DevOps Ninja** — CI/CD, Kubernetes, SRE

---

## 📊 ATS Scoring Weights

| Component | Weight | Description |
|---|---|---|
| Skill Coverage | 30% | Skills found vs 500-skill taxonomy |
| Section Completeness | 25% | Summary, Experience, Skills, Education |
| Experience | 20% | Years of experience (log curve) |
| Keyword Density | 15% | Action verbs and industry terms |
| Contact Info | 10% | Email, phone, LinkedIn, GitHub |

---

*Built by Arvindh Babu · ResumeIQ v1.0 · Prodigy Infotech GenAI Internship Project*
