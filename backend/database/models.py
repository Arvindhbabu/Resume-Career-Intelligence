"""
ResumeIQ — Database Models
Covers: Resume, Analysis, JobMatch, EvolutionSnapshot, InterviewSession
"""

from datetime import datetime
from backend.app import db


class Resume(db.Model):
    """Stores uploaded resume metadata and raw extracted text."""
    __tablename__ = "resumes"

    id          = db.Column(db.Integer, primary_key=True)
    user_token  = db.Column(db.String(64), nullable=False, index=True)   # session / user id
    filename    = db.Column(db.String(256), nullable=False)
    file_path   = db.Column(db.String(512))
    raw_text    = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    analyses    = db.relationship("Analysis", backref="resume", lazy="dynamic",
                                  cascade="all, delete-orphan")
    snapshots   = db.relationship("EvolutionSnapshot", backref="resume", lazy="dynamic",
                                  cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "uploaded_at": self.uploaded_at.isoformat(),
            "version_count": self.snapshots.count(),
        }


class Analysis(db.Model):
    """Full analysis result for one resume version."""
    __tablename__ = "analyses"

    id              = db.Column(db.Integer, primary_key=True)
    resume_id       = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    ats_score       = db.Column(db.Float)            # 0–100
    skill_score     = db.Column(db.Float)
    format_score    = db.Column(db.Float)
    experience_score= db.Column(db.Float)
    overall_score   = db.Column(db.Float)

    # Parsed fields (JSON strings)
    skills_found    = db.Column(db.Text)             # JSON list
    skills_missing  = db.Column(db.Text)             # JSON list
    career_dna      = db.Column(db.Text)             # JSON dict  ← Career DNA Map
    recommendations = db.Column(db.Text)             # JSON list of suggestion strings
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    job_matches     = db.relationship("JobMatch", backref="analysis", lazy="dynamic",
                                      cascade="all, delete-orphan")

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "ats_score": self.ats_score,
            "skill_score": self.skill_score,
            "format_score": self.format_score,
            "experience_score": self.experience_score,
            "overall_score": self.overall_score,
            "skills_found": json.loads(self.skills_found or "[]"),
            "skills_missing": json.loads(self.skills_missing or "[]"),
            "career_dna": json.loads(self.career_dna or "{}"),
            "recommendations": json.loads(self.recommendations or "[]"),
            "created_at": self.created_at.isoformat(),
        }


class JobMatch(db.Model):
    """Top-N job recommendations linked to an analysis."""
    __tablename__ = "job_matches"

    id              = db.Column(db.Integer, primary_key=True)
    analysis_id     = db.Column(db.Integer, db.ForeignKey("analyses.id"), nullable=False)
    job_title       = db.Column(db.String(256))
    company_type    = db.Column(db.String(128))      # e.g. "Startup", "MNC"
    match_score     = db.Column(db.Float)            # 0–100 cosine similarity %
    salary_range    = db.Column(db.String(64))
    required_skills = db.Column(db.Text)             # JSON list
    missing_skills  = db.Column(db.Text)             # JSON list (gap)
    job_url         = db.Column(db.String(512))      # Optional external link

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "job_title": self.job_title,
            "company_type": self.company_type,
            "match_score": round(self.match_score, 1),
            "salary_range": self.salary_range,
            "required_skills": json.loads(self.required_skills or "[]"),
            "missing_skills": json.loads(self.missing_skills or "[]"),
            "job_url": self.job_url,
        }


class EvolutionSnapshot(db.Model):
    """
    Resume Evolution Tracker — stores a score snapshot each time
    the user re-uploads an improved version of their resume.
    """
    __tablename__ = "evolution_snapshots"

    id            = db.Column(db.Integer, primary_key=True)
    resume_id     = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    version       = db.Column(db.Integer, nullable=False, default=1)
    overall_score = db.Column(db.Float)
    ats_score     = db.Column(db.Float)
    skill_score   = db.Column(db.Float)
    delta         = db.Column(db.Float)              # Score change vs previous version
    note          = db.Column(db.String(256))        # User label e.g. "Added AWS certs"
    snapshot_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "version": self.version,
            "overall_score": self.overall_score,
            "ats_score": self.ats_score,
            "skill_score": self.skill_score,
            "delta": self.delta,
            "note": self.note,
            "snapshot_at": self.snapshot_at.isoformat(),
        }


class InterviewSession(db.Model):
    """AI Interview Prep Coach — stores generated Q&A for a resume."""
    __tablename__ = "interview_sessions"

    id          = db.Column(db.Integer, primary_key=True)
    resume_id   = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    role        = db.Column(db.String(256))          # Target role for questions
    questions   = db.Column(db.Text)                 # JSON list of {q, hint, difficulty}
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "role": self.role,
            "questions": json.loads(self.questions or "[]"),
            "created_at": self.created_at.isoformat(),
        }
