# Resume Career Intelligence

> **AI-powered resume analysis, job matching, ATS simulation, career planning, application intelligence, and interview preparation.**

Resume Career Intelligence is a full-stack AI career intelligence platform that transforms a resume from a static document into a structured career profile and connects that profile with job requirements, skills, evidence, ATS-oriented signals, applications, and interview preparation.

Instead of reducing a candidate to a keyword-match percentage, the system combines **resume intelligence, semantic matching, hierarchical skill intelligence, explainable scoring, multi-agent analysis, career-gap detection, evidence-grounded tailoring, application tracking, interview intelligence, portfolio analysis, recruiter feedback, and career analytics**.

---

## ✨ Why This Project?

Traditional resume analyzers generally follow:

```text
Resume
  ↓
Keyword extraction
  ↓
Keyword matching
  ↓
ATS score
  ↓
Generic suggestions
```

Resume Career Intelligence is designed as a broader decision-support workflow:

```text
                         ┌─────────────────────┐
                         │       Resume        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Resume Intelligence │
                         │ Parse • Extract     │
                         │ Normalize•Structure │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Career Profile      │
                         │ Skills • Experience │
                         │ Evidence • Projects │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │ ATS Engine │       │ Job Matcher│       │ Skill Graph│
       └─────┬──────┘       └─────┬──────┘       └─────┬──────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Explainable Career  │
                       │ Intelligence        │
                       └──────────┬──────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │ Gap &      │       │ Resume     │       │ Interview  │
       │ Roadmap    │       │ Tailoring  │       │Intelligence│
       └─────┬──────┘       └─────┬──────┘       └─────┬──────┘
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Application CRM &   │
                       │ Next Best Action    │
                       └─────────────────────┘
```

The goal is to answer not only:

> **"How good is my resume?"**

but also:

> **"Which roles fit me, why do they fit, what evidence do I have, what am I missing, what should I improve, and what should I do next?"**

---

# 🚀 Core Features

## 1. 🧠 Resume Intelligence

Convert unstructured resumes into structured career information.

- PDF and DOCX resume ingestion
- Text extraction
- Resume section identification
- Contact and entity extraction
- Skills extraction
- Experience extraction
- Project extraction
- Education extraction
- Achievement/metric detection
- Language detection
- Skill normalization
- Structured candidate profile generation

---

## 2. 🎯 Semantic Job Matching

Move beyond exact keyword matching.

Resume Career Intelligence combines structured and semantic signals to determine how closely a candidate aligns with a job.

Example:

```text
Job Requirement:
Deep Learning

Resume Evidence:
Built CNN-based image classification models
using PyTorch and TensorFlow
```

Instead of treating the candidate as missing the exact phrase `Deep Learning`, the system can connect:

```text
CNN
  ↓
Deep Learning
  ↓
Machine Learning
```

Matching signals can include:

- Required skill coverage
- Preferred skill coverage
- Semantic similarity
- Experience relevance
- Domain relevance
- Project relevance
- Evidence strength
- Requirement importance
- Missing requirements
- Confidence signals

---

## 3. 🌳 Hierarchical Skill Intelligence

The skill graph represents relationships between technologies and concepts.

Example:

```text
Machine Learning
├── Deep Learning
│   ├── CNN
│   ├── RNN
│   ├── PyTorch
│   └── TensorFlow
│
├── NLP
│   ├── Transformers
│   ├── BERT
│   └── spaCy
│
└── Computer Vision
    ├── OpenCV
    ├── Image Classification
    └── Object Detection
```

This enables:

- Parent-child skill reasoning
- Skill aliases
- Related-skill recognition
- Skill categorization
- Skill-gap discovery
- More robust matching than string equality

---

## 4. 🤖 Multi-Agent AI Analysis

The backend uses specialized agents instead of delegating the entire workflow to one generic prompt.

### Agent pipeline

```text
Resume Parser Agent
        ↓
Job Understanding Agent
        ↓
Matching Agent
        ↓
Critic Agent
        ↓
Explanation Agent
```

