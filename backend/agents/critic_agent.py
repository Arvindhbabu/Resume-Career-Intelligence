"""
ResumeIQ v2 — Critic Agent
Reviews matching results for fairness, accuracy, and potential bias.
Acts as a quality gate in the multi-agent pipeline.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    name = "critic_agent"
    description = "Reviews results for fairness, accuracy, and bias"

    async def execute(self, input_data: dict) -> dict:
        """
        Review the analysis results for quality and fairness.

        Input: {
            "parsed_resume": dict,
            "analysis_scores": dict,
            "job_matches": list,
        }
        Output: {
            "quality_score": float,
            "issues": list,
            "corrections": list,
            "bias_alerts": list,
        }
        """
        parsed = input_data.get("parsed_resume", {})
        scores = input_data.get("analysis_scores", {})
        matches = input_data.get("job_matches", [])

        issues = []
        corrections = []
        bias_alerts = []

        # ── 1. Check for keyword bias ────────────────────────────────────────
        missing_skills = scores.get("skills_missing", [])
        found_skills = set(parsed.get("skills", []))

        for missing in missing_skills[:20]:
            if isinstance(missing, dict):
                skill_name = missing.get("skill", "")
            else:
                skill_name = missing

            # Check if candidate has an equivalent skill
            for found in found_skills:
                if skill_graph.find_equivalent_skills(skill_name, found):
                    bias_alerts.append({
                        "type": "keyword_bias",
                        "severity": "medium",
                        "message": (
                            f"⚠ Resume was penalized for missing '{skill_name}' "
                            f"but has equivalent skill: '{found}'"
                        ),
                        "suggestion": f"Consider '{found}' as equivalent to '{skill_name}'",
                    })
                    corrections.append({
                        "field": "skills_missing",
                        "action": "reclassify",
                        "skill": skill_name,
                        "reason": f"Equivalent to '{found}' via skill graph",
                    })
                    break

                sim = skill_graph.compute_skill_similarity(skill_name, found)
                if sim >= 0.4:
                    bias_alerts.append({
                        "type": "keyword_bias",
                        "severity": "low",
                        "message": (
                            f"ℹ '{skill_name}' is closely related to '{found}' "
                            f"(similarity: {sim:.0%})"
                        ),
                    })

        # ── 2. Check for scoring anomalies ───────────────────────────────────
        overall = scores.get("overall_score", 0)
        skills_match = scores.get("skills_match_score", 0)
        exp_match = scores.get("experience_match_score", 0)

        if overall > 0 and skills_match > 80 and exp_match < 30:
            issues.append({
                "type": "scoring_anomaly",
                "message": "High skill match but very low experience score — may be a fresh graduate with strong skills",
                "suggestion": "Consider weighting skills higher for entry-level roles",
            })

        if len(found_skills) > 20 and overall < 40:
            issues.append({
                "type": "scoring_anomaly",
                "message": f"Resume has {len(found_skills)} skills detected but overall score is only {overall}",
                "suggestion": "Review scoring weights — skills may be undervalued",
            })

        # ── 3. Check for potential name/gender bias ──────────────────────────
        name = parsed.get("name", "").strip()
        if name and name != "Unknown":
            bias_alerts.append({
                "type": "gender_bias_check",
                "severity": "info",
                "message": "Name-blind scoring recommended for fair evaluation",
                "suggestion": "Enable anonymization mode for unbiased ranking",
            })

        # ── 4. Check match quality ───────────────────────────────────────────
        if matches:
            top_score = matches[0].get("final_score", matches[0].get("match_score", 0))
            if top_score < 30:
                issues.append({
                    "type": "poor_matches",
                    "message": f"Best job match is only {top_score}% — candidate may be in a niche domain",
                    "suggestion": "Expand job corpus or consider adjacent roles",
                })

        # ── 5. Quality score ─────────────────────────────────────────────────
        quality = 100
        quality -= len(issues) * 10
        quality -= len([b for b in bias_alerts if b["severity"] == "medium"]) * 15
        quality -= len([b for b in bias_alerts if b["severity"] == "high"]) * 25
        quality = max(0, quality)

        return {
            "quality_score": quality,
            "issues": issues,
            "corrections": corrections,
            "bias_alerts": bias_alerts,
            "recommendations": [
                "Enable anonymization for name-blind evaluation",
                "Consider skill equivalences when computing gaps",
                "Review scoring weights periodically based on recruiter feedback",
            ] if bias_alerts else [],
        }

    async def fallback(self, input_data: dict) -> dict:
        return {
            "quality_score": 80,
            "issues": [],
            "corrections": [],
            "bias_alerts": [{
                "type": "info",
                "severity": "info",
                "message": "Critic agent running in fallback mode — limited bias detection",
            }],
        }


critic_agent = CriticAgent()
