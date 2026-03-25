"""
ResumeIQ — ML Job Recommender
Cosine-similarity based job matching with skill gap analysis.
Includes a built-in job dataset so no external data file is needed at startup.
"""

import json
import math
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# Built-in job dataset (50 roles across domains — extend via CSV in production)
# Each entry: title, domain, required_skills, salary_range, company_type
# ══════════════════════════════════════════════════════════════════════════════
JOB_CORPUS = [
    {"title": "Data Scientist",           "domain": "data_science",
     "skills": ["python","machine learning","pandas","numpy","scikit-learn","sql","statistics","matplotlib"],
     "salary": "₹8–18 LPA", "type": "MNC"},
    {"title": "ML Engineer",              "domain": "data_science",
     "skills": ["python","machine learning","tensorflow","pytorch","mlops","docker","aws","rest api"],
     "salary": "₹12–25 LPA", "type": "Product"},
    {"title": "Data Analyst",             "domain": "data_science",
     "skills": ["sql","python","pandas","tableau","power bi","excel","statistics"],
     "salary": "₹5–12 LPA", "type": "MNC"},
    {"title": "AI/ML Research Engineer",  "domain": "data_science",
     "skills": ["deep learning","nlp","transformers","pytorch","hugging face","python","research"],
     "salary": "₹15–35 LPA", "type": "Research"},
    {"title": "NLP Engineer",             "domain": "data_science",
     "skills": ["nlp","bert","transformers","python","spacy","machine learning","llm"],
     "salary": "₹10–22 LPA", "type": "Product"},
    {"title": "Computer Vision Engineer", "domain": "data_science",
     "skills": ["computer vision","opencv","pytorch","tensorflow","python","deep learning"],
     "salary": "₹10–24 LPA", "type": "Product"},
    {"title": "GenAI / LLM Engineer",     "domain": "data_science",
     "skills": ["llm","rag","langchain","openai","hugging face","python","prompt engineering","vector db"],
     "salary": "₹15–40 LPA", "type": "Startup"},
    {"title": "Data Engineer",            "domain": "data_engineering",
     "skills": ["spark","kafka","airflow","etl","sql","python","aws","data pipeline"],
     "salary": "₹8–20 LPA", "type": "MNC"},
    {"title": "Analytics Engineer",       "domain": "data_engineering",
     "skills": ["dbt","sql","python","bigquery","snowflake","airflow","data warehouse"],
     "salary": "₹10–22 LPA", "type": "Product"},
    {"title": "Big Data Engineer",        "domain": "data_engineering",
     "skills": ["spark","hadoop","kafka","scala","python","hdfs","hive","aws"],
     "salary": "₹10–25 LPA", "type": "MNC"},
    {"title": "Cloud Data Engineer",      "domain": "data_engineering",
     "skills": ["aws","gcp","bigquery","databricks","terraform","python","sql","etl"],
     "salary": "₹12–28 LPA", "type": "Cloud"},
    {"title": "Backend Developer (Python)","domain": "web",
     "skills": ["python","flask","django","fastapi","postgresql","redis","rest api","docker"],
     "salary": "₹6–15 LPA", "type": "Startup"},
    {"title": "Full-Stack Developer",     "domain": "web",
     "skills": ["javascript","react","node.js","python","sql","html","css","rest api"],
     "salary": "₹6–18 LPA", "type": "Startup"},
    {"title": "DevOps / MLOps Engineer",  "domain": "cloud",
     "skills": ["docker","kubernetes","ci/cd","jenkins","terraform","aws","python","helm"],
     "salary": "₹10–25 LPA", "type": "MNC"},
    {"title": "Cloud Solutions Architect","domain": "cloud",
     "skills": ["aws","azure","gcp","terraform","kubernetes","microservices","serverless"],
     "salary": "₹18–45 LPA", "type": "MNC"},
    {"title": "Business Intelligence Developer","domain": "data_science",
     "skills": ["power bi","tableau","sql","excel","python","data visualization","etl"],
     "salary": "₹5–12 LPA", "type": "MNC"},
    {"title": "Quantitative Analyst",     "domain": "data_science",
     "skills": ["python","r","statistics","machine learning","sql","pandas","numpy"],
     "salary": "₹12–30 LPA", "type": "Finance"},
    {"title": "Product Analyst",          "domain": "data_science",
     "skills": ["sql","python","tableau","a/b testing","statistics","excel"],
     "salary": "₹7–15 LPA", "type": "Product"},
    {"title": "Site Reliability Engineer","domain": "cloud",
     "skills": ["kubernetes","docker","prometheus","grafana","python","bash","ci/cd","aws"],
     "salary": "₹12–28 LPA", "type": "MNC"},
    {"title": "Research Scientist (AI)",  "domain": "data_science",
     "skills": ["deep learning","nlp","pytorch","python","statistics","research","machine learning"],
     "salary": "₹20–50 LPA", "type": "Research"},
]


