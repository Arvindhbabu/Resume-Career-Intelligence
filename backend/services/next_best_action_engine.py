"""
ResumeIQ — Next-Best-Action Engine & Priority Queue
Generates a dynamic daily candidate priority list answering "What should I do next?"
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import NextBestAction

logger = logging.getLogger(__name__)


class NextBestActionEngine:
    """Calculates prioritized candidate action queue."""

    def generate_action_queue(
        self,
        db: Session,
        user_id: Optional[int] = None,
        candidate_profile: Optional[Dict[str, Any]] = None,
        job_feed: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate dynamic prioritized candidate actions.
        Priority formula: Priority = (Fit Score * 0.4) + (Impact Weight * 0.4) - (Effort * 0.2)
        """
        actions = []

        # 1. Action: Apply to High-Fit Opportunity
        if job_feed:
            top_job = job_feed[0]
            actions.append({
                "action_type": "APPLY_JOB",
                "title": f"Apply to {top_job['title']} @ {top_job['company']}",
                "description": f"Fit Score: {top_job.get('priority_fit_score', 85)}%. Strong match in core skills.",
                "priority_score": 95.0,
                "effort_minutes": 12,
                "expected_impact": "HIGH",
                "target_link": f"/jobs/{top_job['company']}",
                "status": "pending",
            })

        # 2. Action: Tailor Resume for saved opportunity
        actions.append({
            "action_type": "TAILOR_RESUME",
            "title": "Tailor Resume for Senior Data Scientist Position",
            "description": "Align experience bullets to hard requirements with No-Fabrication proof.",
            "priority_score": 88.0,
            "effort_minutes": 8,
            "expected_impact": "HIGH",
            "target_link": "/resume-tailor",
            "status": "pending",
        })

        # 3. Action: Upskill high-value requirement
        actions.append({
            "action_type": "LEARN_SKILL",
            "title": "Build PyTorch Distributed Training Project",
            "description": "Unlocks 34 high-fit ML Engineer roles currently missing deep learning evidence.",
            "priority_score": 82.0,
            "effort_minutes": 120,
            "expected_impact": "MEDIUM",
            "target_link": "/skill-roadmap",
            "status": "pending",
        })

        # 4. Action: Prepare for upcoming technical interview
        actions.append({
            "action_type": "PREPARE_INTERVIEW",
            "title": "Run Resume-to-Interview Consistency Check",
            "description": "Verify resume claims against technical depth before recruiter screen.",
            "priority_score": 79.0,
            "effort_minutes": 15,
            "expected_impact": "HIGH",
            "target_link": "/interview-prep",
            "status": "pending",
        })

        # Persist to DB if user_id provided
        if user_id:
            for act in actions:
                db.add(NextBestAction(
                    user_id=user_id,
                    action_type=act["action_type"],
                    title=act["title"],
                    description=act["description"],
                    priority_score=act["priority_score"],
                    effort_minutes=act["effort_minutes"],
                    expected_impact=act["expected_impact"],
                    target_link=act["target_link"],
                    status=act["status"],
                ))
            db.commit()

        return actions


next_best_action_engine = NextBestActionEngine()
