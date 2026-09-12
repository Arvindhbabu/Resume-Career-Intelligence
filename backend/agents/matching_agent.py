"""
ResumeIQ v2 — Matching Agent
Performs semantic resume-to-job matching using embeddings + skill graph.
Multi-dimensional scoring across skills, experience, domain, and projects.
"""

import logging
from backend.agents.base_agent import BaseAgent
from backend.ai.embeddings import embedding_engine
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class MatchingAgent(BaseAgent):
    name = "matching_agent"
    description = "Semantic resume-to-job matching with multi-dimensional scoring"

    async def execute(self, input_data: dict) -> dict:
        """
        Match a parsed resume against job requirements.

        Input: {
            "parsed_resume": dict (from parser agent),
            "job_matches": list (from job agent),
        }
        Output: {
            "scored_matches": list,
            "overall_employability": float,
            "dimension_scores": dict
        }
        """
        parsed = input_data.get("parsed_resume", {})
        job_matches = input_data.get("job_matches", [])

        if not job_matches:
            return await self.fallback(input_data)

        resume_skills = parsed.get("skills", [])
        resume_text = parsed.get("raw_text", "")
        yoe = parsed.get("years_of_experience", 0)

        # Create resume embedding
        resume_embedding = embedding_engine.encode_resume(parsed)

        scored_matches = []
        for job in job_matches[:10]:
            # 1. Skill match (semantic)
            skill_result = embedding_engine.semantic_skill_match(
                resume_skills, job.get("required_skills", [])
            )
            skill_score = skill_result["score"]

            # 2. Semantic text similarity (resume vs job description)
            job_desc = job.get("description", job.get("job_title", ""))
            if job_desc:
                job_embedding = embedding_engine.encode(job_desc)
                text_similarity = embedding_engine.similarity_vectors(
                    resume_embedding, job_embedding
                ) * 100
            else:
                text_similarity = skill_score * 0.8

            # 3. Experience alignment
            job_level = job.get("experience_level", "mid")
            exp_score = self._experience_alignment(yoe, job_level)

            # 4. Domain relevance
            domain_score = self._domain_relevance(
                parsed.get("skill_categories", {}), job.get("domain", "")
            )

            # 5. Combined score (weighted)
            combined = (
                skill_score * 0.35 +
                text_similarity * 0.25 +
                exp_score * 0.20 +
                domain_score * 0.20
            )

            scored_matches.append({
                **job,
                "final_score": round(min(100, combined), 1),
                "dimension_scores": {
                    "skills_match": round(skill_score, 1),
                    "semantic_similarity": round(text_similarity, 1),
                    "experience_alignment": round(exp_score, 1),
                    "domain_relevance": round(domain_score, 1),
                },
                "skill_details": {
                    "matched": skill_result.get("matched", []),
                    "missing": skill_result.get("missing", []),
                    "extra": skill_result.get("extra", []),
                },
            })

        # Sort by final score
        scored_matches.sort(key=lambda x: x["final_score"], reverse=True)

        # Overall employability score
        top_scores = [m["final_score"] for m in scored_matches[:5]]
        overall = sum(top_scores) / len(top_scores) if top_scores else 0

        # Aggregate dimension analysis
        dimension_avg = {"skills": 0, "experience": 0, "domain": 0, "semantic": 0}
        for m in scored_matches[:5]:
            ds = m["dimension_scores"]
            dimension_avg["skills"] += ds["skills_match"]
            dimension_avg["experience"] += ds["experience_alignment"]
            dimension_avg["domain"] += ds["domain_relevance"]
            dimension_avg["semantic"] += ds["semantic_similarity"]
        n = min(5, len(scored_matches)) or 1
        dimension_avg = {k: round(v / n, 1) for k, v in dimension_avg.items()}

        return {
            "scored_matches": scored_matches,
            "overall_employability": round(overall, 1),
            "dimension_averages": dimension_avg,
        }

    async def fallback(self, input_data: dict) -> dict:
        return {
            "scored_matches": input_data.get("job_matches", []),
            "overall_employability": 50.0,
            "dimension_averages": {
                "skills": 50, "experience": 50, "domain": 50, "semantic": 50
            },
        }

    def _experience_alignment(self, yoe: float, level: str) -> float:
        """Score how well candidate's experience matches the job level."""
        level_ranges = {
            "entry": (0, 2),
            "mid": (2, 6),
            "senior": (5, 15),
        }
        min_yoe, max_yoe = level_ranges.get(level, (0, 10))

        if min_yoe <= yoe <= max_yoe:
            return 90.0 + min(10, yoe)
        elif yoe < min_yoe:
            gap = min_yoe - yoe
            return max(30, 90 - gap * 15)
        else:
            gap = yoe - max_yoe
            return max(50, 85 - gap * 5)

    def _domain_relevance(self, skill_categories: dict, job_domain: str) -> float:
        """Score domain relevance based on skill category distribution."""
        domain_skill_map = {
            "data_science": ["data_science", "classical_ml", "deep_learning", "analytics"],
            "data_engineering": ["data_engineering", "big_data", "streaming", "etl"],
            "web": ["web_development", "frontend", "backend_frameworks"],
            "cloud_devops": ["cloud_devops", "containers", "cicd", "monitoring"],
            "management": ["soft_skills"],
        }

        relevant_categories = domain_skill_map.get(job_domain, [])
        if not relevant_categories:
            return 50.0

        found = sum(
            1 for cat in skill_categories
            if any(r in cat.lower() for r in relevant_categories)
        )
        return min(100, (found / max(len(relevant_categories), 1)) * 120)


matching_agent = MatchingAgent()
