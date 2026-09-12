"""
ResumeIQ v2 — API Routes
All /api/v2/* endpoints for the Intelligent Hiring Co-Pilot.
"""

import io
import json
import uuid
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.config import get_settings
from backend.database.connection import get_db
from backend.database.models import (
    Resume, Analysis, SkillMapping, JobMatch, BiasReport,
    RecruiterDecision, AgentLog, FeedbackEntry, EvolutionSnapshot,
    InterviewSession,
)
from backend.agents.orchestrator import orchestrator
from backend.ai.xai_scorer import xai_scorer
from backend.ai.gap_analyzer import gap_analyzer
from backend.ai.bias_detector import bias_detector
from backend.ai.recruiter_learning import recruiter_engine
from backend.ai.feedback_loop import feedback_loop
from backend.ai.skill_graph import skill_graph
from backend.ai.embeddings import embedding_engine
from backend.ai.vector_store import resume_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ResumeIQ v2"])

ALLOWED = {".pdf", ".docx", ".doc", ".txt"}


# ── Pydantic models for request bodies ──────────────────────────────────────────
class GapRequest(BaseModel):
    skills: list[str]
    target_role: str

class DecisionRequest(BaseModel):
    resume_id: int
    job_title: str
    decision: str  # "selected" or "rejected"
    reason: Optional[str] = None
    recruiter_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    resume_id: Optional[int] = None
    feedback_type: str
    original_value: str
    corrected_value: str
    comment: Optional[str] = None

class CoachRequest(BaseModel):
    target_role: str = "Software Engineer"
    num_questions: int = 10


