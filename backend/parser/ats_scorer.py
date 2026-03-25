"""
ResumeIQ — ATS Scorer + Career DNA Mapper
Scores a parsed resume and maps personality/skill archetypes.
"""

import json
import math
from backend.parser.pdf_parser import SKILL_TAXONOMY

# ── Scoring weights ────────────────────────────────────────────────────────────
WEIGHTS = {
    "skill_coverage":    0.30,   # How many skills from taxonomy appear
    "section_completeness": 0.25, # All key sections present
    "experience":        0.20,   # Years of experience curve
    "keyword_density":   0.15,   # Industry keywords per 100 words
    "contact_info":      0.10,   # Email, phone, LinkedIn present
}

REQUIRED_SECTIONS = ["education", "experience", "skills", "summary"]

# ── Career DNA Archetypes ──────────────────────────────────────────────────────
# Each archetype has a skill cluster; we score presence → radar chart data
DNA_ARCHETYPES = {
    "The Builder":      ["python", "flask", "django", "fastapi", "docker", "kubernetes",
                         "rest api", "sql", "postgresql", "redis"],
    "The Data Wizard":  ["machine learning", "deep learning", "pandas", "numpy",
                         "scikit-learn", "tensorflow", "pytorch", "statistics", "r"],
    "The Cloud Architect": ["aws", "gcp", "azure", "terraform", "kubernetes",
                            "ci/cd", "microservices", "serverless", "docker"],
    "The Data Engineer": ["spark", "kafka", "airflow", "etl", "data pipeline",
                          "snowflake", "bigquery", "databricks", "dbt"],
    "The Storyteller":  ["tableau", "power bi", "matplotlib", "seaborn", "plotly",
                         "d3.js", "data visualization", "dashboard"],
    "The AI Whisperer":  ["nlp", "llm", "rag", "transformers", "bert", "gpt",
                          "hugging face", "computer vision", "generative ai"],
    "The Full-Stack Engineer": ["react", "angular", "vue", "node.js", "html",
                                "css", "javascript", "typescript", "graphql"],
    "The DevOps Ninja":  ["ci/cd", "jenkins", "github actions", "ansible", "helm",
                          "terraform", "monitoring", "grafana", "docker"],
}

INDUSTRY_KEYWORDS = [
    "developed", "designed", "implemented", "optimized", "deployed", "automated",
    "reduced", "increased", "improved", "led", "managed", "built", "created",
    "analyzed", "architected", "integrated", "mentored", "collaborated",
    "delivered", "scaled", "migrated", "refactored",
]


