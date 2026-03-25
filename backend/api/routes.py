"""
ResumeIQ — REST API Routes
All /api/* endpoints for the frontend to consume.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from backend.app import db
from backend.database.models import (
    Resume, Analysis, JobMatch, EvolutionSnapshot, InterviewSession
)
from backend.parser.pdf_parser import parser as resume_parser
from backend.parser.ats_scorer import scorer as ats_scorer
from backend.ml.recommender import recommender as job_recommender
from backend.ai_coach.coach import coach as interview_coach

logger   = logging.getLogger(__name__)
api_bp   = Blueprint("api", __name__)
ALLOWED  = {".pdf", ".docx", ".doc", ".txt"}


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED


def _user_token() -> str:
    """Generate or read a session-based user token."""
    return request.headers.get("X-User-Token") or str(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/upload  — upload + fully analyse a resume
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify(error="No file uploaded. Field name must be 'resume'."), 400

    file  = request.files["resume"]
    note  = request.form.get("note", "")           # Evolution tracker note
    token = _user_token()

    if not file.filename or not _allowed(file.filename):
        return jsonify(error="Unsupported file type. Upload PDF or DOCX."), 400

    filename   = secure_filename(file.filename)
    file_bytes = file.read()

    # ── 1. Parse ───────────────────────────────────────────────────────────────
    try:
        parsed = resume_parser.parse(file_bytes=file_bytes, filename=filename)
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return jsonify(error="Could not parse the resume. Ensure it is text-based."), 422

    # ── 2. Score ───────────────────────────────────────────────────────────────
    scores = ats_scorer.score(parsed)

    # ── 3. Job Recommendations ─────────────────────────────────────────────────
    matches = job_recommender.recommend(parsed.get("skills", []), top_n=5)

    # ── 4. Persist to DB ───────────────────────────────────────────────────────
    resume = Resume(
        user_token=token,
        filename=filename,
        raw_text=parsed.get("raw_text", "")[:50_000],   # cap at 50k chars
    )
    db.session.add(resume)
    db.session.flush()  # get resume.id

    analysis = Analysis(
        resume_id=resume.id,
        ats_score=scores["ats_score"],
        skill_score=scores["skill_score"],
        format_score=scores["format_score"],
        experience_score=scores["experience_score"],
        overall_score=scores["overall_score"],
        skills_found=json.dumps(scores["skills_found"]),
        skills_missing=json.dumps(scores["skills_missing"]),
        career_dna=json.dumps(scores["career_dna"]),
        recommendations=json.dumps(scores["recommendations"]),
    )
    db.session.add(analysis)
    db.session.flush()

    for m in matches:
        db.session.add(JobMatch(
            analysis_id=analysis.id,
            job_title=m["job_title"],
            company_type=m["company_type"],
            match_score=m["match_score"],
            salary_range=m["salary_range"],
            required_skills=json.dumps(m["required_skills"]),
            missing_skills=json.dumps(m["missing_skills"]),
            job_url=m["job_url"],
        ))

    # ── 5. Evolution Snapshot ──────────────────────────────────────────────────
    prev = (EvolutionSnapshot.query
            .filter_by(resume_id=resume.id)
            .order_by(EvolutionSnapshot.version.desc())
            .first())
    version = (prev.version + 1) if prev else 1
    delta   = round(scores["overall_score"] - prev.overall_score, 1) if prev else 0.0

    snapshot = EvolutionSnapshot(
        resume_id=resume.id,
        version=version,
        overall_score=scores["overall_score"],
        ats_score=scores["ats_score"],
        skill_score=scores["skill_score"],
        delta=delta,
        note=note or f"Version {version}",
    )
    db.session.add(snapshot)
    db.session.commit()

    return jsonify({
        "resume_id":   resume.id,
        "analysis_id": analysis.id,
        "user_token":  token,
        "parsed": {
            "name":     parsed.get("name"),
            "email":    parsed.get("email"),
            "phone":    parsed.get("phone"),
            "linkedin": parsed.get("linkedin"),
            "github":   parsed.get("github"),
            "years_of_experience": parsed.get("years_of_experience"),
        },
        "scores":      scores,
        "matches":     matches,
        "snapshot":    snapshot.to_dict(),
    }), 201


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/results/<analysis_id>
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/results/<int:analysis_id>", methods=["GET"])
def get_results(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    matches  = [m.to_dict() for m in analysis.job_matches]
    return jsonify({**analysis.to_dict(), "job_matches": matches})


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/evolution/<resume_id>  — Resume Evolution Tracker
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/evolution/<int:resume_id>", methods=["GET"])
def get_evolution(resume_id):
    snapshots = (EvolutionSnapshot.query
                 .filter_by(resume_id=resume_id)
                 .order_by(EvolutionSnapshot.version)
                 .all())
    return jsonify({
        "resume_id": resume_id,
        "snapshots": [s.to_dict() for s in snapshots],
        "latest_score": snapshots[-1].overall_score if snapshots else 0,
        "total_improvement": round(
            (snapshots[-1].overall_score - snapshots[0].overall_score), 1
        ) if len(snapshots) >= 2 else 0,
    })


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/coach/<resume_id>  — AI Interview Prep Coach
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/coach/<int:resume_id>", methods=["POST"])
def generate_interview_questions(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    role   = request.json.get("target_role", "Software Engineer") if request.is_json else "Software Engineer"
    n      = min(int(request.json.get("num_questions", 10)), 20) if request.is_json else 10

    latest_analysis = (Analysis.query
                       .filter_by(resume_id=resume_id)
                       .order_by(Analysis.created_at.desc())
                       .first())

    parsed = {
        "name":   resume.filename,
        "skills": json.loads(latest_analysis.skills_found) if latest_analysis else [],
        "years_of_experience": 0,
        "projects": True,
    }

    questions = interview_coach.generate(parsed, role, n)

    session = InterviewSession(
        resume_id=resume_id,
        role=role,
        questions=json.dumps(questions),
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "session_id": session.id,
        "role":       role,
        "questions":  questions,
    }), 201


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/gap  — Skill Gap & Roadmap for a target role
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/gap", methods=["POST"])
def skill_gap():
    data  = request.get_json(silent=True) or {}
    skills = data.get("skills", [])
    role   = data.get("target_role", "")
    if not role:
        return jsonify(error="target_role is required."), 400
    roadmap = job_recommender.skill_gap_roadmap(skills, role)
    return jsonify(roadmap)


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/market  — Real-time Job Market Pulse (trend data)
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/market", methods=["GET"])
def market_pulse():
    """
    Returns demand trend data for top skills.
    In production: connect to Adzuna/LinkedIn API or scrape job boards.
    Here we return realistic synthetic trend data.
    """
    trends = {
        "trending_skills": [
            {"skill": "LLM/RAG Engineering", "demand_score": 98, "yoy_growth": "+340%"},
            {"skill": "MLOps",               "demand_score": 91, "yoy_growth": "+128%"},
            {"skill": "Kubernetes",          "demand_score": 87, "yoy_growth": "+65%"},
            {"skill": "dbt",                 "demand_score": 83, "yoy_growth": "+112%"},
            {"skill": "Spark",               "demand_score": 79, "yoy_growth": "+42%"},
            {"skill": "Terraform",           "demand_score": 77, "yoy_growth": "+58%"},
            {"skill": "Python",              "demand_score": 95, "yoy_growth": "+31%"},
            {"skill": "Rust",                "demand_score": 62, "yoy_growth": "+89%"},
        ],
        "top_roles_by_openings": [
            {"role": "GenAI / LLM Engineer",  "openings": 12_400, "avg_salary": "₹22 LPA"},
            {"role": "Data Engineer",         "openings": 18_200, "avg_salary": "₹14 LPA"},
            {"role": "ML Engineer",           "openings": 9_800,  "avg_salary": "₹18 LPA"},
            {"role": "Data Analyst",          "openings": 24_000, "avg_salary": "₹8 LPA"},
            {"role": "DevOps / MLOps",        "openings": 11_000, "avg_salary": "₹16 LPA"},
        ],
        "monthly_job_trend": [
            {"month": "Oct", "openings": 42_000},
            {"month": "Nov", "openings": 44_500},
            {"month": "Dec", "openings": 38_000},
            {"month": "Jan", "openings": 51_000},
            {"month": "Feb", "openings": 55_200},
            {"month": "Mar", "openings": 59_800},
        ],
    }
    return jsonify(trends)


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/health
# ══════════════════════════════════════════════════════════════════════════════
@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", version="1.0.0")
