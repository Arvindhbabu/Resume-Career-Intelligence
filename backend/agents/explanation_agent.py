"""
ResumeIQ v2 — Explanation Agent
Generates human-readable explanations for all scores and decisions.
"""

import logging
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ExplanationAgent(BaseAgent):
    name = "explanation_agent"
    description = "Generates human-readable explanations for scores"

    async def execute(self, input_data: dict) -> dict:
        """
        Generate natural language explanations for the analysis results.

        Input: {
            "parsed_resume": dict,
            "analysis_scores": dict,
            "job_matches": list,
            "critic_review": dict,
        }
        """
        parsed = input_data.get("parsed_resume", {})
        scores = input_data.get("analysis_scores", {})
        matches = input_data.get("job_matches", [])
        critic = input_data.get("critic_review", {})

        # Try LLM-powered explanation
        llm_result = self.call_llm(
            prompt=self._build_prompt(parsed, scores, matches),
            system_prompt=(
                "You are an expert career advisor. Generate a clear, encouraging "
                "explanation of the resume analysis results. Be specific and actionable."
            ),
        )

        if llm_result:
            explanation = self.parse_llm_json(llm_result)
            if explanation.get("summary"):
                return explanation

        return await self.fallback(input_data)

    async def fallback(self, input_data: dict) -> dict:
        """Generate rule-based explanations."""
        parsed = input_data.get("parsed_resume", {})
        scores = input_data.get("analysis_scores", {})
        matches = input_data.get("job_matches", [])
        critic = input_data.get("critic_review", {})

        name = parsed.get("name", "Candidate")
        skills = parsed.get("skills", [])
        yoe = parsed.get("years_of_experience", 0)
        overall = scores.get("overall_score", 0)

        # Build summary
        parts = []

        # Overall assessment
        if overall >= 80:
            parts.append(f"🌟 {name} presents an exceptional profile with a score of {overall}%.")
        elif overall >= 60:
            parts.append(f"✅ {name} shows a strong profile with a score of {overall}%.")
        elif overall >= 40:
            parts.append(f"📊 {name}'s profile scores {overall}%, showing good potential with room for improvement.")
        else:
            parts.append(f"📋 {name}'s profile scores {overall}%. Focus on adding key skills and experience to improve.")

        # Skills analysis
        if len(skills) >= 15:
            parts.append(f"Demonstrates breadth across {len(skills)} technical skills.")
        elif len(skills) >= 8:
            parts.append(f"Shows solid technical foundation with {len(skills)} identified skills.")
        elif skills:
            parts.append(f"Has {len(skills)} core skills — expanding the skill set would improve match rates.")

        # Experience
        if yoe >= 5:
            parts.append(f"With {yoe} years of experience, qualifies for mid-to-senior level positions.")
        elif yoe >= 2:
            parts.append(f"Has {yoe} years of experience, suitable for mid-level roles.")
        elif yoe > 0:
            parts.append(f"Early career with {yoe} year(s) of experience — projects and certifications can compensate.")
        else:
            parts.append("Experience level unclear — consider adding clear date ranges to work history.")

        # Top matches
        if matches and isinstance(matches[0], dict):
            top = matches[0]
            title = top.get("job_title", "Unknown")
            score = top.get("final_score", top.get("match_score", 0))
            parts.append(f"Best job match: {title} ({score}% fit).")

        # Missing skills
        missing = scores.get("skills_missing", [])[:5]
        if missing:
            missing_names = [m if isinstance(m, str) else m.get("skill", "") for m in missing]
            parts.append(f"Key skills to add: {', '.join(missing_names)}.")

        # Build recommendations
        recs = self._build_recommendations(parsed, scores, critic)

        # Build dimension explanations
        dim_explanations = {}
        score_dims = scores.get("scores", scores)
        if isinstance(score_dims, dict):
            if score_dims.get("skills_match", 0) >= 70:
                dim_explanations["skills"] = "Strong skill alignment with target roles"
            else:
                dim_explanations["skills"] = "Consider adding in-demand skills to improve matching"

            if score_dims.get("experience_match", 0) >= 70:
                dim_explanations["experience"] = "Experience level well-suited for target roles"
            else:
                dim_explanations["experience"] = "Building more experience or showcasing projects would help"

        return {
            "summary": " ".join(parts),
            "dimension_explanations": dim_explanations,
            "recommendations": recs,
            "strengths": self._identify_strengths(parsed, scores),
            "areas_for_improvement": self._identify_improvements(parsed, scores),
        }

    def _build_prompt(self, parsed: dict, scores: dict, matches: list) -> str:
        skills_str = ", ".join(parsed.get("skills", [])[:15])
        top_match = matches[0]["job_title"] if matches else "N/A"

        return f"""
Analyze these resume results and generate an explanation. Return JSON:

{{
  "summary": "2-3 sentence overall assessment",
  "dimension_explanations": {{
    "skills": "explanation of skills score",
    "experience": "explanation of experience score",
    "domain": "explanation of domain relevance"
  }},
  "recommendations": ["actionable recommendation 1", "recommendation 2"],
  "strengths": ["strength 1", "strength 2"],
  "areas_for_improvement": ["area 1", "area 2"]
}}

Candidate: {parsed.get('name', 'Unknown')}
Skills: {skills_str}
Experience: {parsed.get('years_of_experience', 0)} years
Overall Score: {scores.get('overall_score', 0)}
Best Match: {top_match}
"""

    def _build_recommendations(self, parsed: dict, scores: dict, critic: dict) -> list:
        recs = []
        skills = set(parsed.get("skills", []))
        sections = parsed.get("section_flags", {})

        if not sections.get("summary"):
            recs.append("✍️ Add a professional summary — it's the first thing recruiters read.")
        if not parsed.get("linkedin"):
            recs.append("🔗 Include your LinkedIn URL for recruiter visibility.")
        if not parsed.get("github"):
            recs.append("💻 Add your GitHub profile — critical for tech roles.")
        if "docker" not in skills and len(skills) > 5:
            recs.append("🐳 Learn Docker/containerization — required in 70%+ of modern tech roles.")
        if "machine learning" in skills and "mlops" not in skills:
            recs.append("🚀 Add MLOps skills to bridge the gap between ML research and production.")
        if not sections.get("projects"):
            recs.append("📁 Add a Projects section to demonstrate practical experience.")
        if not sections.get("certifications"):
            recs.append("🏆 Certifications from AWS/GCP/Coursera significantly boost ATS scores.")

        # Add critic recommendations
        for issue in critic.get("issues", []):
            if issue.get("suggestion"):
                recs.append(f"⚡ {issue['suggestion']}")

        return recs[:8]

    def _identify_strengths(self, parsed: dict, scores: dict) -> list:
        strengths = []
        skills = parsed.get("skills", [])

        if len(skills) >= 15:
            strengths.append(f"Broad technical skill set ({len(skills)} skills)")
        if parsed.get("github"):
            strengths.append("Active GitHub presence")
        if parsed.get("years_of_experience", 0) >= 3:
            strengths.append(f"{parsed['years_of_experience']} years of industry experience")
        if parsed.get("section_flags", {}).get("projects"):
            strengths.append("Demonstrates practical project experience")
        if any(s in skills for s in ["llm", "rag", "langchain", "generative ai"]):
            strengths.append("GenAI/LLM skills — highly in-demand")
        if any(s in skills for s in ["docker", "kubernetes", "aws", "gcp"]):
            strengths.append("Cloud & DevOps competency")

        return strengths[:5]

    def _identify_improvements(self, parsed: dict, scores: dict) -> list:
        improvements = []
        skills = set(parsed.get("skills", []))

        if len(skills) < 8:
            improvements.append("Expand technical skill set")
        if not parsed.get("linkedin"):
            improvements.append("Add LinkedIn profile")
        if parsed.get("years_of_experience", 0) == 0:
            improvements.append("Clarify work experience with date ranges")
        if not parsed.get("section_flags", {}).get("summary"):
            improvements.append("Add professional summary section")

        return improvements[:5]


explanation_agent = ExplanationAgent()