### Responsibilities

**Parser Agent**

Extracts structured candidate information.

**Job Agent**

Interprets role requirements and separates important requirements.

**Matching Agent**

Calculates candidate/job alignment using available structured and semantic signals.

**Critic Agent**

Reviews inconsistencies, weaknesses, missing evidence, and analysis quality.

**Explanation Agent**

Converts structured analysis into understandable explanations and recommendations.

The orchestration layer coordinates the agents and keeps the overall workflow deterministic where possible.

---

## 5. 📊 Explainable Scoring

A single number is not enough.

Instead of:

```text
ATS Score: 78
```

the system can expose contributing dimensions such as:

```text
Overall Match
██████████████████░░  86%

Skills                91%
Experience             84%
Projects               88%
Domain Relevance       82%
ATS Parseability       94%

Strong Evidence
✓ Python
✓ SQL
✓ Machine Learning
✓ FastAPI
✓ PyTorch

Important Gaps
△ Docker
△ Kubernetes
△ System Design
```

The objective is to make recommendations **traceable and understandable**.

---

## 6. 🧪 Multi-ATS Simulation

Resume Career Intelligence includes ATS-oriented simulation rather than claiming access to proprietary ATS ranking algorithms.

The system can analyze factors such as:

- Parsing robustness
- Section structure
- Keyword/skill coverage
- Requirement alignment
- Formatting risks
- Resume completeness
- Job-specific relevance

### Important limitation

Commercial ATS platforms do not publicly expose their complete proprietary ranking algorithms.

Therefore this project describes its output as:

> **ATS simulation / ATS-oriented analysis**

and not as an exact reproduction of Workday, Greenhouse, Lever, or another vendor's proprietary score.

---

## 7. 🛡️ Evidence-Grounded Resume Tailoring

Resume generation should improve relevance **without inventing experience**.

The intended flow is:

```text
Job Requirement
      ↓
Candidate Evidence
      ↓
Supported Claim
      ↓
Tailored Resume Content
```

If the resume does not contain sufficient evidence for a requirement, the system should identify the gap rather than fabricate experience.

This principle is central to the project.

---

## 8. 📚 Skill Gap Analysis & Career Roadmaps

Resume Career Intelligence identifies missing skills and turns them into an actionable roadmap.

Example:

```text
Target Role: Data Scientist

Current
├── Python                 ✓
├── SQL                    ✓
├── Machine Learning       ✓
├── Pandas                 ✓
└── Statistics             ✓

Priority Gaps
├── Docker                 🔴
├── MLOps                  🟠
└── Kubernetes             🟡
```

The roadmap can incorporate:

- Skill priority
- Dependencies
- Estimated learning effort
- Recommended learning sequence
- Project-oriented practice
- Role-match improvement

---

## 9. 💼 Application CRM

Track the job-search lifecycle from one interface.

```text
Saved
  ↓
Applied
  ↓
Screening
  ↓
Interview
  ↓
Offer
  ↓
Accepted / Rejected
```

Capabilities include:

- Application tracking
- Kanban workflow
- Application history
- Status updates
- Follow-up tracking
- Application analytics
- Job-specific resume association

---

## 10. 🎤 Interview Intelligence

Generate preparation based on the **actual resume + target role**.

Potential preparation areas:

- Technical questions
- Behavioral questions
- Project deep dives
- Role-specific questions
- Resume claim verification
- Weak-area identification
- Interview preparation packs

A particularly important design goal is **resume-to-interview consistency**.

If a resume claims:

```text
"Designed and deployed a production ML pipeline"
```

the interview system should be able to challenge the candidate on:

```text
Architecture
Data pipeline
Model selection
Deployment
Monitoring
Trade-offs
Failure handling
```

---

## 11. 🧑‍💻 Portfolio Intelligence

A resume should not be evaluated in isolation.

Portfolio analysis can inspect engineering signals such as:

- Repository documentation
- README quality
- Project relevance
- Testing
- Deployment
- Technical depth
- Engineering practices
- Documentation quality

This helps connect:

```text
Resume Claim
     ↓
Project
     ↓
Repository
     ↓
Evidence
```

---

## 12. 📈 Career & Hiring Analytics

The analytics layer can provide insights into:

- Skill demand
- Candidate skill distribution
- Application pipeline
- Match distribution
- Missing-skill trends
- Career profile changes
- Recruiter feedback patterns

The system is designed to distinguish between:

```text
Market Demand
      vs.
Candidate Profile
```

rather than showing isolated charts with no decision context.

---

## 13. 🧑‍💼 Recruiter Feedback & Learning

Recruiter decisions and user feedback can become structured signals.

Example:

```text
Job
 ↓
Candidate Match
 ↓
Recruiter Decision
 ↓
Feedback
 ↓
Learning Signal
 ↓
Future Recommendations
```

This creates the foundation for adaptive ranking and recommendation systems.

The learning layer should be evaluated carefully before being used for high-impact automated employment decisions.

---

## 14. ⚡ Next-Best-Action Engine

One of the project's central product ideas is to move from analysis to action.

Instead of only reporting:

```text
Missing:
Docker
Kubernetes
```

the system can prioritize actions:

```text
1. Add Docker evidence to Project A
2. Tailor resume for Role B
3. Learn Docker fundamentals
4. Build one deployment-focused project
5. Prepare interview questions around MLOps
```

The purpose is to answer:

> **"What should I do next?"**

---

# 🏗️ Architecture

```text
                         ┌──────────────────────────┐
                         │       React + Vite       │
                         │    Career Intelligence   │
                         │            UI            │
                         └────────────┬─────────────┘
                                      │
                                  REST API
                                      │
                         ┌────────────▼─────────────┐
                         │         FastAPI          │
                         │ API + Orchestration      │
                         └────────────┬─────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│ Resume Intelligence│      │AI / ML Intelligence│      │ Career Services    │
├────────────────────┤      ├────────────────────┤      ├────────────────────┤
│ Parser             │      │ Agents             │      │ Tailoring          │
│ ATS Simulation     │      │ Embeddings         │      │ Applications       │
│ Job Matching       │      │ Skill Graph        │      │ Interview          │
│ Skill Extraction   │      │ XAI                │      │ Portfolio          │
│ Evidence Analysis  │      │ Bias Analysis      │      │ Career Roadmap     │
└──────────┬─────────┘      └──────────┬─────────┘      └──────────┬─────────┘
           │                           │                           │
           └───────────────────────────┼───────────────────────────┘
                                       ▼
                           ┌────────────────────────┐
                           │     Data Layer         │
                           ├────────────────────────┤
                           │ SQLAlchemy             │
                           │ SQLite / PostgreSQL    │
                           │ FAISS Vector Search    │
                           └────────────────────────┘
```

---

# 🧩 Technology Stack

| Layer | Technology |
|---|---|
| Programming | Python, JavaScript |
| Backend | FastAPI, Uvicorn |
| Frontend | React, Vite |
| Database ORM | SQLAlchemy 2 |
| Database | SQLite / PostgreSQL |
| NLP | spaCy |
| Embeddings | Sentence Transformers |
| ML / Similarity | scikit-learn |
| Vector Search | FAISS |
| PDF Processing | pdfplumber |
| DOCX Processing | python-docx |
| AI Providers | OpenAI / Gemini, where configured |
| Charts | Chart.js |
| Icons | Lucide React |
| Testing | pytest |
| Containerization | Docker / Docker Compose |
| Deployment | Render configuration |

---

# 📁 Project Structure

