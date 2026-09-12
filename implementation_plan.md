# 🚀 RESUMEIQ — MASTER IMPLEMENTATION PLAN
## AI Career Intelligence & Job Application Operating System

---

## Executive Summary

This implementation plan outlines the comprehensive transformation of **ResumeIQ** from an MVP resume analyzer into a **production-grade AI Career Intelligence & Job Application Operating System**. 

The transformed platform combines:
1. **Career Intelligence Engine** — Persistent profile, Normalized Skill Graph, and Evidence Provenance Network.
2. **Resume Intelligence Engine** — Multi-stage layout parser, Quality Scorer, Evidence Linker, and Version Manager.
3. **Multi-Dimensional ATS Engine** — 6 core sub-scores and 6 Platform-Aware ATS Simulations (Workday, Greenhouse, Lever, Taleo, iCIMS, SuccessFactors).
4. **Job Intelligence Engine** — Job Description Parser, Requirement Classifier (Hard/Important/Preferred), and Pluggable Job Source Adapters.
5. **Explainable Matching & Gap Analysis Engine** — Deterministic scoring, transparent match explanations, Skill ROI, and personalized learning roadmaps.
6. **Evidence-Grounded Tailoring Engine** — Strict **No-Fabrication Guarantee**, visual side-by-side diff viewer, ATS-safe PDF/DOCX document generator, and cover letter engine.
7. **Application Intelligence CRM** — Kanban/Table job search CRM, success prediction, application analytics, and A/B experimentation.
8. **Interview Intelligence Engine** — Resume-aware technical/behavioral question packs, project deep-dives, and **Resume-to-Interview Consistency Checker**.
9. **GitHub Portfolio Intelligence Engine** — Deep repository analysis, README/test/code quality scoring, and portfolio recommendations.
10. **Next-Best-Action Engine** — Dynamic daily priority queue guiding candidate actions.
11. **Security, Privacy & Observability** — JWT auth, encrypted storage, PII scrubbing, structured logging, and token usage metrics.
12. **Testing & AI Evaluation Framework** — Comprehensive unit/integration tests and automated AI evaluation benchmark dataset.

---

## User Review Required

> [!IMPORTANT]
> **Key Architectural Decisions for Confirmation:**
> 1. **Backend Unification:** We will deprecate the legacy Flask entry point (`backend/app.py`) and unify 100% of the backend on **FastAPI 0.115+** (`backend/main.py`), mounting all routes under `/api/v1/`.
> 2. **Authentication System:** We will add JWT authentication (sign up, login, bearer token auth middleware) while allowing guest session tokens for quick upload demos.
> 3. **No-Fabrication Guarantee:** Tailoring will enforce that no skill or bullet point is added unless backed by documented evidence in the candidate's Career Profile or uploaded resume. Unbacked requirements will produce an explicit "INSUFFICIENT EVIDENCE" alert.
> 4. **Document Generation:** Native ATS-safe PDF generation using ReportLab and DOCX generation using python-docx.

---

## Open Questions

> [!NOTE]
> None at present. All requirements have been analyzed from the user request and codebase audit.

---

## Proposed Architectural Components & Phased Execution

---

### Phase 1: Foundation & Security Hardening
- **FastAPI Core & Auth:** Consolidate routes, implement JWT auth (`pyjwt`, `passlib`), security middleware, CORS.
- **Database Schema Expansion:** Migrate database schema in `backend/database/models.py` to support 18 entities (`User`, `CareerProfile`, `SkillEvidence`, `ResumeVersion`, `Job`, `JobRequirement`, `JobMatch`, `Application`, `ApplicationEvent`, `Interview`, `InterviewQuestion`, `PortfolioRepo`, `CareerGoal`, `NextBestAction`, `AIUsage`, `AuditLog`).
- **Testing Infrastructure:** Set up `tests/` directory with `pytest`, `pytest-asyncio`, test fixtures, and mock factories.
- **Logging & Security:** Add PII-scrubbed structured logger and IDOR authorization checks.

#### [MODIFY] [backend/config.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/config.py)
#### [MODIFY] [backend/main.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/main.py)
#### [MODIFY] [backend/database/models.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/database/models.py)
#### [NEW] [backend/database/connection.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/database/connection.py)
#### [NEW] [backend/api/auth_routes.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/api/auth_routes.py)
#### [NEW] [tests/conftest.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/conftest.py)

---

### Phase 2: Career Intelligence Engine & Skill Ontology
- **Persistent Career Profile:** Model user identity, preferences, technical profile, and evidence provenance network.
- **Evidence Graph Engine:** Map skills to evidence nodes (`skill -> evidence -> confidence -> recency -> proficiency`).
- **Skill Ontology:** Build comprehensive normalized skill ontology supporting aliases, categories, related skills, and prerequisites.

