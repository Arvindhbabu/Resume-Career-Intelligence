"""
ResumeIQ — API v1 Routes
Unified REST API endpoints for the AI Career Intelligence & Job Application Operating System.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.connection import get_db
from backend.api.auth_routes import get_current_user, require_current_user
from backend.database.models import User, Resume
from backend.services.career_profile_service import career_profile_service
from backend.services.resume_intelligence_service import resume_intelligence_service
from backend.services.ats_simulation_engine import ats_simulation_engine
from backend.services.job_intelligence_service import job_intelligence_service
from backend.services.explainable_matcher_service import explainable_matcher_service
from backend.services.resume_tailor_service import resume_tailor_service
from backend.services.document_generator import document_generator_service
from backend.services.cover_letter_service import cover_letter_service
from backend.services.job_discovery_service import job_discovery_service
from backend.services.application_crm_service import application_crm_service
from backend.services.interview_intelligence_service import interview_intelligence_service
from backend.services.portfolio_intelligence_service import portfolio_intelligence_service
from backend.services.next_best_action_engine import next_best_action_engine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ResumeIQ v1 OS"])


# ── Request Pydantic Schemas ───────────────────────────────────────────────────
class ProfileUpdateReq(BaseModel):
    full_name: Optional[str] = None
    location: Optional[str] = None
    current_role: Optional[str] = None
    target_roles: Optional[List[str]] = None
    total_years_experience: Optional[float] = None
    bio_summary: Optional[str] = None

class AddEvidenceReq(BaseModel):
    skill_name: str
    evidence_type: str = "project"
    source_title: str
    source_url: Optional[str] = None
    snippet: Optional[str] = None
    confidence: float = 1.0
    proficiency: str = "intermediate"

class ParseJDReq(BaseModel):
    raw_jd: str
    title: str = "Target Role"
    company: str = "Target Company"

class MatchReq(BaseModel):
    candidate_skills: List[str]
    candidate_experience_years: float = 3.0
    job_parsed: Dict[str, Any]

class TailorReq(BaseModel):
    resume_id: int
    target_job_title: str
    target_company: str
    required_job_skills: List[str]

class CoverLetterReq(BaseModel):
    candidate_name: str
    target_role: str
    target_company: str
    verified_skills: List[str]
    achievements: Optional[List[str]] = []

class CreateAppReq(BaseModel):
    company_name: str
    job_title: str
    job_url: Optional[str] = None
    status: str = "Saved"
    notes: Optional[str] = None

class UpdateStageReq(BaseModel):
    new_status: str
    notes: Optional[str] = None

class InterviewPrepReq(BaseModel):
    role_title: str
    company_name: str
    resume_text: str
    skills: List[str]

class AnalyzeRepoReq(BaseModel):
    repo_name: str
    repo_url: str
    readme_text: Optional[str] = None
    primary_language: str = "Python"


# ══════════════════════════════════════════════════════════════════════════════
# 1. CAREER PROFILE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.get("/career-profile")
def get_career_profile(
    user: Optional[User] = Depends(get_current_user),
    user_token: str = "guest-demo",
    db: Session = Depends(get_db)
):
    """Get persistent candidate career profile twin."""
    profile = career_profile_service.get_or_create_profile(
        db,
        user_id=user.id if user else None,
        user_token=user_token
    )
    graph = career_profile_service.get_evidence_graph(db, profile.id)
    return {
        "profile": profile.to_dict(),
        "evidence_graph": graph,
    }

@router.put("/career-profile")
def update_career_profile(
    req: ProfileUpdateReq,
    user: Optional[User] = Depends(get_current_user),
    user_token: str = "guest-demo",
    db: Session = Depends(get_db)
):
    """Update candidate career profile twin."""
    profile = career_profile_service.get_or_create_profile(
        db,
        user_id=user.id if user else None,
        user_token=user_token
    )
    updated = career_profile_service.update_profile(db, profile.id, req.model_dump(exclude_unset=True))
    return updated.to_dict()

@router.post("/career-profile/evidence")
def add_skill_evidence(
    req: AddEvidenceReq,
    user: Optional[User] = Depends(get_current_user),
    user_token: str = "guest-demo",
    db: Session = Depends(get_db)
):
    """Add verified evidence node to candidate skill graph."""
    profile = career_profile_service.get_or_create_profile(
        db,
        user_id=user.id if user else None,
        user_token=user_token
    )
    ev = career_profile_service.add_skill_evidence(
        db,
        profile_id=profile.id,
        skill_name=req.skill_name,
        evidence_type=req.evidence_type,
        source_title=req.source_title,
        source_url=req.source_url,
        snippet=req.snippet,
        confidence=req.confidence,
        proficiency=req.proficiency,
    )
    return ev.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# 2. RESUME & MULTI-ATS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.post("/resumes/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    user: Optional[User] = Depends(get_current_user),
    user_token: str = Form("guest-demo"),
    db: Session = Depends(get_db)
):
    """Upload resume and run full high-fidelity processing & multi-ATS simulation."""
    file_bytes = await resume.read()
    raw_text = file_bytes.decode("utf-8", errors="ignore")
    if not raw_text.strip():
        raw_text = f"Sample Resume content for {resume.filename}"

    res = resume_intelligence_service.process_and_analyze_resume(
        db,
        raw_text=raw_text,
        filename=resume.filename or "resume.pdf",
        user_id=user.id if user else None,
        user_token=user_token,
    )
    return res


# ══════════════════════════════════════════════════════════════════════════════
# 3. JOB INTELLIGENCE & MATCHING ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.post("/jobs/parse")
def parse_job_description(req: ParseJDReq):
    """Parse raw Job Description and classify requirement levels."""
    return job_intelligence_service.parse_and_classify_jd(req.raw_jd, req.title, req.company)

@router.post("/jobs/match")
def match_job(req: MatchReq):
    """Calculate deterministic explainable match score."""
    return explainable_matcher_service.match_resume_to_job(
        candidate_skills=req.candidate_skills,
        candidate_experience_years=req.candidate_experience_years,
        job_parsed=req.job_parsed,
    )

@router.get("/jobs/feed")
def get_job_feed(
    skills: str = "python,pytorch,fastapi",
    target_role: str = "Data Scientist"
):
    """Get personalized, deduplicated top job opportunities feed."""
    cand_skills = [s.strip() for s in skills.split(",") if s.strip()]
    return job_discovery_service.fetch_personalized_feed(cand_skills, target_role)


# ══════════════════════════════════════════════════════════════════════════════
# 4. TAILORING & DOCUMENT EXPORT ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.post("/tailor")
def tailor_resume(
    req: TailorReq,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate evidence-grounded tailored resume with No-Fabrication Guarantee."""
    profile_id = None
    if user:
        p = career_profile_service.get_or_create_profile(db, user_id=user.id)
        profile_id = p.id

    res = resume_tailor_service.tailor_resume_for_job(
        db,
        master_resume_id=req.resume_id,
        target_job_title=req.target_job_title,
        target_company=req.target_company,
        required_job_skills=req.required_job_skills,
        profile_id=profile_id,
    )
    return res

