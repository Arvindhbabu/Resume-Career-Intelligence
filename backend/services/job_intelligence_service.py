"""
ResumeIQ — Job Intelligence Service
Parses raw job descriptions, extracts structured requirements, and classifies importance levels.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import Job, JobRequirement
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class JobIntelligenceService:
    """Service for job ingestion, parsing, and requirement classification."""

    def parse_and_classify_jd(self, raw_jd: str, title: str = "Target Role", company: str = "Target Company") -> Dict[str, Any]:
        """
        Parse raw job description into structured requirements categorized by importance:
        - Hard requirements (must have, minimum years, required degree)
        - Important requirements (core tech stack, essential responsibilities)
        - Preferred requirements (nice to have, bonus certifications)
        """
        jd_lower = raw_jd.lower()
        extracted_skills = skill_graph.extract_skills_semantic(raw_jd)

        # Sentence segmentation
        sentences = [s.strip() for s in re.split(r'[\.\n\•\-\*]', raw_jd) if len(s.strip()) > 10]

        hard_reqs = []
        important_reqs = []
        preferred_reqs = []

        hard_keywords = ["must have", "required", "minimum", "at least", "mandatory", "essential", "proven experience"]
        preferred_keywords = ["preferred", "nice to have", "plus", "bonus", "ideal", "desirable"]

        for s in sentences:
            s_lower = s.lower()
            if any(hk in s_lower for hk in hard_keywords):
                hard_reqs.append(s)
            elif any(pk in s_lower for pk in preferred_keywords):
                preferred_reqs.append(s)
            else:
                important_reqs.append(s)

        # Categorize extracted skills
        hard_skills = [s["skill"] for s in extracted_skills[:5]]
        important_skills = [s["skill"] for s in extracted_skills[5:15]]
        preferred_skills = [s["skill"] for s in extracted_skills[15:]]

        # Extract Experience Level & Seniority
        years_match = re.search(r'(\d+)\+?\s*years', jd_lower)
        years_required = float(years_match.group(1)) if years_match else 2.0

        seniority = "Mid-Level"
        if "senior" in jd_lower or "lead" in jd_lower or years_required >= 5:
            seniority = "Senior"
        elif "junior" in jd_lower or "entry" in jd_lower or years_required <= 1:
            seniority = "Entry-Level"

        return {
            "title": title,
            "company": company,
            "seniority": seniority,
            "years_required": years_required,
            "skills": [s["skill"] for s in extracted_skills],
            "hard_skills": hard_skills,
            "important_skills": important_skills,
            "preferred_skills": preferred_skills,
            "hard_requirements": hard_reqs[:5],
            "important_requirements": important_reqs[:10],
            "preferred_requirements": preferred_reqs[:5],
        }

    def ingest_job(self, db: Session, raw_jd: str, title: str, company: str, source_adapter: str = "Manual") -> Job:
        """Parse and persist job posting entity."""
        parsed = self.parse_and_classify_jd(raw_jd, title, company)

        job = Job(
            title=title,
            company=company,
            description_raw=raw_jd,
            source_adapter=source_adapter,
        )
        db.add(job)
        db.flush()

        for req in parsed["hard_requirements"]:
            db.add(JobRequirement(job_id=job.id, requirement_text=req, importance_level="hard", category="general"))

        for req in parsed["important_requirements"]:
            db.add(JobRequirement(job_id=job.id, requirement_text=req, importance_level="important", category="general"))

        for req in parsed["preferred_requirements"]:
            db.add(JobRequirement(job_id=job.id, requirement_text=req, importance_level="preferred", category="general"))

        db.commit()
        db.refresh(job)
        return job


job_intelligence_service = JobIntelligenceService()
