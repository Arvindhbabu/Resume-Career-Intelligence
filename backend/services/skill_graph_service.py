"""
ResumeIQ — Skill Graph Service
High-level service wrapping SkillGraphEngine with evidence verification & prerequisite mapping.
"""

import logging
from typing import List, Dict, Any, Optional
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class SkillGraphService:
    """Service providing skill resolution, evidence strength scoring, and prerequisite mapping."""

    def resolve_skill_with_evidence(self, skill_name: str, evidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Resolve a skill and calculate its evidence score and recency.
        """
        resolved = skill_graph.resolve_skill(skill_name)
        canonical = resolved["canonical"] if resolved else skill_name.lower()

        matching_evidences = [
            e for e in evidences
            if (e.get("canonical") or "").lower() == canonical or (e.get("skill") or "").lower() == canonical
        ]

        if not matching_evidences:
            return {
                "skill": skill_name,
                "canonical": canonical,
                "category": resolved["category"] if resolved else "General",
                "evidence_supported": False,
                "evidence_score": 0.0,
                "status": "UNSUPPORTED",
                "evidences": [],
            }

        score = sum(e.get("confidence", 1.0) for e in matching_evidences) / len(matching_evidences)
        return {
            "skill": skill_name,
            "canonical": canonical,
            "category": resolved["category"] if resolved else "General",
            "evidence_supported": True,
            "evidence_score": round(min(1.0, score), 2),
            "status": "VERIFIED",
            "evidences": matching_evidences,
        }

    def evaluate_skills_against_evidence(self, required_skills: List[str], evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check required job skills against candidate evidence network.
        Returns verified skills and missing evidence alerts.
        """
        verified = []
        unsupported = []

        for skill in required_skills:
            res = self.resolve_skill_with_evidence(skill, evidence_list)
            if res["evidence_supported"]:
                verified.append(res)
            else:
                unsupported.append(res)

        total = len(required_skills) if required_skills else 1
        evidence_coverage = round((len(verified) / total) * 100, 1)

        return {
            "evidence_coverage_percent": evidence_coverage,
            "verified_skills_count": len(verified),
            "unsupported_skills_count": len(unsupported),
            "verified_skills": verified,
            "unsupported_skills": unsupported,
        }

    def get_prerequisites(self, skill_name: str) -> List[str]:
        """Infer prerequisite foundational skills for a given technical skill."""
        prereqs = {
            "fastapi": ["python", "rest api", "pydantic"],
            "pytorch": ["python", "deep learning", "tensors", "numpy"],
            "tensorflow": ["python", "deep learning", "neural networks"],
            "kubernetes": ["docker", "containerization", "devops"],
            "spark": ["scala", "python", "hadoop", "sql"],
            "react": ["javascript", "html", "css"],
            "next.js": ["react", "javascript", "typescript"],
            "dbt": ["sql", "data warehouse", "etl"],
        }
        skill_lower = skill_name.lower()
        return prereqs.get(skill_lower, skill_graph._infer_parent_skills(skill_lower))


skill_graph_service = SkillGraphService()