@router.post("/tailor/export-pdf")
def export_pdf(structured_content: Dict[str, Any]):
    """Render ATS-safe PDF document."""
    filepath = document_generator_service.generate_pdf(structured_content, "tailored_resume.pdf")
    return {"pdf_path": filepath, "status": "success"}

@router.post("/tailor/cover-letter")
def generate_cover_letter(req: CoverLetterReq):
    """Generate 5-part evidence-grounded cover letter."""
    return cover_letter_service.generate_cover_letter(
        candidate_name=req.candidate_name,
        target_role=req.target_role,
        target_company=req.target_company,
        verified_skills=req.verified_skills,
        achievements=req.achievements or [],
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5. APPLICATION CRM ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.get("/applications/kanban")
def get_kanban(user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get Kanban board stage columns."""
    return application_crm_service.get_kanban_board(db, user_id=user.id if user else None)

@router.post("/applications")
def create_application(req: CreateAppReq, user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create job application CRM entry."""
    app = application_crm_service.create_application(
        db,
        company_name=req.company_name,
        job_title=req.job_title,
        user_id=user.id if user else None,
        job_url=req.job_url,
        status=req.status,
        notes=req.notes,
    )
    return app.to_dict()

@router.put("/applications/{app_id}/stage")
def update_stage(app_id: int, req: UpdateStageReq, db: Session = Depends(get_db)):
    """Move application stage."""
    app = application_crm_service.update_stage(db, app_id, req.new_status, req.notes)
    return app.to_dict()

@router.get("/applications/analytics")
def get_crm_analytics(user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get CRM response analytics."""
    return application_crm_service.get_analytics(db, user_id=user.id if user else None)


# ══════════════════════════════════════════════════════════════════════════════
# 6. INTERVIEW & PORTFOLIO INTELLIGENCE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.post("/interviews/prep-pack")
def generate_interview_pack(req: InterviewPrepReq, db: Session = Depends(get_db)):
    """Generate interview pack with consistency risk check."""
    return interview_intelligence_service.generate_interview_pack(
        db,
        role_title=req.role_title,
        company_name=req.company_name,
        resume_text=req.resume_text,
        skills=req.skills,
    )

@router.post("/portfolio/analyze")
def analyze_repo(req: AnalyzeRepoReq, user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze GitHub repo for technical depth."""
    repo = portfolio_intelligence_service.analyze_repository(
        db,
        repo_url=req.repo_url,
        repo_name=req.repo_name,
        user_id=user.id if user else None,
        readme_text=req.readme_text,
        primary_language=req.primary_language,
    )
    return repo.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# 7. NEXT-BEST-ACTION PRIORITY QUEUE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════
@router.get("/next-best-action")
def get_next_best_actions(user: Optional[User] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get candidate daily priority queue."""
    actions = next_best_action_engine.generate_action_queue(db, user_id=user.id if user else None)
    return {"actions": actions}
