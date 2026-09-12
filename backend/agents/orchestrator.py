"""
ResumeIQ v2 — Agent Orchestrator
Coordinates the multi-agent pipeline: Parser → Job → Matching → Critic → Explanation
"""

import time
import uuid
import json
import logging
from typing import Optional

from backend.agents.parser_agent import parser_agent
from backend.agents.job_agent import job_agent
from backend.agents.matching_agent import matching_agent
from backend.agents.critic_agent import critic_agent
from backend.agents.explanation_agent import explanation_agent
from backend.ai.gap_analyzer import gap_analyzer

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates the multi-agent pipeline for resume analysis.

    Pipeline:
    1. Parser Agent    → Extract structured data from resume
    2. Job Agent       → Analyze job requirements and initial matching
    3. Matching Agent  → Semantic resume-to-job matching with multi-dim scoring
    4. Critic Agent    → Review for fairness, bias, accuracy
    5. Explanation Agent → Generate human-readable explanations

    Each agent receives output from previous agents, creating a chain of reasoning.
    """

    def __init__(self):
        self.agents = [
            parser_agent,
            job_agent,
            matching_agent,
            critic_agent,
            explanation_agent,
        ]

    async def run_pipeline(self, raw_text: str, filename: str = "",
                            note: str = "") -> dict:
        """
        Run the full multi-agent pipeline on a resume.

        Args:
            raw_text: Extracted text from the resume
            filename: Original filename
            note: Version note

        Returns:
            Complete analysis result with agent logs
        """
        pipeline_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        agent_logs = []

        logger.info(f"═══ Pipeline {pipeline_id} starting ═══")

        # ── Stage 1: Parse Resume ────────────────────────────────────────────
        parse_result = await parser_agent.run({
            "raw_text": raw_text,
            "filename": filename,
        })
        agent_logs.append(parse_result)
        parsed = parse_result.get("output", {})

        # ── Stage 2: Job Understanding ───────────────────────────────────────
        job_result = await job_agent.run({
            "skills": parsed.get("skills", []),
            "years_of_experience": parsed.get("years_of_experience", 0),
        })
        agent_logs.append(job_result)
        job_data = job_result.get("output", {})

        # ── Stage 3: Semantic Matching ───────────────────────────────────────
        match_result = await matching_agent.run({
            "parsed_resume": parsed,
            "job_matches": job_data.get("top_matches", []),
        })
        agent_logs.append(match_result)
        match_data = match_result.get("output", {})

        # ── Stage 4: Build scores for critic ─────────────────────────────────
        scored_matches = match_data.get("scored_matches", [])
        overall_employability = match_data.get("overall_employability", 50)
        dim_avgs = match_data.get("dimension_averages", {})

        analysis_scores = {
            "overall_score": overall_employability,
            "skills_match_score": dim_avgs.get("skills", 50),
            "experience_match_score": dim_avgs.get("experience", 50),
            "domain_relevance_score": dim_avgs.get("domain", 50),
            "project_complexity_score": self._project_score(parsed),
            "format_score": self._format_score(parsed),
            "skills_found": parsed.get("skills", []),
            "skills_missing": scored_matches[0].get("skill_details", {}).get("missing", [])
                              if scored_matches else [],
            "scores": dim_avgs,
        }

        # ── Stage 5: Critic Review ───────────────────────────────────────────
        critic_result = await critic_agent.run({
            "parsed_resume": parsed,
            "analysis_scores": analysis_scores,
            "job_matches": scored_matches,
        })
        agent_logs.append(critic_result)
        critic_data = critic_result.get("output", {})

        # ── Stage 6: Generate Explanations ───────────────────────────────────
        explain_result = await explanation_agent.run({
            "parsed_resume": parsed,
            "analysis_scores": analysis_scores,
            "job_matches": scored_matches,
            "critic_review": critic_data,
        })
        agent_logs.append(explain_result)
        explain_data = explain_result.get("output", {})

        # ── Build Career DNA ─────────────────────────────────────────────────
        career_dna = self._build_career_dna(parsed.get("skills", []))

        # ── Stage 7: Smart Gap Analysis + Roadmap ─────────────────────────
        target_role = scored_matches[0].get("job_title", "Software Engineer") if scored_matches else "Software Engineer"
        gap_data = gap_analyzer.analyze(
            current_skills=parsed.get("skills", []),
            target_role=target_role,
            job_matches=scored_matches
        )

        total_time = int((time.time() - start_time) * 1000)
        logger.info(f"═══ Pipeline {pipeline_id} completed in {total_time}ms ═══")

        return {
            "pipeline_id": pipeline_id,
            "parsed": {
                "name": parsed.get("name"),
                "email": parsed.get("email"),
                "phone": parsed.get("phone"),
                "linkedin": parsed.get("linkedin"),
                "github": parsed.get("github"),
                "years_of_experience": parsed.get("years_of_experience", 0),
                "language": parsed.get("language", "en"),
                "skills": parsed.get("skills", []),
                "inferred_skills": parsed.get("inferred_skills", []),
                "skill_categories": parsed.get("skill_categories", {}),
                "skill_graph_mappings": parsed.get("skill_graph_mappings", []),
                "section_flags": parsed.get("section_flags", {}),
            },
            "scores": {
                "overall_score": round(overall_employability, 1),
                "skills_match": round(analysis_scores["skills_match_score"], 1),
                "experience_match": round(analysis_scores["experience_match_score"], 1),
                "domain_relevance": round(analysis_scores["domain_relevance_score"], 1),
                "project_complexity": round(analysis_scores["project_complexity_score"], 1),
                "format_quality": round(analysis_scores["format_score"], 1),
                "confidence": round(critic_data.get("quality_score", 80) / 100, 2),
            },
            "career_dna": career_dna,
            "job_matches": scored_matches[:10],
            "explanation": explain_data,
            "bias_report": {
                "alerts": critic_data.get("bias_alerts", []),
                "corrections": critic_data.get("corrections", []),
                "quality_score": critic_data.get("quality_score", 80),
            },
            "skills_found": parsed.get("skills", []),
            "skills_missing": analysis_scores.get("skills_missing", []),
            "recommendations": explain_data.get("recommendations", []),
            "roadmap": gap_data.get("roadmap", []),
            "roadmap_summary": {
                "total_weeks": gap_data.get("total_learning_weeks", 0),
                "target_role": target_role,
                "projected_match": gap_data.get("projected_match", 0),
            },
            "agent_logs": [
                {
                    "agent": log.get("agent"),
                    "status": log.get("status"),
                    "duration_ms": log.get("duration_ms"),
                }
                for log in agent_logs
            ],
            "total_duration_ms": total_time,
            "note": note,
        }

    def _project_score(self, parsed: dict) -> float:
        """Score project complexity from parsed resume."""
        projects = parsed.get("projects", "")
        if not projects:
            return 20.0

        score = 40.0
        text = projects.lower()

        # Check for complexity indicators
        indicators = [
            ("deploy", 10), ("production", 10), ("scale", 8),
            ("api", 8), ("database", 7), ("machine learning", 10),
            ("model", 8), ("pipeline", 8), ("docker", 8),
            ("kubernetes", 10), ("aws", 8), ("gcp", 8),
            ("real-time", 10), ("million", 8), ("performance", 7),
        ]
        for keyword, points in indicators:
            if keyword in text:
                score += points

        return min(100, score)

    def _format_score(self, parsed: dict) -> float:
        """Score resume formatting quality."""
        flags = parsed.get("section_flags", {})
        required = ["education", "experience", "skills", "summary"]
        present = sum(1 for s in required if flags.get(s))
        base = (present / len(required)) * 60

        # Bonuses
        if parsed.get("email"):
            base += 10
        if parsed.get("phone"):
            base += 5
        if parsed.get("linkedin"):
            base += 10
        if parsed.get("github"):
            base += 5
        if flags.get("projects"):
            base += 5
        if flags.get("certifications"):
            base += 5

        return min(100, base)

    def _build_career_dna(self, skills: list) -> dict:
        """Build Career DNA radar chart data."""
        DNA_ARCHETYPES = {
            "The Builder": ["python", "flask", "django", "fastapi", "docker",
                            "kubernetes", "rest api", "sql", "postgresql", "redis"],
            "The Data Wizard": ["machine learning", "deep learning", "pandas", "numpy",
                                "scikit-learn", "tensorflow", "pytorch", "statistics", "r"],
            "The Cloud Architect": ["aws", "gcp", "azure", "terraform", "kubernetes",
                                    "ci/cd", "microservices", "serverless", "docker"],
            "The Data Engineer": ["spark", "kafka", "airflow", "etl", "data pipeline",
                                  "snowflake", "bigquery", "databricks", "dbt"],
            "The Storyteller": ["tableau", "power bi", "matplotlib", "seaborn",
                                "plotly", "d3.js", "data visualization"],
            "The AI Whisperer": ["nlp", "llm", "rag", "transformers", "bert", "gpt",
                                 "hugging face", "computer vision", "generative ai"],
            "The Full-Stack": ["react", "angular", "vue", "node.js", "html",
                               "css", "javascript", "typescript", "graphql"],
            "The DevOps Ninja": ["ci/cd", "jenkins", "github actions", "ansible",
                                 "helm", "terraform", "grafana", "docker", "prometheus"],
        }

        found_set = set(s.lower() for s in skills)
        dna = {}
        for archetype, cluster in DNA_ARCHETYPES.items():
            overlap = len(found_set & set(cluster))
            score = round(min(100.0, (overlap / len(cluster)) * 100), 1)
            dna[archetype] = {
                "score": score,
                "matched_skills": sorted(list(found_set & set(cluster))),
                "total_in_cluster": len(cluster),
            }
        return dna


# ── Singleton ────────────────────────────────────────────────────────────────────
orchestrator = AgentOrchestrator()