# ══════════════════════════════════════════════════════════════════════════════
class JobRecommender:
    """
    TF-IDF + Cosine Similarity recommender.
    No external dependencies — works out of the box.
    """

    def __init__(self):
        self.corpus  = JOB_CORPUS
        self._tfidf  = self._build_tfidf()

    def _build_tfidf(self) -> list[dict]:
        """Pre-compute TF-IDF vectors for each job in corpus."""
        # Corpus-wide term frequencies
        doc_freq: Counter = Counter()
        N = len(self.corpus)
        all_skill_sets = [set(j["skills"]) for j in self.corpus]
        for skill_set in all_skill_sets:
            for skill in skill_set:
                doc_freq[skill] += 1

        vectors = []
        for job, skill_set in zip(self.corpus, all_skill_sets):
            vec = {}
            for skill in skill_set:
                tf  = 1.0 / len(skill_set)                      # normalised TF
                idf = math.log((N + 1) / (doc_freq[skill] + 1)) # smooth IDF
                vec[skill] = tf * idf
            vectors.append(vec)
        return vectors

    def _cosine(self, vec_a: dict, vec_b: dict) -> float:
        common = set(vec_a) & set(vec_b)
        if not common:
            return 0.0
        dot  = sum(vec_a[k] * vec_b.get(k, 0) for k in common)
        norm_a = math.sqrt(sum(v**2 for v in vec_a.values()))
        norm_b = math.sqrt(sum(v**2 for v in vec_b.values()))
        return dot / (norm_a * norm_b + 1e-9)

    def _resume_vec(self, skills: list[str]) -> dict:
        """Create a simple unit vector for resume skills."""
        if not skills:
            return {}
        weight = 1.0 / len(skills)
        return {skill: weight for skill in skills}

    def recommend(self, skills: list[str], top_n: int = 5) -> list[dict]:
        """
        Returns top-N job matches sorted by cosine similarity.
        Each result includes match_score, required_skills, missing_skills.
        """
        resume_vec = self._resume_vec(skills)
        skill_set  = set(skills)
        scored = []

        for job, job_vec in zip(self.corpus, self._tfidf):
            sim     = self._cosine(resume_vec, job_vec)
            missing = [s for s in job["skills"] if s not in skill_set]
            scored.append({
                "job_title":       job["title"],
                "company_type":    job["type"],
                "match_score":     round(sim * 100, 1),
                "salary_range":    job["salary"],
                "required_skills": job["skills"],
                "missing_skills":  missing,
                "job_url":         f"https://www.linkedin.com/jobs/search/?keywords={job['title'].replace(' ','%20')}",
            })

        # Sort by score desc, deduplicate titles
        seen, results = set(), []
        for item in sorted(scored, key=lambda x: x["match_score"], reverse=True):
            if item["job_title"] not in seen:
                seen.add(item["job_title"])
                results.append(item)
            if len(results) >= top_n:
                break

        return results

    def skill_gap_roadmap(self, skills: list[str], target_role: str) -> dict:
        """
        For a specific target role, return a structured learning roadmap
        covering the missing skills.
        """
        job = next((j for j in self.corpus if j["title"].lower() == target_role.lower()), None)
        if not job:
            return {}
        skill_set = set(skills)
        missing   = [s for s in job["skills"] if s not in skill_set]
        present   = [s for s in job["skills"] if s in skill_set]
        return {
            "target_role":     job["title"],
            "match_percent":   round((len(present) / len(job["skills"])) * 100, 1),
            "skills_present":  present,
            "skills_missing":  missing,
            "resources": {
                skill: f"https://www.google.com/search?q=learn+{skill.replace(' ','+')}+free+course"
                for skill in missing
            },
        }


recommender = JobRecommender()
