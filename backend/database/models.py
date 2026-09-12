"""
ResumeIQ — Database Models
Comprehensive normalized models for the AI Career Intelligence & Job Application OS.

Entities:
  1. User: Auth & identity
  2. CareerProfile: Persistent career identity, preferences, and profile
  3. SkillEvidence: Evidence provenance graph for candidate claims
  4. Resume: Uploaded master resume & extracted content
  5. ResumeVersion: Tailored job-specific resume snapshots
  6. Analysis: Multi-dimensional XAI scoring & analysis
  7. SkillMapping: Resume to ontology graph mapping
  8. Job: Normalized job postings from multiple sources
  9. JobRequirement: Granular requirement classification (Hard/Important/Preferred)
 10. JobMatch: Explainable match evaluation
 11. Application: Kanban application tracker CRM
 12. ApplicationEvent: Application history timeline & audit
 13. Interview: Interview prep sessions & consistency evaluations
 14. InterviewQuestion: Resume-aware interview question bank
 15. PortfolioRepo: Parsed GitHub projects & code quality intelligence
 16. CareerGoal: Target trajectory & skill gap targets
 17. NextBestAction: Candidate priority action queue
 18. RecruiterDecision, AgentLog, FeedbackEntry, EvolutionSnapshot, AIUsage, AuditLog
"""

import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.database.connection import Base


def utcnow():
    return datetime.now(timezone.utc)


# ══════════════════════════════════════════════════════════════════════════════════
# 1. USER — Authentication & Identity
# ══════════════════════════════════════════════════════════════════════════════════
class User(Base):
    """User account entity."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(256))
    role = Column(String(32), default="candidate")  # candidate, recruiter, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    profile = relationship("CareerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    portfolio_repos = relationship("PortfolioRepo", back_populates="user", cascade="all, delete-orphan")
    next_best_actions = relationship("NextBestAction", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 2. CAREER PROFILE — Persistent Career Twin
# ══════════════════════════════════════════════════════════════════════════════════
class CareerProfile(Base):
    """Persistent Candidate Profile & Career Twin."""
    __tablename__ = "career_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    user_token = Column(String(64), index=True)  # Guest session support

    full_name = Column(String(256))
    location = Column(String(128))
    preferred_locations = Column(Text)  # JSON list
    work_authorization = Column(String(128))
    portfolio_url = Column(String(512))
    github_url = Column(String(512))
    linkedin_url = Column(String(512))

    current_role = Column(String(128))
    target_roles = Column(Text)  # JSON list e.g. ["Data Scientist", "ML Engineer"]
    experience_level = Column(String(64))  # entry, mid, senior, lead, executive
    total_years_experience = Column(Float, default=0.0)
    preferred_industries = Column(Text)  # JSON list
    employment_preferences = Column(Text)  # JSON e.g. {"remote": true, "hybrid": true}

    bio_summary = Column(Text)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    evidences = relationship("SkillEvidence", back_populates="profile", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "location": self.location,
            "preferred_locations": json.loads(self.preferred_locations or "[]"),
            "portfolio_url": self.portfolio_url,
            "github_url": self.github_url,
            "linkedin_url": self.linkedin_url,
            "current_role": self.current_role,
            "target_roles": json.loads(self.target_roles or "[]"),
            "experience_level": self.experience_level,
            "total_years_experience": self.total_years_experience,
            "preferred_industries": json.loads(self.preferred_industries or "[]"),
            "employment_preferences": json.loads(self.employment_preferences or "{}"),
            "bio_summary": self.bio_summary,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 3. SKILL EVIDENCE — Provenance Network
# ══════════════════════════════════════════════════════════════════════════════════
class SkillEvidence(Base):
    """Evidence graph associating candidate skill claims with verifiable sources."""
    __tablename__ = "skill_evidences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False)

    skill_name = Column(String(128), nullable=False)
    canonical_name = Column(String(128))
    category = Column(String(64))

    evidence_type = Column(String(64), nullable=False)  # "resume", "github_repo", "project", "certification", "experience"
    source_title = Column(String(256))  # e.g., "DeepVision AI Repo", "Senior Engineer at Google"
    source_url = Column(String(512))
    snippet = Column(Text)  # Context proof

    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    proficiency = Column(String(32), default="intermediate")  # beginner, intermediate, advanced, expert
    recency_years = Column(Float, default=0.0)  # How recent (years ago)

    created_at = Column(DateTime, default=utcnow)

    profile = relationship("CareerProfile", back_populates="evidences")

    def to_dict(self):
        return {
            "id": self.id,
            "skill": self.skill_name,
            "canonical": self.canonical_name,
            "category": self.category,
            "evidence_type": self.evidence_type,
            "source_title": self.source_title,
            "source_url": self.source_url,
            "snippet": self.snippet,
            "confidence": self.confidence,
            "proficiency": self.proficiency,
            "recency_years": self.recency_years,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 4. RESUME — Master Uploaded Document
# ══════════════════════════════════════════════════════════════════════════════════
class Resume(Base):
    """Uploaded master resume entity."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_token = Column(String(64), nullable=False, index=True)

    filename = Column(String(256), nullable=False)
    file_path = Column(String(512))
    raw_text = Column(Text)
    language = Column(String(16), default="en")
    embedding_vector = Column(Text)  # JSON float array (384-dim)
    uploaded_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
    snapshots = relationship("EvolutionSnapshot", back_populates="resume", cascade="all, delete-orphan")
    skill_mappings = relationship("SkillMapping", back_populates="resume", cascade="all, delete-orphan")
    bias_reports = relationship("BiasReport", back_populates="resume", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="resume", cascade="all, delete-orphan")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "language": self.language,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 5. RESUME VERSION — Tailored Job-Specific Resume
