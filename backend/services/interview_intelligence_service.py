"""
ResumeIQ — Interview Intelligence & Resume-to-Interview Consistency Engine
Generates resume-aware technical question packs and checks for risky/unsupported resume claims.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import Interview, InterviewQuestion, Resume, Analysis
from backend.services.skill_graph_service import skill_graph_service

logger = logging.getLogger(__name__)


class InterviewIntelligenceService:
    """Service generating interview packs and performing consistency risk checks."""

    def analyze_resume_consistency(
        self,
        resume_claims: List[str],
        candidate_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect risky resume claims where claimed expertise exceeds documented proof.
        Example: Resume says "Implemented distributed multi-node LLM training",
        but evidence only proves basic single-GPU PyTorch fine-tuning.
        """
        risky_claims = []
        verified_claims = []

        complex_keywords = ["distributed", "multi-node", "petabyte", "million rps", "high availability", "zero downtime"]

        for claim in resume_claims:
            claim_lower = claim.lower()
            is_complex = any(ck in claim_lower for ck in complex_keywords)

            # Check evidence grounding
            matching_ev = [
                e for e in candidate_evidence
                if (e.get("snippet") or "").lower() in claim_lower or (e.get("skill") or "").lower() in claim_lower
            ]

            if is_complex and not matching_ev:
                risky_claims.append({
                    "claim": claim,
                    "risk_level": "HIGH INTERVIEW RISK",
                    "reason": "Claim involves complex architectural scale, but no evidence node backs this specific claim.",
                    "recommended_prep_question": f"Can you explain the exact distributed architecture and node synchronization protocol used when you {claim}?",
                })
            else:
                verified_claims.append(claim)

        risk_score = round((len(risky_claims) / max(1, len(resume_claims))) * 100, 1)

        return {
            "consistency_risk_score": risk_score,
            "risky_claims_count": len(risky_claims),
            "verified_claims_count": len(verified_claims),
            "risky_claims": risky_claims,
            "verified_claims": verified_claims,
        }

    def generate_interview_pack(
        self,
        db: Session,
        role_title: str,
        company_name: str,
        resume_text: str,
        skills: List[str],
        evidence_list: List[Dict[str, Any]] = []
    ) -> Dict[str, Any]:
        """Generate comprehensive 3-category interview preparation pack."""
        lines = [l.strip() for l in resume_text.splitlines() if len(l.strip()) > 15]

        # Consistency analysis
        consistency_res = self.analyze_resume_consistency(lines[:5], evidence_list)

        questions = []

        # 1. Technical Questions
        for s in skills[:3]:
            prereqs = skill_graph_service.get_prerequisites(s)
            questions.append({
                "category": "technical",
                "question_text": f"How do you handle performance optimization and trade-offs when working with {s.title()}?",
                "expected_evidence_ref": s,
                "risky_claim_flag": False,
                "talking_points": [f"Explain core {s} concepts", f"Mention prerequisites: {', '.join(prereqs[:2])}", "Give concrete production metric"],
            })

        # 2. Project Deep-Dive Questions
        questions.append({
            "category": "project",
            "question_text": f"Walk me through the technical architecture of your primary project for {role_title}. What were the key bottlenecks?",
            "expected_evidence_ref": "Projects",
            "risky_claim_flag": False,
            "talking_points": ["State overall goal & architecture", "Explain trade-offs made", "Quantify final result"],
        })

        # 3. Consistency / Defense Questions for flagged claims
        for rc in consistency_res["risky_claims"]:
            questions.append({
                "category": "consistency",
                "question_text": rc["recommended_prep_question"],
                "expected_evidence_ref": rc["claim"][:30],
                "risky_claim_flag": True,
                "talking_points": ["Acknowledge exact scope", "Explain tools used", "Avoid exaggerating scale"],
            })

        # Persist Interview Session
        interview = Interview(
            role_title=role_title,
            company_name=company_name,
            interview_type="Technical Screen",
            consistency_risk_score=consistency_res["consistency_risk_score"],
            risky_claims=json.dumps(consistency_res["risky_claims"]),
            prep_completed=False,
        )
        db.add(interview)
        db.flush()

        for q in questions:
            db.add(InterviewQuestion(
                interview_id=interview.id,
                question_text=q["question_text"],
                category=q["category"],
                expected_evidence_ref=q["expected_evidence_ref"],
                risky_claim_flag=q["risky_claim_flag"],
                talking_points=json.dumps(q["talking_points"]),
            ))

        db.commit()
        db.refresh(interview)

        return {
            "interview_id": interview.id,
            "role_title": role_title,
            "company_name": company_name,
            "consistency_analysis": consistency_res,
            "questions": questions,
        }


interview_intelligence_service = InterviewIntelligenceService()
