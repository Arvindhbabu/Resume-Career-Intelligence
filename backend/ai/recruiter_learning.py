"""
ResumeIQ v2 — Recruiter Decision Learning System
Learns company hiring patterns from recruiter accept/reject decisions.
"""

import json
import logging
from collections import Counter, defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


class RecruiterLearningEngine:
    """
    Learns from recruiter decisions to identify hiring patterns.

    Capabilities:
    - Store and analyze accept/reject patterns
    - Identify most valued skills per company/role
    - Detect common rejection reasons
    - Generate hiring pattern insights
    - Predict candidate likelihood of selection
    """

    def __init__(self):
        self._decisions: list[dict] = []  # In-memory cache synced with DB

    def load_from_db(self, decisions: list[dict]):
        """Bulk load decisions from DB to synchronize in-memory state."""
        self._decisions = decisions
        logger.info(f"Loaded {len(decisions)} hiring decisions into learning engine")

    def record_decision(self, decision: dict) -> dict:
        """
        Record a recruiter's decision on a candidate.

        Args:
            decision: {
                "resume_id": int,
                "job_title": str,
                "decision": "selected" | "rejected",
                "reason": str (optional),
                "candidate_skills": list,
                "candidate_experience": float,
                "recruiter_id": str
            }
        """
        self._decisions.append(decision)

        return {
            "recorded": True,
            "total_decisions": len(self._decisions),
            "decision": decision.get("decision"),
        }

    def get_patterns(self, job_title: str = None,
                     recruiter_id: str = None) -> dict:
        """
        Analyze hiring patterns from recorded decisions.

        Returns insights about what skills and qualities are most valued.
        """
        filtered = self._decisions

        if job_title:
            filtered = [d for d in filtered
                        if d.get("job_title", "").lower() == job_title.lower()]
        if recruiter_id:
            filtered = [d for d in filtered
                        if d.get("recruiter_id") == recruiter_id]

        if not filtered:
            return self._default_patterns()

        selected = [d for d in filtered if d.get("decision") == "selected"]
        rejected = [d for d in filtered if d.get("decision") == "rejected"]

        # Skill frequency analysis
        selected_skills = Counter()
        rejected_skills = Counter()
        for d in selected:
            for s in d.get("candidate_skills", []):
                selected_skills[s] += 1
        for d in rejected:
            for s in d.get("candidate_skills", []):
                rejected_skills[s] += 1

        # Skills that correlate with selection
        valued_skills = []
        for skill, count in selected_skills.most_common(20):
            reject_count = rejected_skills.get(skill, 0)
            total = count + reject_count
            if total > 0:
                selection_rate = count / total
                valued_skills.append({
                    "skill": skill,
                    "selection_rate": round(selection_rate * 100, 1),
                    "appearances": total,
                })

        # Experience analysis
        selected_exp = [d.get("candidate_experience", 0) for d in selected]
        rejected_exp = [d.get("candidate_experience", 0) for d in rejected]

        avg_selected_exp = sum(selected_exp) / max(len(selected_exp), 1)
        avg_rejected_exp = sum(rejected_exp) / max(len(rejected_exp), 1)

        # Rejection reasons
        rejection_reasons = Counter()
        for d in rejected:
            reason = d.get("reason", "Not specified")
            rejection_reasons[reason] += 1

        return {
            "total_decisions": len(filtered),
            "selection_rate": round(len(selected) / max(len(filtered), 1) * 100, 1),
            "most_valued_skills": sorted(
                valued_skills, key=lambda x: x["selection_rate"], reverse=True
            )[:10],
            "experience_profile": {
                "avg_selected": round(avg_selected_exp, 1),
                "avg_rejected": round(avg_rejected_exp, 1),
                "preferred_range": f"{max(0, avg_selected_exp - 1):.0f}-{avg_selected_exp + 2:.0f} years"
            },
            "common_rejection_reasons": [
                {"reason": r, "count": c}
                for r, c in rejection_reasons.most_common(5)
            ],
            "insights": self._generate_insights(
                valued_skills, avg_selected_exp, len(selected), len(rejected)
            ),
        }

    def predict_likelihood(self, candidate_skills: list, experience: float,
                            job_title: str = None) -> dict:
        """
        Predict how likely a candidate is to be selected based on historical patterns.
        """
        patterns = self.get_patterns(job_title=job_title)
        valued = {s["skill"]: s["selection_rate"]
                  for s in patterns.get("most_valued_skills", [])}

        if not valued:
            return {"likelihood": 50.0, "basis": "insufficient_data"}

        # Skill alignment
        skill_scores = []
        for skill in candidate_skills:
            rate = valued.get(skill.lower(), 50)
            skill_scores.append(rate)

        avg_skill_align = sum(skill_scores) / max(len(skill_scores), 1)

        # Experience alignment
        exp_profile = patterns.get("experience_profile", {})
        preferred_exp = exp_profile.get("avg_selected", 3)
        exp_diff = abs(experience - preferred_exp)
        exp_factor = max(0, 100 - exp_diff * 15)

        likelihood = avg_skill_align * 0.7 + exp_factor * 0.3

        return {
            "likelihood": round(min(100, likelihood), 1),
            "basis": "historical_patterns",
            "factors": {
                "skill_alignment": round(avg_skill_align, 1),
                "experience_fit": round(exp_factor, 1),
            },
        }

    def _generate_insights(self, valued_skills, avg_exp, selected, rejected) -> list:
        """Generate human-readable hiring insights."""
        insights = []

        total = selected + rejected
        if total > 0:
            rate = selected / total * 100
            insights.append(
                f"📊 Overall selection rate: {rate:.0f}% ({selected}/{total} candidates)"
            )

        if valued_skills:
            top = valued_skills[0]
            insights.append(
                f"🎯 Most valued skill: '{top['skill']}' "
                f"({top['selection_rate']}% selection rate)"
            )

        if avg_exp > 0:
            insights.append(
                f"⏱ Average experience of selected candidates: {avg_exp:.1f} years"
            )

        return insights

    def _default_patterns(self) -> dict:
        """Return default patterns when no data is available."""
        return {
            "total_decisions": 0,
            "selection_rate": 0,
            "most_valued_skills": [],
            "experience_profile": {},
            "common_rejection_reasons": [],
            "insights": [
                "📋 No hiring decisions recorded yet.",
                "💡 Start recording decisions to build hiring pattern intelligence.",
            ],
        }


# ── Singleton ────────────────────────────────────────────────────────────────────
recruiter_engine = RecruiterLearningEngine()