```text
resume-career-intelligence/
│
├── backend/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── parser_agent.py
│   │   ├── job_agent.py
│   │   ├── matching_agent.py
│   │   ├── critic_agent.py
│   │   ├── explanation_agent.py
│   │   └── orchestrator.py
│   │
│   ├── ai/
│   │   ├── embeddings.py
│   │   ├── skill_graph.py
│   │   ├── gap_analyzer.py
│   │   ├── xai_scorer.py
│   │   ├── bias_detector.py
│   │   ├── recruiter_learning.py
│   │   ├── feedback_loop.py
│   │   └── vector_store.py
│   │
│   ├── api/
│   │   ├── auth_routes.py
│   │   ├── v1_routes.py
│   │   └── v2_routes.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── models.py
│   │
│   ├── parser/
│   ├── services/
│   ├── ml/
│   ├── ai_coach/
│   ├── config.py
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── data/
├── docker/
├── tests/
├── docs/
├── .github/
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── requirements.txt
├── render.yaml
└── wsgi.py
```

---

# ⚙️ Local Setup

## Prerequisites

Recommended development environment:

- Python **3.11**
- Node.js **20+**
- npm **10+**
- Git

Python 3.12 can work in some environments, but Python 3.11 is the recommended baseline for reproducible development and deployment.

---

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/resume-career-intelligence.git
cd resume-career-intelligence
```

---

## 2. Create a Python virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install backend dependencies

From the repository root:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

---

## 4. Configure environment variables

Copy the example environment file.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then configure the values required by your environment.

Example:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=false

DATABASE_URL=sqlite:///./data/resumeiq_v2.db

EMBEDDING_MODEL=all-MiniLM-L6-v2
FAISS_INDEX_PATH=./data/faiss_index
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE_MB=10

# Optional
# OPENAI_API_KEY=
# GEMINI_API_KEY=
```

**Never commit `.env` or API keys.**

---

# ▶️ Running the Backend

From the **repository root**, run:

```bash
python -m uvicorn backend.main:app --reload
```

Expected:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

### Important import-path note

Use:

```bash
python -m uvicorn backend.main:app --reload
```

from the project root.

Avoid:

```bash
cd backend
uvicorn main:app --reload
```

when `main.py` imports modules using the `backend.*` package namespace.

---

# ▶️ Running the Frontend

Open a second terminal.

```bash
cd frontend
npm install
npm run dev
```

Vite will normally provide:

```text
http://localhost:5173
```

---

# 🔌 API Overview

The backend exposes versioned APIs.

## Authentication

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

## Career Profile

```text
GET  /api/v1/career-profile
PUT  /api/v1/career-profile
POST /api/v1/career-profile/evidence
```

## Resume

```text
POST /api/v1/resumes/upload
POST /api/v2/upload
GET  /api/v2/analysis/{analysis_id}
GET  /api/v2/evolution/{resume_id}
```

## Job Intelligence

```text
POST /api/v1/jobs/parse
POST /api/v1/jobs/match
GET  /api/v1/jobs/feed
```

## ATS / Intelligence

```text
GET  /api/v2/skill-graph/{resume_id}
GET  /api/v2/bias-report/{resume_id}
POST /api/v2/gap-roadmap
GET  /api/v2/analytics/dashboard
GET  /api/v2/agents/logs/{resume_id}
```

## Resume Tailoring

```text
POST /api/v1/tailor
POST /api/v1/tailor/export-pdf
POST /api/v1/tailor/cover-letter
```

## Applications

```text
GET  /api/v1/applications/kanban
POST /api/v1/applications
PUT  /api/v1/applications/{app_id}/stage
GET  /api/v1/applications/analytics
```

## Interview / Portfolio

```text
POST /api/v1/interviews/prep-pack
POST /api/v1/portfolio/analyze
```

## Decision Support

```text
GET  /api/v1/next-best-action
POST /api/v2/recruiter/decide
GET  /api/v2/recruiter/patterns
POST /api/v2/feedback
GET  /api/v2/market
GET  /api/v2/health
```

For the authoritative generated schema, use:

```text
/docs
```

---

# 🧪 Testing

Run backend tests:

```bash
pytest tests/ -v
```

Run frontend linting:

```bash
cd frontend
npm run lint
```

Build the frontend:

```bash
npm run build
```

A complete validation cycle is:

```bash
pytest tests/ -v

cd frontend
npm run lint
npm run build
```

---

# 🐳 Docker

Build and start the development/production-style stack:

```bash
docker compose -f docker/docker-compose.yml up --build
```

The Docker setup is intended to provide the application and supporting services required by the current architecture.

Before deploying publicly, review:

- secrets
- database credentials
- CORS
- upload storage
- persistent volumes
- authentication
- logging
- resource limits

---

# ☁️ Deployment

The repository includes deployment configuration for Render.

Before production deployment:

- Set a strong production `SECRET_KEY`
- Use PostgreSQL rather than a local SQLite database
- Configure secure CORS origins
- Configure persistent file/object storage
- Store API keys in platform secrets
- Enable HTTPS
- Validate authentication and authorization
- Protect uploaded resumes
- Disable development/demo fallbacks
- Run the full test suite
- Review logging for PII
- Configure monitoring and error reporting

---

# 🔐 Privacy & Security

Resumes may contain:

- Names
- Email addresses
- Phone numbers
- Education history
- Employment history
- Personal links
- Career information

Therefore privacy is a first-class engineering concern.

Production deployments should:

- Minimize data retention
- Encrypt stored documents
- Restrict access by authenticated user
- Avoid raw resume text in logs
- Validate uploaded file types
- Limit upload size
- Protect API endpoints with authentication
- Use HTTPS
- Protect secrets through environment/secret management
- Avoid sending candidate data to external AI providers unless required and disclosed

See [`docs/privacy.md`](docs/privacy.md) for additional guidance.

---

# 🧠 AI Design Principles

## Deterministic scoring where possible

The system should not depend on an LLM for every numerical decision.

A preferred architecture is:

```text
Resume Evidence
      +
Job Requirements
      +
Skill Graph
      +
Semantic Similarity
      +
Experience Signals
      ↓
Structured / Deterministic Score
      ↓
LLM Interpretation & Explanation
```

This improves:

- reproducibility
- testability
- explainability
- debugging
- evaluation

---

## Evidence before generation

Resume Career Intelligence follows:

> **Do not invent candidate experience to satisfy a job description.**

Generated claims should be traceable to candidate evidence whenever possible.

---

## Human-in-the-loop

The platform is intended as a **career decision-support system**.

It should not be presented as an autonomous employment decision-maker.

---

# 🧬 Evidence Model

A future-facing representation of candidate information is:

```text
Candidate
   │
   ├── Skill
   │    └── Evidence
   │
   ├── Experience
   │    └── Evidence
   │
   ├── Project
   │    └── Repository
   │          └── Evidence
   │
   ├── Achievement
   │    └── Metric
   │
   └── Education
```

This makes it possible to connect a generated recommendation to the underlying evidence that supports it.

---

# 📐 Explainable Matching Model

A conceptual matching model can combine several independent signals:

```text
Overall Match
    =
    Skill Alignment
  + Experience Alignment
  + Semantic Relevance
  + Project Evidence
  + Domain Relevance
  + ATS-oriented Signals
```

The exact weighting should be treated as a configurable engineering model and validated against evaluation datasets rather than presented as an objective universal hiring formula.

---

# 🔬 AI Evaluation

A serious AI system needs evaluation, not only demonstrations.

Future evaluation should measure:

| Metric | Purpose |
|---|---|
| Parsing Precision | Accuracy of extracted information |
| Parsing Recall | Coverage of resume information |
| Skill Extraction F1 | Skill detection quality |
| Requirement Classification | Required vs preferred distinction |
| Match Stability | Score consistency |
| Evidence Grounding Rate | Generated claims supported by evidence |
| Hallucination Rate | Unsupported generated information |
| Tailoring Fidelity | Whether tailoring preserves candidate truth |
| Explanation Consistency | Whether explanations match computed signals |
| Recommendation Utility | Whether suggested actions are useful |

Evaluation datasets should be versioned so changes in models, prompts, and scoring logic can be compared reproducibly.

---

# ⚠️ Limitations

### ATS simulation

Resume Career Intelligence does **not** reproduce proprietary ATS algorithms.

Its ATS module provides an engineering simulation based on observable ATS-oriented principles.

### AI recommendations

