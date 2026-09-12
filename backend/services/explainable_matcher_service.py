"""
ResumeIQ — Explainable Matcher Service
Computes deterministic fit scores and transparent evidence-backed explanations.
"""

import logging
from typing import Dict, Any, List
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class ExplainableMatcherService:
    """Deterministic explainable job matching engine."""

    def match_resume_to_job(
        self,
        candidate_skills: List[str],
        candidate_experience_years: float,
        job_parsed: Dict[str, Any],
        evidence_graph: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Compute transparent fit breakdown and actionable recommendation.
        Scored using deterministic calculations (No LLM score hallucinations).
        """
        candidate_set = set(s.lower() for s in candidate_skills)
        hard_skills = set(s.lower() for s in job_parsed.get("hard_skills", []))
        important_skills = set(s.lower() for s in job_parsed.get("important_skills", []))
        preferred_skills = set(s.lower() for s in job_parsed.get("preferred_skills", []))

        all_job_skills = hard_skills | important_skills | preferred_skills
        if not all_job_skills:
            all_job_skills = set(s.lower() for s in job_parsed.get("skills", ["python"]))

        # 1. Hard Skills Match %
        hard_match_count = len(hard_skills & candidate_set)
        hard_match_score = (hard_match_count / max(1, len(hard_skills))) * 100 if hard_skills else 100.0

        # 2. Overall Skills Match %
        matched_skills = candidate_set & all_job_skills
        missing_skills = list(all_job_skills - candidate_set)
        skills_match_score = (len(matched_skills) / max(1, len(all_job_skills))) * 100

        # 3. Experience Alignment %
        required_years = job_parsed.get("years_required", 2.0)
        if candidate_experience_years >= required_years:
            exp_match_score = 100.0
        else:
            exp_match_score = (candidate_experience_years / max(1.0, required_years)) * 100

        # 4. Overall Weighted Score
        overall_match = round(
            (hard_match_score * 0.40) +
            (skills_match_score * 0.35) +
            (exp_match_score * 0.25),
            1
        )

        # 5. Recommendation Logic
        if overall_match >= 85.0 and hard_match_score >= 80.0:
            recommendation = "APPLY NOW"
            rec_reason = "Strong alignment on hard requirements and tech stack. High probability of screen success."
        elif overall_match >= 65.0:
            recommendation = "APPLY AFTER TAILORING"
            rec_reason = "Good core skills coverage. Tailor resume to emphasize matching experience and missing keywords."
        elif overall_match >= 45.0:
            recommendation = "UPSKILL FIRST"
            rec_reason = "Moderate gap in hard requirements. Complete target projects before applying."
        else:
            recommendation = "NOT RECOMMENDED"
            rec_reason = "Significant gap in required core competencies."

        # 6. Structured Explanation
        why_match = [
            f"Matches {len(matched_skills)} core skills ({', '.join(list(matched_skills)[:5])})",
            f"Experience requirement satisfied ({candidate_experience_years} years vs {required_years} years required)",
        ]
        why_not_match = [
            f"Missing {len(missing_skills)} target skills ({', '.join(missing_skills[:5])})"
        ] if missing_skills else []

        recruiter_notice = [
            f"Hard requirement coverage: {round(hard_match_score, 1)}%",
            f"Candidate seniority level: {'Aligned' if candidate_experience_years >= required_years else 'Below target years'}",
        ]

        return {
            "overall_match": overall_match,
            "dimension_scores": {
                "hard_skills": round(hard_match_score, 1),
                "overall_skills": round(skills_match_score, 1),
                "experience": round(exp_match_score, 1),
            },
            "recommendation": recommendation,
            "recommendation_reason": rec_reason,
            "matched_skills": sorted(list(matched_skills)),
            "missing_skills": sorted(missing_skills),
            "explanation": {
                "why_you_match": why_match,
                "why_you_dont_match": why_not_match,
                "recruiter_focus": recruiter_notice,
            }
        }


explainable_matcher_service = ExplainableMatcherService()
