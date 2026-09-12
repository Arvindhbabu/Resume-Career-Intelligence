"""
ResumeIQ v2 — Explainable AI Scorer
Multi-dimensional scoring with transparent, explainable breakdowns.
"""

import math
import logging
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class XAIScorer:
    """
    Explainable AI Score Engine.

    Instead of a single opaque score, provides:
    - Multi-dimensional breakdown (skills, experience, domain, projects, format)
    - Per-skill confidence and context
    - Natural language explanation for each dimension
    - Confidence intervals
    """

    def score(self, parsed: dict, job_match_data: dict = None) -> dict:
        """
        Compute a comprehensive, explainable score for a parsed resume.

        Args:
            parsed: Output from parser agent
            job_match_data: Optional job matching results

        Returns:
            Full XAI scoring breakdown
        """
        skills_found = parsed.get("skills", [])
        sections = parsed.get("section_flags", {})
        raw_text = parsed.get("raw_text", "")
        yoe = parsed.get("years_of_experience", 0)

        # ── Dimension scores ─────────────────────────────────────────────────
        skill_coverage = self._skill_coverage(skills_found)
        section_quality = self._section_quality(sections, parsed)
        experience = self._experience_score(yoe)
        keyword_depth = self._keyword_depth(raw_text)
        contact = self._contact_score(parsed)
        project_depth = self._project_depth(parsed)

        # ── Weighted overall ─────────────────────────────────────────────────
        overall = (
            skill_coverage * 0.30 +
            section_quality * 0.20 +
            experience * 0.20 +
            keyword_depth * 0.10 +
            contact * 0.05 +
            project_depth * 0.15
        )

        # ── Skill gaps with priority ─────────────────────────────────────────
        all_high_demand = [
            "python", "sql", "docker", "aws", "machine learning",
            "react", "kubernetes", "ci/cd", "rest api", "git",
        ]
        missing_critical = [s for s in all_high_demand if s not in set(skills_found)]

        # ── Skill graph enrichment ───────────────────────────────────────────
        skill_details = []
        for skill in skills_found:
            resolved = skill_graph.resolve_skill(skill)
            detail = {
                "skill": skill,
                "category": resolved["category"] if resolved else "Unknown",
                "confidence": 1.0,
            }
            if resolved:
                detail["path"] = resolved["path"]
            skill_details.append(detail)

        # ── Confidence ───────────────────────────────────────────────────────
        confidence = self._compute_confidence(parsed, skill_coverage)

        # ── Dimension explanations ───────────────────────────────────────────
        explanations = {
            "skills": self._explain_skill_score(skill_coverage, len(skills_found)),
            "experience": self._explain_experience(experience, yoe),
            "format": self._explain_format(section_quality, sections),
            "projects": self._explain_projects(project_depth, parsed),
            "contact": self._explain_contact(contact, parsed),
        }

        # ── Build recommendations ────────────────────────────────────────────
        recommendations = self._build_recommendations(
            skill_coverage, section_quality, experience, contact,
            sections, parsed, skills_found, missing_critical
        )

        return {
            "overall_score": round(overall, 1),
            "dimensions": {
                "skill_coverage": {"score": round(skill_coverage, 1), "weight": "30%",
                                   "explanation": explanations["skills"]},
                "section_quality": {"score": round(section_quality, 1), "weight": "20%",
                                    "explanation": explanations["format"]},
                "experience": {"score": round(experience, 1), "weight": "20%",
                               "explanation": explanations["experience"]},
                "project_depth": {"score": round(project_depth, 1), "weight": "15%",
                                  "explanation": explanations["projects"]},
                "keyword_density": {"score": round(keyword_depth, 1), "weight": "10%"},
                "contact_info": {"score": round(contact, 1), "weight": "5%",
                                 "explanation": explanations["contact"]},
            },
            "confidence": round(confidence, 2),
            "skill_details": skill_details,
            "missing_critical": missing_critical[:10],
            "recommendations": recommendations,
        }

    # ── Component scorers ──────────────────────────────────────────────────────

    def _skill_coverage(self, found: list) -> float:
        all_skills = skill_graph.get_all_skills_flat()
        total = len(all_skills) if all_skills else 100
        return min(100.0, (len(found) / max(total * 0.08, 1)) * 100)

    def _section_quality(self, flags: dict, parsed: dict) -> float:
        required = ["education", "experience", "skills", "summary"]
        present = sum(1 for s in required if flags.get(s))
        base = (present / len(required)) * 70

        # Quality bonuses
        if parsed.get("experience") and len(parsed["experience"]) > 100:
            base += 10
        if parsed.get("education") and len(parsed["education"]) > 50:
            base += 10
        if flags.get("projects"):
            base += 5
        if flags.get("certifications"):
            base += 5

        return min(100, base)

    def _experience_score(self, yoe: float) -> float:
        if yoe <= 0:
            return 10.0
        return min(100.0, 35 * math.log(yoe + 1, 2))

    def _keyword_depth(self, text: str) -> float:
        if not text:
            return 0.0
        action_verbs = [
            "developed", "designed", "implemented", "optimized", "deployed",
            "automated", "reduced", "increased", "improved", "led", "managed",
            "built", "created", "analyzed", "architected", "integrated",
            "mentored", "collaborated", "delivered", "scaled", "migrated",
        ]
        words = text.lower().split()
        kw_count = sum(1 for w in words if w in action_verbs)
        density = (kw_count / max(len(words), 1)) * 100
        return min(100.0, density * 20)

    def _contact_score(self, parsed: dict) -> float:
        score = 0
        if parsed.get("email"): score += 35
        if parsed.get("phone"): score += 15
        if parsed.get("linkedin"): score += 30
        if parsed.get("github"): score += 20
        return float(score)

    def _project_depth(self, parsed: dict) -> float:
        projects = parsed.get("projects", "")
        if not projects:
            return 15.0

        score = 35.0
        text = projects.lower()
        indicators = {
            "deploy": 8, "production": 8, "scale": 7, "api": 7,
            "database": 6, "machine learning": 9, "model": 7,
            "pipeline": 7, "docker": 7, "aws": 7, "real-time": 8,
        }
        for keyword, points in indicators.items():
            if keyword in text:
                score += points

        words = len(projects.split())
        if words > 200: score += 10
        if words > 500: score += 5

        return min(100, score)

    def _compute_confidence(self, parsed: dict, skill_score: float) -> float:
        """How confident are we in this analysis?"""
        text_len = len(parsed.get("raw_text", ""))
        confidence = 0.5

        if text_len > 500: confidence += 0.1
        if text_len > 1000: confidence += 0.1
        if text_len > 2000: confidence += 0.1
        if parsed.get("name") and parsed["name"] != "Unknown": confidence += 0.05
        if parsed.get("email"): confidence += 0.05
        if skill_score > 30: confidence += 0.1

        return min(1.0, confidence)

    # ── Explanations ───────────────────────────────────────────────────────────

    def _explain_skill_score(self, score: float, count: int) -> str:
        if score >= 80:
            return f"Excellent skill coverage with {count} skills detected across multiple domains."
        elif score >= 50:
            return f"Good skill coverage ({count} skills). Adding cloud & DevOps skills would improve this."
        else:
            return f"Limited skill coverage ({count} skills). Focus on adding in-demand technical skills."

    def _explain_experience(self, score: float, yoe: float) -> str:
        if yoe >= 5:
            return f"Strong experience profile with {yoe} years — qualifies for senior roles."
        elif yoe >= 2:
            return f"{yoe} years of experience — suitable for mid-level positions."
        elif yoe > 0:
            return f"Early career ({yoe} yr). Projects and certifications help compensate."
        return "Could not estimate experience — add clear date ranges to work history."

    def _explain_format(self, score: float, sections: dict) -> str:
        missing = [s for s in ["education", "experience", "skills", "summary"]
                   if not sections.get(s)]
        if not missing:
            return "All key resume sections present — well-structured format."
        return f"Missing sections: {', '.join(missing)}. Adding these will significantly improve ATS compatibility."

    def _explain_projects(self, score: float, parsed: dict) -> str:
        if score >= 70:
            return "Projects demonstrate strong practical complexity and production experience."
        elif score > 20:
            return "Projects show promise. Add deployment details and scale metrics for higher scores."
        return "No projects section detected. Adding 2-3 significant projects is highly recommended."

    def _explain_contact(self, score: float, parsed: dict) -> str:
        parts = []
        if not parsed.get("email"): parts.append("email")
        if not parsed.get("linkedin"): parts.append("LinkedIn")
        if not parsed.get("github"): parts.append("GitHub")
        if parts:
            return f"Missing: {', '.join(parts)}. Complete contact info improves recruiter reach."
        return "Complete contact information detected."

    def _build_recommendations(self, skill_s, section_s, exp_s, contact_s,
                                sections, parsed, skills, missing) -> list:
        recs = []
        if missing:
            recs.append({
                "icon": "🎯",
                "text": f"Add high-demand skills: {', '.join(missing[:5])}",
                "impact": "high",
            })
        if not sections.get("summary"):
            recs.append({
                "icon": "✍️",
                "text": "Add a professional summary section",
                "impact": "high",
            })
        if not parsed.get("linkedin"):
            recs.append({
                "icon": "🔗",
                "text": "Include LinkedIn profile URL",
                "impact": "medium",
            })
        if not parsed.get("github"):
            recs.append({
                "icon": "💻",
                "text": "Add GitHub URL for technical roles",
                "impact": "medium",
            })
        if not sections.get("projects"):
            recs.append({
                "icon": "📁",
                "text": "Add a Projects section with 2-3 significant projects",
                "impact": "high",
            })
        if exp_s < 30:
            recs.append({
                "icon": "📅",
                "text": "Add clear date ranges to experience entries",
                "impact": "medium",
            })
        return recs[:8]


# ── Singleton ────────────────────────────────────────────────────────────────────
xai_scorer = XAIScorer()