Recommendations are advisory and can contain errors.

### Bias analysis

A bias report should be interpreted as a risk-detection mechanism, not proof of legal or statistical fairness.

### Hiring decisions

The system should not be used as the sole basis for employment decisions.

---

# 🗺️ Roadmap

## Foundation

- [x] FastAPI backend
- [x] React/Vite frontend
- [x] Resume parsing
- [x] Job description analysis
- [x] Semantic matching
- [x] Skill ontology
- [x] Skill graph
- [x] Multi-agent orchestration
- [x] Explainable scoring
- [x] ATS simulation

## Career Intelligence

- [x] Career profile
- [x] Skill-gap analysis
- [x] Career roadmap
- [x] Resume tailoring
- [x] Application CRM
- [x] Interview preparation
- [x] Portfolio analysis
- [x] Career analytics
- [x] Next-best-action foundation

## Advanced Intelligence

- [x] Recruiter feedback foundation
- [x] Bias-analysis foundation
- [x] Vector search
- [x] Agent execution logging
- [ ] Comprehensive evidence provenance
- [ ] Stronger evaluation benchmark
- [ ] Automated hallucination evaluation
- [ ] Prompt-injection defenses
- [ ] Multimodal/OCR resume parsing
- [ ] Production-grade authentication isolation
- [ ] Full E2E testing
- [ ] Observability
- [ ] Model/version evaluation dashboard

---

# 🧪 Recommended Future Research

Resume Career Intelligence can evolve into a research-oriented platform around:

### 1. Evidence-grounded career intelligence

Can resume recommendations be generated while maintaining measurable evidence provenance?

### 2. Hierarchical skill reasoning

Can skill ontologies reduce false negatives caused by exact keyword matching?

### 3. Explainable job matching

Can candidates understand why a system considers a role suitable?

### 4. Adaptive recommendation

Can recruiter/user feedback improve recommendations without introducing harmful feedback loops?

### 5. Fairness-aware career intelligence

Can irrelevant candidate attributes be prevented from influencing career recommendations?

### 6. Resume-to-interview consistency

Can interview preparation automatically detect claims that require stronger candidate evidence?

---

# 🧑‍💻 Development Guidelines

When contributing:

1. Keep business logic testable.
2. Prefer typed/structured data between services.
3. Keep LLM outputs schema-validated.
4. Do not fabricate candidate information.
5. Do not commit personal resumes.
6. Do not commit API keys.
7. Avoid logging raw PII.
8. Update tests when scoring logic changes.
9. Update documentation when APIs change.
10. Clearly distinguish demo data from production data.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

# 📄 Documentation

| Document | Description |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | System architecture |
| [`docs/ai-system.md`](docs/ai-system.md) | AI and multi-agent design |
| [`docs/api.md`](docs/api.md) | API overview |
| [`docs/testing.md`](docs/testing.md) | Testing and evaluation |
| [`docs/privacy.md`](docs/privacy.md) | Privacy and security |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guide |
| [`SECURITY.md`](SECURITY.md) | Security policy |
| [`CHANGELOG.md`](CHANGELOG.md) | Project history |

---

# 🤝 Contributing

Contributions are welcome.

Typical workflow:

```bash
git checkout -b feature/your-feature
```

Make changes, add tests, then validate:

```bash
pytest tests/ -v

cd frontend
npm run lint
npm run build
```

Create a pull request describing:

- Problem
- Proposed solution
- Implementation
- Tests
- UI screenshots, if applicable
- Security/privacy implications

---

# 📜 License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE).

---

# 🌟 Project Vision

A resume should not be treated as a collection of keywords.

It is a collection of:

```text
Experience
Skills
Projects
Achievements
Evidence
```

Resume Career Intelligence connects those signals with:

```text
Jobs
   ↓
Opportunities
   ↓
Applications
   ↓
Interviews
   ↓
Career Growth
```

The long-term vision is a system that helps people understand **where they stand, where they fit, what evidence they have, what they are missing, and what they should do next**.

> **From resume analysis to career intelligence.**