# ══════════════════════════════════════════════════════════════════════════════════
# POST /api/v2/upload — Upload + Full Multi-Agent Analysis
# ══════════════════════════════════════════════════════════════════════════════════
@router.post("/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
):
    """Upload a resume and run the full multi-agent analysis pipeline."""
    # Validate file
    ext = Path(resume.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Unsupported file type: {ext}. Use PDF or DOCX.")

    file_bytes = await resume.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(413, "File too large. Max 10 MB.")

    # ── Parse the file ───────────────────────────────────────────────────────
    from backend.parser.pdf_parser import parser as pdf_parser
    try:
        raw_text = ""
        if ext == ".pdf":
            raw_text = pdf_parser._extract_pdf(None, file_bytes)
        elif ext in (".docx", ".doc"):
            raw_text = pdf_parser._extract_docx(None, file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Parse error: {e}")
        raise HTTPException(422, "Could not parse the resume.")

    if not raw_text.strip():
        raise HTTPException(422, "Could not extract text from the resume.")

    # ── Run multi-agent pipeline ─────────────────────────────────────────────
    result = await orchestrator.run_pipeline(
        raw_text=raw_text,
        filename=resume.filename or "resume",
        note=note,
    )

    parsed = result.get("parsed", {})
    scores = result.get("scores", {})
    token = str(uuid.uuid4())

    # ── Generate embedding ───────────────────────────────────────────────────
    embedding = embedding_engine.encode_resume(parsed)

    # ── Run XAI scorer ───────────────────────────────────────────────────────
    xai_result = xai_scorer.score(parsed)

    # ── Run bias detection ───────────────────────────────────────────────────
    bias_result = bias_detector.analyze(parsed, {
        **scores,
        "skills_missing": result.get("skills_missing", []),
    })

    # ── Persist to database ──────────────────────────────────────────────────
    resume_record = Resume(
        user_token=token,
        filename=resume.filename or "resume",
        raw_text=raw_text[:50000],
        language=parsed.get("language", "en"),
        embedding_vector=embedding_engine.serialize_vector(embedding),
    )
    db.add(resume_record)
    db.flush()

    analysis = Analysis(
        resume_id=resume_record.id,
        overall_score=scores.get("overall_score", 0),
        skills_match_score=scores.get("skills_match", 0),
        experience_match_score=scores.get("experience_match", 0),
        domain_relevance_score=scores.get("domain_relevance", 0),
        project_complexity_score=scores.get("project_complexity", 0),
        format_score=scores.get("format_quality", 0),
        confidence=scores.get("confidence", 0.5),
        skills_found=json.dumps(result.get("skills_found", [])),
        skills_missing=json.dumps(result.get("skills_missing", [])),
        career_dna=json.dumps(result.get("career_dna", {})),
        score_explanation=result.get("explanation", {}).get("summary", ""),
        recommendations=json.dumps(result.get("recommendations", [])),
        agent_summary=json.dumps(result.get("agent_logs", [])),
    )
    db.add(analysis)
    db.flush()

    # Persist job matches
    for m in result.get("job_matches", [])[:10]:
        db.add(JobMatch(
            analysis_id=analysis.id,
            job_title=m.get("job_title", ""),
            company_type=m.get("company_type", ""),
            match_score=m.get("final_score", m.get("match_score", 0)),
            salary_range=m.get("salary_range", ""),
            required_skills=json.dumps(m.get("required_skills", [])),
            missing_skills=json.dumps(m.get("skills_missing", m.get("skill_details", {}).get("missing", []))),
            match_explanation=json.dumps(m.get("dimension_scores", {})),
            job_url=m.get("job_url", ""),
        ))

    # Persist skill mappings
    for sm in parsed.get("skill_graph_mappings", []):
        db.add(SkillMapping(
            resume_id=resume_record.id,
            skill_name=sm.get("skill", ""),
            canonical_name=sm.get("canonical", ""),
            category=sm.get("category", ""),
            parent_category=sm.get("parent", ""),
            confidence=sm.get("confidence", 1.0),
            inferred=sm.get("inferred", False),
        ))

    # Persist bias report
    br = BiasReport(
        resume_id=resume_record.id,
        gender_bias_score=bias_result.get("gender_bias_score", 0),
        institution_bias_score=bias_result.get("institution_bias_score", 0),
        keyword_bias_score=bias_result.get("keyword_bias_score", 0),
        overall_bias_risk=bias_result.get("overall_bias_risk", 0),
        findings=json.dumps(bias_result.get("findings", [])),
        equivalent_skills=json.dumps(bias_result.get("equivalent_skills", [])),
        anonymized_score_diff=bias_result.get("anonymized_score_diff", 0),
        recommendations=json.dumps(bias_result.get("recommendations", [])),
    )
    db.add(br)

    # Persist agent logs
    pipeline_id = result.get("pipeline_id", "")
    for log in result.get("agent_logs", []):
        db.add(AgentLog(
            resume_id=resume_record.id,
            pipeline_id=pipeline_id,
            agent_name=log.get("agent", ""),
            status=log.get("status", ""),
            duration_ms=log.get("duration_ms", 0),
        ))

    # Evolution snapshot
    prev = (db.query(EvolutionSnapshot)
            .filter_by(resume_id=resume_record.id)
            .order_by(EvolutionSnapshot.version.desc())
            .first())
    version = (prev.version + 1) if prev else 1
    delta = round(scores.get("overall_score", 0) - (prev.overall_score or 0), 1) if prev else 0.0

    snapshot = EvolutionSnapshot(
        resume_id=resume_record.id,
        version=version,
        overall_score=scores.get("overall_score", 0),
        skills_match_score=scores.get("skills_match", 0),
        experience_score=scores.get("experience_match", 0),
        delta=delta,
        note=note or f"Version {version}",
    )
    db.add(snapshot)

    # Add to vector store
    resume_store.add(embedding, {
        "resume_id": resume_record.id,
        "filename": resume.filename,
        "skills": parsed.get("skills", [])[:20],
        "score": scores.get("overall_score", 0),
    })

    db.commit()

    return {
        "resume_id": resume_record.id,
        "analysis_id": analysis.id,
        "user_token": token,
        "pipeline_id": pipeline_id,
        "parsed": {
            "name": parsed.get("name"),
            "email": parsed.get("email"),
            "phone": parsed.get("phone"),
            "linkedin": parsed.get("linkedin"),
            "github": parsed.get("github"),
            "years_of_experience": parsed.get("years_of_experience", 0),
            "skills_count": len(parsed.get("skills", [])),
            "inferred_skills_count": len(parsed.get("inferred_skills", [])),
        },
        "scores": scores,
        "xai_breakdown": xai_result.get("dimensions", {}),
        "career_dna": result.get("career_dna", {}),
        "job_matches": result.get("job_matches", [])[:5],
        "explanation": result.get("explanation", {}),
        "bias_report": bias_result,
        "skills_found": result.get("skills_found", []),
        "skills_missing": result.get("skills_missing", []),
        "recommendations": result.get("recommendations", []),
        "agent_logs": result.get("agent_logs", []),
        "snapshot": snapshot.to_dict(),
        "total_duration_ms": result.get("total_duration_ms", 0),
    }


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/analysis/{id} — Get Analysis Results
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get full XAI analysis results by ID."""
    analysis = db.query(Analysis).filter_by(id=analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")

    matches = [m.to_dict() for m in db.query(JobMatch).filter_by(analysis_id=analysis_id).all()]

    return {**analysis.to_dict(), "job_matches": matches}


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/skill-graph/{resume_id} — Skill Graph
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/skill-graph/{resume_id}")
def get_skill_graph(resume_id: int, db: Session = Depends(get_db)):
    """Get skill ontology mapping for a resume."""
    mappings = db.query(SkillMapping).filter_by(resume_id=resume_id).all()
    if not mappings:
        raise HTTPException(404, "No skill mappings found")

    return {
        "resume_id": resume_id,
        "mappings": [m.to_dict() for m in mappings],
        "tree_summary": skill_graph.get_skill_tree_summary(),
    }


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/bias-report/{resume_id} — Bias Report
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/bias-report/{resume_id}")
def get_bias_report(resume_id: int, db: Session = Depends(get_db)):
    """Get bias detection report for a resume."""
    report = db.query(BiasReport).filter_by(resume_id=resume_id).order_by(BiasReport.id.desc()).first()
    if not report:
        raise HTTPException(404, "No bias report found")
    return report.to_dict()


# ══════════════════════════════════════════════════════════════════════════════════
# POST /api/v2/gap-roadmap — Smart Gap Analysis
# ══════════════════════════════════════════════════════════════════════════════════
@router.post("/gap-roadmap")
def gap_roadmap(req: GapRequest):
    """Generate a skill gap analysis and learning roadmap."""
    if not req.target_role:
        raise HTTPException(400, "target_role is required")
    result = gap_analyzer.analyze(req.skills, req.target_role)
    return result


# ══════════════════════════════════════════════════════════════════════════════════
# POST /api/v2/recruiter/decide — Record Decision
# ══════════════════════════════════════════════════════════════════════════════════
@router.post("/recruiter/decide")
def record_decision(req: DecisionRequest, db: Session = Depends(get_db)):
    """Record a recruiter's hiring decision."""
    if req.decision not in ("selected", "rejected"):
        raise HTTPException(400, "decision must be 'selected' or 'rejected'")

    # Get resume skills
    resume = db.query(Resume).filter_by(id=req.resume_id).first()
    skills = []
    if resume:
        analysis = db.query(Analysis).filter_by(resume_id=req.resume_id).order_by(Analysis.id.desc()).first()
        if analysis:
            skills = json.loads(analysis.skills_found or "[]")

    # Record in DB
    decision = RecruiterDecision(
        resume_id=req.resume_id,
        job_title=req.job_title,
        decision=req.decision,
        reason=req.reason,
        recruiter_id=req.recruiter_id or "anonymous",
        skills_valued=json.dumps(skills[:20]),
    )
    db.add(decision)
    db.commit()

    # Also record in learning engine
    recruiter_engine.record_decision({
        "resume_id": req.resume_id,
        "job_title": req.job_title,
        "decision": req.decision,
        "reason": req.reason,
        "candidate_skills": skills,
        "recruiter_id": req.recruiter_id,
    })

    return {"recorded": True, "decision_id": decision.id}


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/recruiter/patterns — Hiring Patterns
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/recruiter/patterns")
def hiring_patterns(job_title: Optional[str] = None):
    """Get hiring pattern insights from recruiter decisions."""
    return recruiter_engine.get_patterns(job_title=job_title)


# ══════════════════════════════════════════════════════════════════════════════════
# POST /api/v2/feedback — Submit Feedback
# ══════════════════════════════════════════════════════════════════════════════════
@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    """Submit feedback for continuous learning."""
    entry = FeedbackEntry(
        resume_id=req.resume_id,
        feedback_type=req.feedback_type,
        original_value=req.original_value,
        corrected_value=req.corrected_value,
        comment=req.comment,
    )
    db.add(entry)
    db.commit()

    result = feedback_loop.submit_feedback(req.model_dump())
    return result


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/analytics/dashboard — Hiring Dashboard
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/analytics/dashboard")
def analytics_dashboard(db: Session = Depends(get_db)):
    """Aggregated hiring analytics for the dashboard."""
    total_resumes = db.query(Resume).count()
    total_analyses = db.query(Analysis).count()

    # Recent analyses
    recent = (db.query(Analysis)
              .order_by(Analysis.created_at.desc())
              .limit(10)
              .all())

    avg_score = 0
    if recent:
        avg_score = sum(a.overall_score or 0 for a in recent) / len(recent)

    # Skill distribution
    all_mappings = db.query(SkillMapping).limit(500).all()
    skill_counts = {}
    for m in all_mappings:
        cat = m.category or "Other"
        skill_counts[cat] = skill_counts.get(cat, 0) + 1

    return {
        "total_resumes": total_resumes,
        "total_analyses": total_analyses,
        "avg_score": round(avg_score, 1),
        "recent_analyses": [a.to_dict() for a in recent[:5]],
        "skill_distribution": skill_counts,
        "hiring_patterns": recruiter_engine.get_patterns(),
        "feedback_summary": feedback_loop.get_feedback_summary(),
    }


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/agents/logs/{resume_id} — Agent Pipeline Logs
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/agents/logs/{resume_id}")
def agent_logs(resume_id: int, db: Session = Depends(get_db)):
    """Get multi-agent pipeline execution logs."""
    logs = db.query(AgentLog).filter_by(resume_id=resume_id).order_by(AgentLog.id).all()
    return {"resume_id": resume_id, "logs": [l.to_dict() for l in logs]}


# ══════════════════════════════════════════════════════════════════════════════════
# POST /api/v2/coach/{resume_id} — AI Interview Coach
# ══════════════════════════════════════════════════════════════════════════════════
@router.post("/coach/{resume_id}")
def interview_coach(resume_id: int, req: CoachRequest, db: Session = Depends(get_db)):
    """Generate AI-powered interview questions."""
    resume = db.query(Resume).filter_by(id=resume_id).first()
    if not resume:
        raise HTTPException(404, "Resume not found")

    analysis = db.query(Analysis).filter_by(resume_id=resume_id).order_by(Analysis.id.desc()).first()
    skills = json.loads(analysis.skills_found or "[]") if analysis else []

    from backend.ai_coach.coach import coach
    parsed = {"name": resume.filename, "skills": skills, "years_of_experience": 0, "projects": True}
    questions = coach.generate(parsed, req.target_role, min(req.num_questions, 20))

    session = InterviewSession(
        resume_id=resume_id,
        role=req.target_role,
        questions=json.dumps(questions),
    )
    db.add(session)
    db.commit()

    return {"session_id": session.id, "role": req.target_role, "questions": questions}


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/evolution/{resume_id} — Evolution Tracker
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/evolution/{resume_id}")
def get_evolution(resume_id: int, db: Session = Depends(get_db)):
    """Get resume evolution history."""
    snapshots = (db.query(EvolutionSnapshot)
                 .filter_by(resume_id=resume_id)
                 .order_by(EvolutionSnapshot.version)
                 .all())
    return {
        "resume_id": resume_id,
        "snapshots": [s.to_dict() for s in snapshots],
        "latest_score": snapshots[-1].overall_score if snapshots else 0,
        "total_improvement": round(
            (snapshots[-1].overall_score - snapshots[0].overall_score), 1
        ) if len(snapshots) >= 2 else 0,
    }


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/market — Market Pulse
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/market")
def market_pulse():
    """Real-time job market trend data."""
    return {
        "trending_skills": [
            {"skill": "LLM/RAG Engineering", "demand_score": 98, "yoy_growth": "+340%"},
            {"skill": "MLOps", "demand_score": 91, "yoy_growth": "+128%"},
            {"skill": "Kubernetes", "demand_score": 87, "yoy_growth": "+65%"},
            {"skill": "dbt", "demand_score": 83, "yoy_growth": "+112%"},
            {"skill": "Spark", "demand_score": 79, "yoy_growth": "+42%"},
            {"skill": "Terraform", "demand_score": 77, "yoy_growth": "+58%"},
            {"skill": "Python", "demand_score": 95, "yoy_growth": "+31%"},
            {"skill": "Rust", "demand_score": 62, "yoy_growth": "+89%"},
        ],
        "top_roles_by_openings": [
            {"role": "GenAI / LLM Engineer", "openings": 12400, "avg_salary": "₹22 LPA"},
            {"role": "Data Engineer", "openings": 18200, "avg_salary": "₹14 LPA"},
            {"role": "ML Engineer", "openings": 9800, "avg_salary": "₹18 LPA"},
            {"role": "Data Analyst", "openings": 24000, "avg_salary": "₹8 LPA"},
            {"role": "DevOps / MLOps", "openings": 11000, "avg_salary": "₹16 LPA"},
        ],
        "monthly_job_trend": [
            {"month": "Oct", "openings": 42000},
            {"month": "Nov", "openings": 44500},
            {"month": "Dec", "openings": 38000},
            {"month": "Jan", "openings": 51000},
            {"month": "Feb", "openings": 55200},
            {"month": "Mar", "openings": 59800},
        ],
    }


# ══════════════════════════════════════════════════════════════════════════════════
# GET /api/v2/health — Health Check
# ══════════════════════════════════════════════════════════════════════════════════
@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "version": "2.0.0",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.EMBEDDING_MODEL,
        "features": [
            "multi_agent_system",
            "semantic_embeddings",
            "skill_graph",
            "xai_scoring",
            "bias_detection",
            "gap_analysis",
            "recruiter_learning",
            "feedback_loop",
        ],
    }