# ══════════════════════════════════════════════════════════════════════════════════
class ResumeVersion(Base):
    """Tailored resume versions generated for target roles/jobs."""
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    version_name = Column(String(256), nullable=False)  # e.g., "Data Scientist - Google"
    target_job_title = Column(String(256))
    target_company = Column(String(256))

    structured_content = Column(Text)  # JSON: {summary, experience, projects, education, skills}
    diff_from_master = Column(Text)  # JSON visual diff
    evidence_map = Column(Text)  # JSON: mapping generated bullets to evidence IDs
    unsupported_claims_flagged = Column(Text)  # JSON list of flagged unbacked requirements

    pdf_path = Column(String(512))
    docx_path = Column(String(512))

    created_at = Column(DateTime, default=utcnow)

    resume = relationship("Resume", back_populates="versions")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "version_name": self.version_name,
            "target_job_title": self.target_job_title,
            "target_company": self.target_company,
            "structured_content": json.loads(self.structured_content or "{}"),
            "diff_from_master": json.loads(self.diff_from_master or "{}"),
            "evidence_map": json.loads(self.evidence_map or "{}"),
            "unsupported_claims_flagged": json.loads(self.unsupported_claims_flagged or "[]"),
            "pdf_path": self.pdf_path,
            "docx_path": self.docx_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 6. ANALYSIS — Multi-Dimensional XAI Scoring Result