#### [NEW] [backend/services/career_profile_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/career_profile_service.py)
#### [NEW] [backend/services/skill_graph_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/skill_graph_service.py)
#### [MODIFY] [backend/ai/skill_graph.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/ai/skill_graph.py)
#### [NEW] [tests/test_skill_graph.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_skill_graph.py)

---

### Phase 3: Multi-Dimensional ATS & Resume Intelligence Engine
- **High-Fidelity Parser:** Multi-stage layout, section, entity, achievement, and metrics extractor.
- **6 Multi-Dimensional Scores:**
  1. Resume Quality Score
  2. Job Match Score
  3. ATS Parseability Score
  4. Evidence Strength Score
  5. Recruiter Impact Score
  6. Application Readiness Score
- **Platform-Aware ATS Simulation:** 6 configurable profiles (Workday, Greenhouse, Lever, Taleo, iCIMS, SuccessFactors) with specific parsing rule variations.

#### [MODIFY] [backend/parser/pdf_parser.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/parser/pdf_parser.py)
#### [NEW] [backend/services/ats_simulation_engine.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/ats_simulation_engine.py)
#### [NEW] [backend/services/resume_intelligence_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/resume_intelligence_service.py)
#### [NEW] [tests/test_ats_simulation.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_ats_simulation.py)

---

### Phase 4: Job Description Intelligence & Explainable Matcher
- **JD Parser & Classifier:** Classify requirements into Hard, Important, Preferred, Nice-to-have.
- **Deterministic Matcher:** Pure mathematical scoring for skills, experience, domain, and evidence strength.
- **Match Explanation Generator:** Transparent "Why you match / Why you don't match / Risk factors / Recommendation" breakdown.
- **Gap Analysis & Skill ROI:** Priority missing skills, difficulty, learning roadmap, and job unlock counts.

#### [NEW] [backend/services/job_intelligence_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/job_intelligence_service.py)
#### [NEW] [backend/services/explainable_matcher_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/explainable_matcher_service.py)
#### [MODIFY] [backend/ai/gap_analyzer.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/ai/gap_analyzer.py)
#### [NEW] [tests/test_job_matcher.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_job_matcher.py)

---

### Phase 5: Evidence-Grounded Resume Tailoring & Document Generation
- **No-Fabrication Tailoring Engine:** Strict evidence validation. Require mapped proof before inserting bullets.
- **Bullet Optimization:** Structure bullets as Action + Work + Context + Scale + Result.
- **Resume Versioning & Visual Diff:** Master resume → Target role → Job versioning with visual diff.
- **ATS-Safe Document Generation:** PDF (ReportLab) and DOCX (python-docx) export engines.
- **Cover Letter Generator:** Evidence-grounded 5-part cover letters.

#### [NEW] [backend/services/resume_tailor_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/resume_tailor_service.py)
#### [NEW] [backend/services/document_generator.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/document_generator.py)
#### [NEW] [backend/services/cover_letter_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/cover_letter_service.py)
#### [NEW] [tests/test_tailoring.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_tailoring.py)

---

### Phase 6: Job Discovery, Application CRM & Next-Best-Action Engine
- **Pluggable Job Adapters:** `GreenhouseSource`, `LeverSource`, `AdzunaSource`, `RemoteOKSource`, `CompanyCareerSource`.
- **Personalized Job Feed:** Ranked daily top jobs based on evidence match, trajectory, and success probability.
- **Application Tracker CRM:** Lifecycle pipeline, timeline events, follow-up reminders, application analytics.
- **Next-Best-Action Engine:** Priority queue ranking actions ("Apply to X", "Tailor for Y", "Learn Z").

#### [NEW] [backend/services/job_discovery_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/job_discovery_service.py)
#### [NEW] [backend/services/application_crm_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/application_crm_service.py)
#### [NEW] [backend/services/next_best_action_engine.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/next_best_action_engine.py)
#### [NEW] [tests/test_application_crm.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_application_crm.py)

---

### Phase 7: Interview Intelligence & Portfolio Intelligence Engine
- **Interview Pack Generator:** JD & resume-aware technical, behavioral, and project deep-dive questions.
- **Resume-to-Interview Consistency Checker:** Detect risky claims where resume claims exceed candidate evidence.
- **GitHub Portfolio Analyzer:** Repo analysis, README depth, code quality, testing, deployment, and recommendations.

#### [NEW] [backend/services/interview_intelligence_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/interview_intelligence_service.py)
#### [NEW] [backend/services/portfolio_intelligence_service.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/services/portfolio_intelligence_service.py)
#### [NEW] [tests/test_interview_consistency.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_interview_consistency.py)

---