class ATSScorer:
    """
    Returns a full scoring breakdown and Career DNA map for a parsed resume dict.
    """

    def score(self, parsed: dict) -> dict:
        skills_found = parsed.get("skills", [])
        sections     = parsed.get("section_flags", {})
        raw_text     = parsed.get("raw_text", "")
        yoe          = parsed.get("years_of_experience", 0)

        # Component scores (each 0–100)
        skill_score   = self._skill_coverage(skills_found)
        section_score = self._section_completeness(sections)
        exp_score     = self._experience_score(yoe)
        kw_score      = self._keyword_density(raw_text)
        contact_score = self._contact_score(parsed)

        # Weighted overall
        overall = (
            skill_score   * WEIGHTS["skill_coverage"]
            + section_score * WEIGHTS["section_completeness"]
            + exp_score     * WEIGHTS["experience"]
            + kw_score      * WEIGHTS["keyword_density"]
            + contact_score * WEIGHTS["contact_info"]
        )

        # Skill gaps
        all_skills = {s for skills in SKILL_TAXONOMY.values() for s in skills}
        missing = sorted(list(all_skills - set(skills_found)))[:20]  # top 20 gaps

        # Career DNA
        dna = self._career_dna(skills_found)

        # Actionable recommendations
        recommendations = self._build_recommendations(
            skill_score, section_score, exp_score, contact_score,
            sections, parsed, skills_found
        )

        return {
            "ats_score":        round(overall, 1),
            "skill_score":      round(skill_score, 1),
            "format_score":     round(section_score, 1),
            "experience_score": round(exp_score, 1),
            "keyword_score":    round(kw_score, 1),
            "contact_score":    round(contact_score, 1),
            "overall_score":    round(overall, 1),
            "skills_found":     skills_found,
            "skills_missing":   missing,
            "career_dna":       dna,
            "recommendations":  recommendations,
        }

    # ── Component scorers ──────────────────────────────────────────────────────
    def _skill_coverage(self, found: list) -> float:
        total = sum(len(v) for v in SKILL_TAXONOMY.values())
        return min(100.0, (len(found) / max(total * 0.25, 1)) * 100)

    def _section_completeness(self, flags: dict) -> float:
        present = sum(flags.get(s, False) for s in REQUIRED_SECTIONS)
        return (present / len(REQUIRED_SECTIONS)) * 100

    def _experience_score(self, yoe: float) -> float:
        # Logarithmic curve: 0yr→0, 2yr→60, 5yr→85, 10yr→100
        if yoe <= 0:
            return 0.0
        return min(100.0, 35 * math.log(yoe + 1, 2))

    def _keyword_density(self, text: str) -> float:
        if not text:
            return 0.0
        words     = text.lower().split()
        kw_count  = sum(1 for w in words if w in INDUSTRY_KEYWORDS)
        density   = (kw_count / max(len(words), 1)) * 100
        return min(100.0, density * 20)   # normalise

    def _contact_score(self, parsed: dict) -> float:
        score = 0
        if parsed.get("email"):    score += 40
        if parsed.get("phone"):    score += 20
        if parsed.get("linkedin"): score += 25
        if parsed.get("github"):   score += 15
        return float(score)

    # ── Career DNA Map ─────────────────────────────────────────────────────────
    def _career_dna(self, found_skills: list) -> dict:
        found_set = set(found_skills)
        dna = {}
        for archetype, cluster in DNA_ARCHETYPES.items():
            overlap = len(found_set & set(cluster))
            score   = round(min(100.0, (overlap / len(cluster)) * 100), 1)
            dna[archetype] = {
                "score":         score,
                "matched_skills": list(found_set & set(cluster)),
                "total_in_cluster": len(cluster),
            }
        return dna

    # ── Recommendations ────────────────────────────────────────────────────────
    def _build_recommendations(self, skill_s, section_s, exp_s, contact_s,
                                sections, parsed, found_skills) -> list:
        recs = []
        if skill_s < 40:
            recs.append("🔧 Add more technical skills — include frameworks, tools, and cloud platforms you've used.")
        if not sections.get("summary"):
            recs.append("✍️ Add a professional summary/objective section — ATS systems weight this heavily.")
        if not sections.get("certifications"):
            recs.append("🏆 List certifications and online courses (Coursera, AWS, GCP, etc.) to boost ATS score.")
        if not parsed.get("linkedin"):
            recs.append("🔗 Include your LinkedIn profile URL for recruiter visibility.")
        if not parsed.get("github"):
            recs.append("💻 Add your GitHub URL — especially critical for technical roles.")
        if exp_s < 30:
            recs.append("📅 Quantify project dates to help systems estimate your experience.")
        if "machine learning" in found_skills and "mlops" not in found_skills:
            recs.append("🚀 Consider adding MLOps skills (MLflow, BentoML, model monitoring) to stand out.")
        if not sections.get("projects"):
            recs.append("📁 Add a Projects section showcasing GitHub repos or hackathon work.")
        if section_s < 75:
            recs.append("📋 Ensure all core sections are present: Summary, Experience, Skills, Education.")
        if len(found_skills) > 0 and "docker" not in found_skills:
            recs.append("🐳 Docker & containerisation is increasingly required — add it if applicable.")
        return recs


scorer = ATSScorer()
