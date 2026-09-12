"""
ResumeIQ — Resume Intelligence Service
Handles multi-stage resume parsing, section extraction, metrics/achievement detection, and versioning.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.parser.pdf_parser import parser as pdf_parser
from backend.services.ats_simulation_engine import ats_simulation_engine
from backend.database.models import Resume, Analysis, SkillMapping, ResumeVersion, EvolutionSnapshot

logger = logging.getLogger(__name__)


class ResumeIntelligenceService:
    """High-fidelity resume processing pipeline."""

    def process_and_analyze_resume(
        self,
        db: Session,
        raw_text: str,
        filename: str,
        user_id: Optional[int] = None,
        user_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute full high-fidelity resume processing pipeline:
        File Parsing -> Section Detection -> Entity/Skill Extraction -> Multi-Dim ATS Scoring -> Version Snapshot.
        """
        # 1. Parse structured resume data
        parsed = pdf_parser.parse_text(raw_text, filename)

        # 2. Extract metrics & achievements
        achievements = self.extract_quantified_achievements(raw_text)
        parsed["achievements"] = achievements

        # 3. Compute multi-dimensional ATS scores & platform simulations
        scores = ats_simulation_engine.calculate_multi_dimensional_scores(parsed)
        simulations = ats_simulation_engine.simulate_platform_profiles(parsed, scores)

        # 4. Save to DB
        resume_record = Resume(
            user_id=user_id,
            user_token=user_token or "guest-session",
            filename=filename,
            raw_text=raw_text[:50000],
            language=parsed.get("language", "en"),
        )
        db.add(resume_record)
        db.flush()

        analysis_record = Analysis(
            resume_id=resume_record.id,
            user_id=user_id,
            overall_score=scores["application_readiness"],
            resume_quality_score=scores["resume_quality"],
            job_match_score=scores["job_match"],
            ats_parseability_score=scores["ats_parseability"],
            evidence_strength_score=scores["evidence_strength"],
            recruiter_impact_score=scores["recruiter_impact"],
            skills_match_score=scores["job_match"],
            experience_match_score=75.0,
            domain_relevance_score=80.0,
            project_complexity_score=scores["recruiter_impact"],
            format_score=scores["ats_parseability"],
            confidence=0.90,
            skills_found=str(parsed.get("skills", [])),
            skills_missing="[]",
            career_dna=str({}),
            ats_simulations=str(simulations),
            score_explanation=f"Resume quality is {scores['resume_quality']}% with ATS parseability of {scores['ats_parseability']}%.",
            recommendations=str(["Add quantified metrics to bullet points", "Include targeted keywords for target role"]),
        )
        db.add(analysis_record)
        db.flush()

        # Skill Mappings
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

        # Initial Evolution Snapshot
        snapshot = EvolutionSnapshot(
            resume_id=resume_record.id,
            version=1,
            overall_score=scores["application_readiness"],
            skills_match_score=scores["job_match"],
            experience_score=75.0,
            delta=0.0,
            note="Master Resume Baseline",
        )
        db.add(snapshot)
        db.commit()

        return {
            "resume_id": resume_record.id,
            "analysis_id": analysis_record.id,
            "parsed": parsed,
            "scores": scores,
            "ats_simulations": simulations,
            "achievements": achievements,
        }

    def extract_quantified_achievements(self, text: str) -> List[str]:
        """Extract bullet points containing quantitative metric proof."""
        bullets = []
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Match percentages, dollar values, multipliers, scale indicators
            if re.search(r'\d+%', line_str) or re.search(r'\$\d+', line_str) or re.search(r'\b\d+x\b', line_str, re.I):
                bullets.append(line_str)
        return bullets[:10]


resume_intelligence_service = ResumeIntelligenceService()