### Phase 8: Multi-Agent Orchestration & AI Evaluation Framework
- **Structured Pydantic Agents:** Upgrade multi-agent pipeline with Pydantic V2 response validation, retries, fallbacks.
- **AI Evaluation Benchmark:** Benchmark dataset for parsing precision, skill recall, hallucination rate, and fabrication tests.

#### [MODIFY] [backend/agents/orchestrator.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/agents/orchestrator.py)
#### [NEW] [backend/ai/evaluation_framework.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/ai/evaluation_framework.py)
#### [NEW] [tests/test_ai_evaluation.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_ai_evaluation.py)

---

### Phase 9: Unified API Routes Architecture
- **API v1 Standard:** Expose clear, typed, RESTful endpoints under `/api/v1/`:
  - `/api/v1/auth/*`
  - `/api/v1/career-profile/*`
  - `/api/v1/resumes/*`
  - `/api/v1/ats/*`
  - `/api/v1/jobs/*`
  - `/api/v1/tailor/*`
  - `/api/v1/applications/*`
  - `/api/v1/interviews/*`
  - `/api/v1/portfolio/*`
  - `/api/v1/analytics/*`
  - `/api/v1/next-best-action/*`

#### [NEW] [backend/api/v1_routes.py](file:///c:/Users/varav/Documents/Projects/resumeiq/backend/api/v1_routes.py)
#### [NEW] [tests/test_api_v1.py](file:///c:/Users/varav/Documents/Projects/resumeiq/tests/test_api_v1.py)

---

### Phase 10: Premium Frontend Transformation (React OS UI)
- **Command Center Dashboard:** Daily priority queue, Career Readiness score, top jobs, recommended actions.
- **Career & Evidence Profile UI:** Skill tree visualizer, evidence manager, target role settings.
- **Multi-ATS Simulator UI:** Score breakdown cards + 6 platform tabs (Workday, Greenhouse, Lever, etc.).
- **Job Discovery & Detail Page:** Fit breakdown, hard/preferred skill pills, match explanations, direct tailor action.
- **Resume Editor & Visual Diff Viewer:** Master/version editor, side-by-side diff, PDF/DOCX download.
- **Application Tracker CRM UI:** Kanban board, table view, timeline events, follow-up alerts, response analytics.
- **Interview Coach & Consistency UI:** Question packs, claim risk indicators, answer practice drawer.
- **Portfolio Intelligence UI:** GitHub repo scoring radar, project optimization recommendations.

#### [MODIFY] [frontend/src/App.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/App.jsx)
#### [MODIFY] [frontend/src/index.css](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/index.css)
#### [NEW] [frontend/src/pages/CommandCenterPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/CommandCenterPage.jsx)
#### [NEW] [frontend/src/pages/CareerProfilePage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/CareerProfilePage.jsx)
#### [NEW] [frontend/src/pages/ATSSimulatorPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/ATSSimulatorPage.jsx)
#### [NEW] [frontend/src/pages/JobDiscoveryPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/JobDiscoveryPage.jsx)
#### [NEW] [frontend/src/pages/ResumeTailorPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/ResumeTailorPage.jsx)
#### [NEW] [frontend/src/pages/ApplicationCRMPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/ApplicationCRMPage.jsx)
#### [NEW] [frontend/src/pages/InterviewPrepPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/InterviewPrepPage.jsx)
#### [NEW] [frontend/src/pages/PortfolioPage.jsx](file:///c:/Users/varav/Documents/Projects/resumeiq/frontend/src/pages/PortfolioPage.jsx)

---

### Phase 11: End-to-End Verification & Production Polish
- **Full E2E Execution Test:** Upload resume → Career profile → ATS simulation → Job match → Tailor with diff → PDF render → Application track → Interview prep.
- **Documentation:** Complete update of `README.md` and docs directory (`docs/architecture.md`, `docs/ai-system.md`, `docs/ats-simulation.md`, `docs/evidence-system.md`, `docs/security.md`, `docs/testing.md`).

---

## Verification Plan

### Automated Tests
1. **Pytest Test Suite:**
   ```bash
   pytest tests/ -v
   ```
2. **AI Evaluation Benchmark:**
   ```bash
   python -m pytest tests/test_ai_evaluation.py
   ```
3. **Frontend Build Check:**
   ```bash
   cd frontend && npm run build
   ```

### Manual & E2E Browser Verification
1. Launch FastAPI backend: `uvicorn backend.main:app --port 8000`.
2. Launch React frontend: `cd frontend && npm run dev`.
3. Perform complete candidate flow in browser subagent:
   - Upload sample resume.
   - Inspect Career Profile & Evidence Graph.
   - Run 6 Multi-ATS Platform Simulations.
   - Search & paste a job description.
   - Generate evidence-grounded tailored resume & inspect visual diff.
   - Download generated ATS-safe PDF.
   - Add job to Application CRM.
   - Run Resume-to-Interview Consistency check.

---