# ══════════════════════════════════════════════════════════════════════════════════
class Analysis(Base):
    """Full explainable analysis with multi-dimensional scoring and ATS simulation."""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ── Multi-Dimensional Scores ─────────────────────────────────────────────
    overall_score = Column(Float)  # Application Readiness Score
    resume_quality_score = Column(Float)  # Intrinsic document quality
    job_match_score = Column(Float)  # Job alignment %
    ats_parseability_score = Column(Float)  # Document ATS parseability
    evidence_strength_score = Column(Float)  # Evidence grounding strength
    recruiter_impact_score = Column(Float)  # Bullet impact & quantification

    # Legacy score aliases for backwards compatibility
    skills_match_score = Column(Float)
    experience_match_score = Column(Float)
    domain_relevance_score = Column(Float)
    project_complexity_score = Column(Float)
    format_score = Column(Float)

    confidence = Column(Float, default=0.85)

    # ── Extracted JSON Data ──────────────────────────────────────────────────
    skills_found = Column(Text)
    skills_missing = Column(Text)
    career_dna = Column(Text)
    ats_simulations = Column(Text)  # JSON: {Workday: 84, Greenhouse: 91, Lever: 88, Taleo: 79, iCIMS: 86, SuccessFactors: 82}
    experience_details = Column(Text)
    education_details = Column(Text)
    project_details = Column(Text)

    # ── Explanations ─────────────────────────────────────────────────────────
    score_explanation = Column(Text)
    recommendations = Column(Text)
    agent_summary = Column(Text)

    created_at = Column(DateTime, default=utcnow)

    resume = relationship("Resume", back_populates="analyses")
    job_matches = relationship("JobMatch", back_populates="analysis", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "overall_score": self.overall_score,
            "scores": {
                "resume_quality": self.resume_quality_score or self.format_score or 0,
                "job_match": self.job_match_score or self.skills_match_score or 0,
                "ats_parseability": self.ats_parseability_score or self.format_score or 0,
                "evidence_strength": self.evidence_strength_score or 75.0,
                "recruiter_impact": self.recruiter_impact_score or self.project_complexity_score or 0,
                "application_readiness": self.overall_score or 0,
            },
            "ats_simulations": json.loads(self.ats_simulations or "{}"),
            "confidence": self.confidence,
            "skills_found": json.loads(self.skills_found or "[]"),
            "skills_missing": json.loads(self.skills_missing or "[]"),
            "career_dna": json.loads(self.career_dna or "{}"),
            "score_explanation": self.score_explanation,
            "recommendations": json.loads(self.recommendations or "[]"),
            "agent_summary": json.loads(self.agent_summary or "{}"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 7. SKILL MAPPING — Skill Graph Node Mapping
# ══════════════════════════════════════════════════════════════════════════════════
class SkillMapping(Base):
    """Maps skills found in a resume to ontology graph nodes."""
    __tablename__ = "skill_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    skill_name = Column(String(128), nullable=False)
    canonical_name = Column(String(128))
    category = Column(String(64))
    parent_category = Column(String(64))
    confidence = Column(Float, default=1.0)
    context_snippet = Column(Text)
    inferred = Column(Boolean, default=False)

    resume = relationship("Resume", back_populates="skill_mappings")

    def to_dict(self):
        return {
            "skill": self.skill_name,
            "canonical": self.canonical_name,
            "category": self.category,
            "parent": self.parent_category,
            "confidence": self.confidence,
            "inferred": self.inferred,
            "context": self.context_snippet,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 8. JOB — Normalized Opportunity Posting
# ══════════════════════════════════════════════════════════════════════════════════
class Job(Base):
    """Normalized job vacancy entity ingested from job source adapters."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    company = Column(String(256), nullable=False)
    location = Column(String(256))
    employment_type = Column(String(64), default="Full-time")  # Full-time, Contract, Internship
    remote_type = Column(String(64), default="Hybrid")  # Remote, Hybrid, Onsite
    salary_range = Column(String(128))

    description_raw = Column(Text, nullable=False)
    source_adapter = Column(String(64))  # Greenhouse, Lever, RemoteOK, Adzuna, Manual
    external_url = Column(String(512))
    posting_date = Column(DateTime, default=utcnow)
    status = Column(String(32), default="active")  # active, expired, filled

    created_at = Column(DateTime, default=utcnow)

    # Relationships
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "employment_type": self.employment_type,
            "remote_type": self.remote_type,
            "salary_range": self.salary_range,
            "description_raw": self.description_raw[:500] if self.description_raw else "",
            "source_adapter": self.source_adapter,
            "external_url": self.external_url,
            "posting_date": self.posting_date.isoformat() if self.posting_date else None,
            "status": self.status,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 9. JOB REQUIREMENT — Granular Classified Requirement
# ══════════════════════════════════════════════════════════════════════════════════
class JobRequirement(Base):
    """Classified requirement for a job posting."""
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    requirement_text = Column(Text, nullable=False)
    importance_level = Column(String(32), nullable=False)  # "hard", "important", "preferred", "nice_to_have"
    canonical_skill = Column(String(128))
    category = Column(String(64))  # skill, experience, education, domain

    job = relationship("Job", back_populates="requirements")

    def to_dict(self):
        return {
            "id": self.id,
            "requirement_text": self.requirement_text,
            "importance_level": self.importance_level,
            "canonical_skill": self.canonical_skill,
            "category": self.category,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 10. JOB MATCH — Explainable Match Evaluation
# ══════════════════════════════════════════════════════════════════════════════════
class JobMatch(Base):
    """Matched job evaluation linking Analysis & Job."""
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    job_title = Column(String(256))
    company_type = Column(String(128))
    match_score = Column(Float)  # 0-100 overall semantic match

    # Granular dimension breakdown
    skills_match = Column(Float, default=0.0)
    experience_match = Column(Float, default=0.0)
    domain_match = Column(Float, default=0.0)
    evidence_strength = Column(Float, default=0.0)

    salary_range = Column(String(64))
    required_skills = Column(Text)  # JSON list
    missing_skills = Column(Text)  # JSON list
    recommendation = Column(String(64), default="APPLY AFTER TAILORING")  # APPLY NOW, APPLY AFTER TAILORING, UPSKILL FIRST
    match_explanation = Column(Text)  # JSON why you match / why you don't / risk factors
    job_url = Column(String(512))

    analysis = relationship("Analysis", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company_type": self.company_type,
            "match_score": round(self.match_score, 1) if self.match_score else 0,
            "dimension_scores": {
                "skills": self.skills_match,
                "experience": self.experience_match,
                "domain": self.domain_match,
                "evidence": self.evidence_strength,
            },
            "salary_range": self.salary_range,
            "required_skills": json.loads(self.required_skills or "[]"),
            "missing_skills": json.loads(self.missing_skills or "[]"),
            "recommendation": self.recommendation,
            "match_explanation": json.loads(self.match_explanation or "{}") if (self.match_explanation or "").startswith("{") else self.match_explanation,
            "job_url": self.job_url,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 11. APPLICATION — Job Search CRM Pipeline
# ══════════════════════════════════════════════════════════════════════════════════
class Application(Base):
    """Job application CRM pipeline tracking entity."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=True)

    company_name = Column(String(256), nullable=False)
    job_title = Column(String(256), nullable=False)
    job_url = Column(String(512))

    status = Column(String(64), nullable=False, default="Saved")
    # Pipeline stages: Discovered, Saved, Preparing, Applied, Assessment, Screen, Technical, Final, Offer, Rejected

    applied_date = Column(DateTime)
    salary_offered = Column(String(64))
    recruiter_contact = Column(String(256))
    notes = Column(Text)
    priority_score = Column(Float, default=75.0)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "job_title": self.job_title,
            "job_url": self.job_url,
            "status": self.status,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "salary_offered": self.salary_offered,
            "recruiter_contact": self.recruiter_contact,
            "notes": self.notes,
            "priority_score": self.priority_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 12. APPLICATION EVENT — CRM Timeline Audit
# ══════════════════════════════════════════════════════════════════════════════════
class ApplicationEvent(Base):
    """Audit trail of status changes and events for an application."""
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    from_status = Column(String(64))
    to_status = Column(String(64), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="events")

    def to_dict(self):
        return {
            "id": self.id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 13. INTERVIEW — Interview Intelligence Session
# ══════════════════════════════════════════════════════════════════════════════════
class Interview(Base):
    """Interview preparation and consistency evaluation session."""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    role_title = Column(String(256), nullable=False)
    company_name = Column(String(256))
    interview_type = Column(String(64), default="Technical Screen")  # Screen, Technical, Behavioral, System Design

    consistency_risk_score = Column(Float, default=0.0)  # 0 to 100 risk score
    risky_claims = Column(Text)  # JSON list of flagged resume claims lacking evidence
    prep_completed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=utcnow)

    application = relationship("Application", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "role_title": self.role_title,
            "company_name": self.company_name,
            "interview_type": self.interview_type,
            "consistency_risk_score": self.consistency_risk_score,
            "risky_claims": json.loads(self.risky_claims or "[]"),
            "prep_completed": self.prep_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 14. INTERVIEW QUESTION — Resume-Aware Question Bank
# ══════════════════════════════════════════════════════════════════════════════════
class InterviewQuestion(Base):
    """Granular interview question generated for candidate."""
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    category = Column(String(64), default="technical")  # technical, behavioral, project, consistency
    expected_evidence_ref = Column(String(256))
    risky_claim_flag = Column(Boolean, default=False)
    talking_points = Column(Text)  # JSON list
    user_answer = Column(Text)
    self_score = Column(Integer)  # 1 to 5

    interview = relationship("Interview", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "category": self.category,
            "expected_evidence_ref": self.expected_evidence_ref,
            "risky_claim_flag": self.risky_claim_flag,
            "talking_points": json.loads(self.talking_points or "[]"),
            "user_answer": self.user_answer,
            "self_score": self.self_score,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 15. PORTFOLIO REPO — GitHub & Code Quality Intelligence
# ══════════════════════════════════════════════════════════════════════════════════
class PortfolioRepo(Base):
    """Parsed GitHub repository portfolio intelligence entity."""
    __tablename__ = "portfolio_repos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    repo_name = Column(String(256), nullable=False)
    repo_url = Column(String(512), nullable=False)
    primary_language = Column(String(64))
    stars_count = Column(Integer, default=0)

    overall_depth_score = Column(Float, default=70.0)
    documentation_score = Column(Float, default=70.0)
    testing_score = Column(Float, default=60.0)
    deployment_score = Column(Float, default=50.0)
    code_quality_score = Column(Float, default=75.0)

    readme_summary = Column(Text)
    tech_stack = Column(Text)  # JSON list
    resume_bullet_suggestions = Column(Text)  # JSON list
    recommendations = Column(Text)  # JSON list

    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="portfolio_repos")

    def to_dict(self):
        return {
            "id": self.id,
            "repo_name": self.repo_name,
            "repo_url": self.repo_url,
            "primary_language": self.primary_language,
            "stars_count": self.stars_count,
            "scores": {
                "overall_depth": self.overall_depth_score,
                "documentation": self.documentation_score,
                "testing": self.testing_score,
                "deployment": self.deployment_score,
                "code_quality": self.code_quality_score,
            },
            "readme_summary": self.readme_summary,
            "tech_stack": json.loads(self.tech_stack or "[]"),
            "resume_bullet_suggestions": json.loads(self.resume_bullet_suggestions or "[]"),
            "recommendations": json.loads(self.recommendations or "[]"),
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 16. CAREER GOAL — Trajectory Modeling
# ══════════════════════════════════════════════════════════════════════════════════
class CareerGoal(Base):
    """Candidate long-term career milestone target."""
    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    target_role = Column(String(256), nullable=False)
    timeframe_months = Column(Integer, default=12)
    current_readiness = Column(Float, default=65.0)
    required_skill_gaps = Column(Text)  # JSON list
    learning_plan = Column(Text)  # JSON roadmap

    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "target_role": self.target_role,
            "timeframe_months": self.timeframe_months,
            "current_readiness": self.current_readiness,
            "required_skill_gaps": json.loads(self.required_skill_gaps or "[]"),
            "learning_plan": json.loads(self.learning_plan or "[]"),
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 17. NEXT BEST ACTION — Candidates Priority Queue
# ══════════════════════════════════════════════════════════════════════════════════
class NextBestAction(Base):
    """Prioritized candidate recommendation in the Command Center queue."""
    __tablename__ = "next_best_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    action_type = Column(String(64), nullable=False)  # "APPLY_JOB", "TAILOR_RESUME", "LEARN_SKILL", "PREPARE_INTERVIEW", "IMPROVE_PORTFOLIO"
    title = Column(String(256), nullable=False)
    description = Column(Text)
    priority_score = Column(Float, default=80.0)  # Higher score = shown first
    effort_minutes = Column(Integer, default=15)
    expected_impact = Column(String(32), default="HIGH")  # HIGH, MEDIUM, LOW
    target_link = Column(String(256))
    status = Column(String(32), default="pending")  # pending, completed, dismissed

    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="next_best_actions")

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "title": self.title,
            "description": self.description,
            "priority_score": self.priority_score,
            "effort_minutes": self.effort_minutes,
            "expected_impact": self.expected_impact,
            "target_link": self.target_link,
            "status": self.status,
        }


# ══════════════════════════════════════════════════════════════════════════════════
# 18. RECRUITER DECISION, AGENT LOG, FEEDBACK, EVOLUTION (Retained & Enhanced)
# ══════════════════════════════════════════════════════════════════════════════════
class BiasReport(Base):
    """Bias detection analysis."""
    __tablename__ = "bias_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)

    gender_bias_score = Column(Float, default=0)
    institution_bias_score = Column(Float, default=0)
    keyword_bias_score = Column(Float, default=0)
    overall_bias_risk = Column(Float, default=0)

    findings = Column(Text)
    equivalent_skills = Column(Text)
    anonymized_score_diff = Column(Float)
    recommendations = Column(Text)

    created_at = Column(DateTime, default=utcnow)

    resume = relationship("Resume", back_populates="bias_reports")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "bias_scores": {
                "gender": self.gender_bias_score,
                "institution": self.institution_bias_score,
                "keyword": self.keyword_bias_score,
                "overall_risk": self.overall_bias_risk,
            },
            "findings": json.loads(self.findings or "[]"),
            "equivalent_skills": json.loads(self.equivalent_skills or "[]"),
            "anonymized_score_diff": self.anonymized_score_diff,
            "recommendations": json.loads(self.recommendations or "[]"),
        }


class RecruiterDecision(Base):
    """Recruiter decision tracking for pattern learning."""
    __tablename__ = "recruiter_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_title = Column(String(256))
    decision = Column(String(16), nullable=False)
    reason = Column(Text)
    recruiter_id = Column(String(64))
    skills_valued = Column(Text)
    decided_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "job_title": self.job_title,
            "decision": self.decision,
            "reason": self.reason,
            "skills_valued": json.loads(self.skills_valued or "[]"),
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }


class AgentLog(Base):
    """Logs agent execution steps."""
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    pipeline_id = Column(String(64), nullable=False)

    agent_name = Column(String(64), nullable=False)
    status = Column(String(16))
    input_summary = Column(Text)
    output_summary = Column(Text)
    duration_ms = Column(Integer)
    error = Column(Text)
    created_at = Column(DateTime, default=utcnow)

    resume = relationship("Resume", back_populates="agent_logs")

    def to_dict(self):
        return {
            "agent": self.agent_name,
            "status": self.status,
            "output": self.output_summary,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


class FeedbackEntry(Base):
    """Feedback entry for continuous model learning."""
    __tablename__ = "feedback_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    feedback_type = Column(String(32))
    original_value = Column(Text)
    corrected_value = Column(Text)
    comment = Column(Text)
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.feedback_type,
            "original": self.original_value,
            "corrected": self.corrected_value,
            "comment": self.comment,
            "applied": self.applied,
        }


class EvolutionSnapshot(Base):
    """Resume version score snapshot."""
    __tablename__ = "evolution_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    overall_score = Column(Float)
    skills_match_score = Column(Float)
    experience_score = Column(Float)
    delta = Column(Float)
    note = Column(String(256))
    snapshot_at = Column(DateTime, default=utcnow)

    resume = relationship("Resume", back_populates="snapshots")

    def to_dict(self):
        return {
            "version": self.version,
            "overall_score": self.overall_score,
            "skills_match_score": self.skills_match_score,
            "experience_score": self.experience_score,
            "delta": self.delta,
            "note": self.note,
            "snapshot_at": self.snapshot_at.isoformat() if self.snapshot_at else None,
        }


class InterviewSession(Base):
    """Legacy AI Interview Prep Coach sessions."""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    role = Column(String(256))
    questions = Column(Text)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "role": self.role,
            "questions": json.loads(self.questions or "[]"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ── Indexes ──────────────────────────────────────────────────────────────────────
Index("idx_user_email", User.email)
Index("idx_career_profile_user", CareerProfile.user_id)
Index("idx_skill_evidence_profile", SkillEvidence.profile_id)
Index("idx_resume_version_resume", ResumeVersion.resume_id)
Index("idx_job_company_title", Job.company, Job.title)
Index("idx_job_requirement_job", JobRequirement.job_id)
Index("idx_application_user_status", Application.user_id, Application.status)
Index("idx_next_best_action_user", NextBestAction.user_id, NextBestAction.status)
