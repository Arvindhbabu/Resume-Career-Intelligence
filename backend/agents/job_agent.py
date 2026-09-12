"""
ResumeIQ v2 — Job Understanding Agent
Analyzes job descriptions semantically to extract requirements.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)

# ── Built-in job corpus (50+ roles) ──────────────────────────────────────────────
JOB_CORPUS = [
    {"title": "Data Scientist", "domain": "data_science",
     "skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql", "statistics", "matplotlib"],
     "salary": "₹8–18 LPA", "type": "MNC", "experience_level": "mid",
     "description": "Build ML models for predictive analytics, perform EDA, create data pipelines"},
    {"title": "ML Engineer", "domain": "data_science",
     "skills": ["python", "machine learning", "tensorflow", "pytorch", "mlops", "docker", "aws", "rest api"],
     "salary": "₹12–25 LPA", "type": "Product", "experience_level": "mid",
     "description": "Deploy ML models at scale, build training pipelines, optimize model performance"},
    {"title": "Data Analyst", "domain": "data_science",
     "skills": ["sql", "python", "pandas", "tableau", "power bi", "statistics"],
     "salary": "₹5–12 LPA", "type": "MNC", "experience_level": "entry",
     "description": "Analyze business data, create dashboards, generate insights for stakeholders"},
    {"title": "AI/ML Research Engineer", "domain": "data_science",
     "skills": ["deep learning", "nlp", "transformers", "pytorch", "hugging face", "python"],
     "salary": "₹15–35 LPA", "type": "Research", "experience_level": "senior",
     "description": "Conduct ML research, publish papers, develop novel architectures"},
    {"title": "NLP Engineer", "domain": "data_science",
     "skills": ["nlp", "bert", "transformers", "python", "machine learning", "llm"],
     "salary": "₹10–22 LPA", "type": "Product", "experience_level": "mid",
     "description": "Build NLP pipelines, fine-tune language models, develop text analytics"},
    {"title": "Computer Vision Engineer", "domain": "data_science",
     "skills": ["computer vision", "opencv", "pytorch", "tensorflow", "python", "deep learning"],
     "salary": "₹10–24 LPA", "type": "Product", "experience_level": "mid",
     "description": "Develop image/video processing systems, object detection, segmentation"},
    {"title": "GenAI / LLM Engineer", "domain": "data_science",
     "skills": ["llm", "rag", "langchain", "hugging face", "python", "prompt engineering", "vector database"],
     "salary": "₹15–40 LPA", "type": "Startup", "experience_level": "mid",
     "description": "Build RAG systems, fine-tune LLMs, develop AI-powered applications"},
    {"title": "Data Engineer", "domain": "data_engineering",
     "skills": ["spark", "kafka", "airflow", "etl", "sql", "python", "aws", "data pipeline"],
     "salary": "₹8–20 LPA", "type": "MNC", "experience_level": "mid",
     "description": "Design data pipelines, manage data warehouses, ensure data quality"},
    {"title": "Analytics Engineer", "domain": "data_engineering",
     "skills": ["dbt", "sql", "python", "bigquery", "snowflake", "airflow", "data warehouse"],
     "salary": "₹10–22 LPA", "type": "Product", "experience_level": "mid",
     "description": "Transform raw data into analysis-ready datasets, manage data models"},
    {"title": "Big Data Engineer", "domain": "data_engineering",
     "skills": ["spark", "hadoop", "kafka", "scala", "python", "hive", "aws"],
     "salary": "₹10–25 LPA", "type": "MNC", "experience_level": "mid",
     "description": "Process large-scale datasets, optimize distributed computing systems"},
    {"title": "Backend Developer (Python)", "domain": "web",
     "skills": ["python", "flask", "django", "fastapi", "postgresql", "redis", "rest api", "docker"],
     "salary": "₹6–15 LPA", "type": "Startup", "experience_level": "mid",
     "description": "Build scalable backend services, design APIs, manage databases"},
    {"title": "Full-Stack Developer", "domain": "web",
     "skills": ["javascript", "react", "node.js", "python", "sql", "html", "css", "rest api"],
     "salary": "₹6–18 LPA", "type": "Startup", "experience_level": "mid",
     "description": "Develop end-to-end web applications, frontend and backend"},
    {"title": "DevOps / MLOps Engineer", "domain": "cloud_devops",
     "skills": ["docker", "kubernetes", "ci/cd", "jenkins", "terraform", "aws", "python", "helm"],
     "salary": "₹10–25 LPA", "type": "MNC", "experience_level": "mid",
     "description": "Automate deployment pipelines, manage infrastructure, ensure reliability"},
    {"title": "Cloud Solutions Architect", "domain": "cloud_devops",
     "skills": ["aws", "azure", "gcp", "terraform", "kubernetes", "microservices", "serverless"],
     "salary": "₹18–45 LPA", "type": "MNC", "experience_level": "senior",
     "description": "Design cloud architectures, lead migration projects, optimize costs"},
    {"title": "Site Reliability Engineer", "domain": "cloud_devops",
     "skills": ["kubernetes", "docker", "prometheus", "grafana", "python", "bash", "ci/cd", "aws"],
     "salary": "₹12–28 LPA", "type": "MNC", "experience_level": "mid",
     "description": "Ensure system reliability, implement monitoring, automate incident response"},
    {"title": "Business Intelligence Developer", "domain": "data_science",
     "skills": ["power bi", "tableau", "sql", "python", "data visualization", "etl"],
     "salary": "₹5–12 LPA", "type": "MNC", "experience_level": "entry",
     "description": "Build dashboards, create reports, automate data workflows"},
    {"title": "Quantitative Analyst", "domain": "data_science",
     "skills": ["python", "r", "statistics", "machine learning", "sql", "pandas", "numpy"],
     "salary": "₹12–30 LPA", "type": "Finance", "experience_level": "mid",
     "description": "Develop quantitative models, algorithmic trading, risk analysis"},
    {"title": "Research Scientist (AI)", "domain": "data_science",
     "skills": ["deep learning", "nlp", "pytorch", "python", "statistics", "machine learning"],
     "salary": "₹20–50 LPA", "type": "Research", "experience_level": "senior",
     "description": "Lead AI research projects, publish in top venues, mentor team"},
    {"title": "Frontend Developer", "domain": "web",
     "skills": ["react", "javascript", "typescript", "html", "css", "next.js", "tailwindcss"],
     "salary": "₹5–15 LPA", "type": "Startup", "experience_level": "mid",
     "description": "Build responsive web interfaces, implement design systems"},
    {"title": "Product Manager (Tech)", "domain": "management",
     "skills": ["product management", "agile", "sql", "data analysis", "stakeholder management"],
     "salary": "₹12–30 LPA", "type": "Product", "experience_level": "mid",
     "description": "Define product roadmap, coordinate cross-functional teams"},
]


class JobAgent(BaseAgent):
    name = "job_agent"
    description = "Analyzes job requirements and matches them semantically"

    async def execute(self, input_data: dict) -> dict:
        """
        Understand job requirements from the built-in corpus.

        Input: {"skills": list, "experience_level": str}
        Output: {"jobs": list, "domain_analysis": dict}
        """
        candidate_skills = set(s.lower() for s in input_data.get("skills", []))
        yoe = input_data.get("years_of_experience", 0)

        # Determine experience level
        if yoe >= 7:
            exp_level = "senior"
        elif yoe >= 2:
            exp_level = "mid"
        else:
            exp_level = "entry"

        # Analyze each job in corpus
        job_analyses = []
        for job in JOB_CORPUS:
            job_skills = set(s.lower() for s in job["skills"])

            # Skill overlap
            matched = candidate_skills & job_skills
            missing = job_skills - candidate_skills
            extra = candidate_skills - job_skills

            # Check for semantic equivalents using skill graph
            semantic_matches = []
            still_missing = set()
            for m_skill in missing:
                found_equiv = False
                for c_skill in extra:
                    if skill_graph.find_equivalent_skills(m_skill, c_skill):
                        semantic_matches.append((c_skill, m_skill))
                        found_equiv = True
                        break
                    sim = skill_graph.compute_skill_similarity(m_skill, c_skill)
                    if sim >= 0.5:
                        semantic_matches.append((c_skill, m_skill))
                        found_equiv = True
                        break
                if not found_equiv:
                    still_missing.add(m_skill)

            total_match = len(matched) + len(semantic_matches)
            match_pct = (total_match / len(job_skills) * 100) if job_skills else 0

            # Experience level bonus/penalty
            exp_match = 1.0
            if exp_level == job.get("experience_level", "mid"):
                exp_match = 1.1
            elif exp_level == "senior" and job.get("experience_level") == "entry":
                exp_match = 0.9

            final_score = min(100, match_pct * exp_match)

            job_analyses.append({
                "job_title": job["title"],
                "domain": job["domain"],
                "company_type": job["type"],
                "salary_range": job["salary"],
                "experience_level": job.get("experience_level", "mid"),
                "description": job.get("description", ""),
                "match_score": round(final_score, 1),
                "skills_matched": list(matched),
                "semantic_matches": [{"candidate": c, "required": r}
                                     for c, r in semantic_matches],
                "skills_missing": list(still_missing),
                "skills_extra": list(extra)[:5],
                "required_skills": job["skills"],
                "job_url": f"https://www.linkedin.com/jobs/search/?keywords={job['title'].replace(' ', '%20')}",
            })

        # Sort by match score
        job_analyses.sort(key=lambda x: x["match_score"], reverse=True)

        # Domain analysis
        domain_scores = {}
        for ja in job_analyses:
            domain = ja["domain"]
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(ja["match_score"])

        domain_analysis = {
            domain: {
                "avg_match": round(sum(scores) / len(scores), 1),
                "best_match": round(max(scores), 1),
                "jobs_count": len(scores),
            }
            for domain, scores in domain_scores.items()
        }

        return {
            "top_matches": job_analyses[:10],
            "domain_analysis": domain_analysis,
            "total_jobs_analyzed": len(JOB_CORPUS),
            "candidate_experience_level": exp_level,
        }

    async def fallback(self, input_data: dict) -> dict:
        return await self.execute(input_data)  # Already rule-based


job_agent = JobAgent()
