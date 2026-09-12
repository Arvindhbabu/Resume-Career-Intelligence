"""
ResumeIQ — Career Profile Service
Manages persistent candidate profile, career twin settings, and evidence graph nodes.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.database.models import User, CareerProfile, SkillEvidence, CareerGoal

logger = logging.getLogger(__name__)


class CareerProfileService:
    """Service for candidate identity, preferences, and skill evidence graph."""

    def get_or_create_profile(self, db: Session, user_id: Optional[int] = None, user_token: Optional[str] = None) -> CareerProfile:
        """Fetch or initialize a candidate career profile."""
        profile = None
        if user_id:
            profile = db.query(CareerProfile).filter_by(user_id=user_id).first()
        elif user_token:
            profile = db.query(CareerProfile).filter_by(user_token=user_token).first()

        if not profile:
            profile = CareerProfile(
                user_id=user_id,
                user_token=user_token or f"guest-{user_id or 0}",
                target_roles=json.dumps(["Software Engineer"]),
                preferred_locations=json.dumps(["Remote"]),
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return profile

    def update_profile(self, db: Session, profile_id: int, updates: Dict[str, Any]) -> CareerProfile:
        """Update profile fields with JSON handling."""
        profile = db.query(CareerProfile).filter_by(id=profile_id).first()
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        json_fields = ["preferred_locations", "target_roles", "preferred_industries", "employment_preferences"]
        for key, value in updates.items():
            if hasattr(profile, key):
                if key in json_fields and isinstance(value, (list, dict)):
                    setattr(profile, key, json.dumps(value))
                else:
                    setattr(profile, key, value)

        db.commit()
        db.refresh(profile)
        return profile

    def add_skill_evidence(
        self,
        db: Session,
        profile_id: int,
        skill_name: str,
        evidence_type: str,
        source_title: str,
        source_url: Optional[str] = None,
        snippet: Optional[str] = None,
        confidence: float = 1.0,
        proficiency: str = "intermediate",
        recency_years: float = 0.0,
    ) -> SkillEvidence:
        """Add an evidence node to candidate's skill graph."""
        from backend.ai.skill_graph import skill_graph
        resolved = skill_graph.resolve_skill(skill_name)
        canonical = resolved["canonical"] if resolved else skill_name.lower()
        category = resolved["category"] if resolved else "General"

        evidence = SkillEvidence(
            profile_id=profile_id,
            skill_name=skill_name,
            canonical_name=canonical,
            category=category,
            evidence_type=evidence_type,
            source_title=source_title,
            source_url=source_url,
            snippet=snippet,
            confidence=confidence,
            proficiency=proficiency,
            recency_years=recency_years,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    def get_evidence_graph(self, db: Session, profile_id: int) -> Dict[str, Any]:
        """Build structured evidence graph tree (skill -> evidences -> confidence -> proficiency)."""
        evidences = db.query(SkillEvidence).filter_by(profile_id=profile_id).all()
        
        graph: Dict[str, Any] = {}
        for ev in evidences:
            skill_key = ev.canonical_name or ev.skill_name.lower()
            if skill_key not in graph:
                graph[skill_key] = {
                    "skill": ev.skill_name,
                    "canonical": skill_key,
                    "category": ev.category,
                    "evidences": [],
                    "overall_confidence": 0.0,
                    "highest_proficiency": "beginner",
                    "evidence_count": 0,
                }
            
            graph[skill_key]["evidences"].append(ev.to_dict())
            graph[skill_key]["evidence_count"] += 1

        # Calculate aggregated confidence and proficiency
        proficiency_ranks = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        rank_to_name = {1: "beginner", 2: "intermediate", 3: "advanced", 4: "expert"}

        for skill_key, data in graph.items():
            conf_sum = sum(e["confidence"] for e in data["evidences"])
            data["overall_confidence"] = min(1.0, round(conf_sum / max(1, len(data["evidences"])), 2))
            
            max_rank = max(proficiency_ranks.get(e.get("proficiency", "intermediate"), 2) for e in data["evidences"])
            data["highest_proficiency"] = rank_to_name.get(max_rank, "intermediate")

        return {
            "profile_id": profile_id,
            "total_skills": len(graph),
            "skills": graph,
        }


career_profile_service = CareerProfileService()
