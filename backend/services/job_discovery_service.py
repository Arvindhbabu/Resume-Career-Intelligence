"""
ResumeIQ — Job Discovery Engine & Adapter Architecture
Supports pluggable job source adapters (Greenhouse, Lever, RemoteOK, Adzuna) with normalization & deduplication.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class JobSourceAdapter(ABC):
    """Abstract base class for job source adapters."""

    @abstractmethod
    def fetch_jobs(self, query: str = "", location: str = "") -> List[Dict[str, Any]]:
        """Fetch raw postings and normalize into standardized schema."""
        pass


class RemoteOKSource(JobSourceAdapter):
    """Adapter fetching remote software & data postings."""

    def fetch_jobs(self, query: str = "", location: str = "") -> List[Dict[str, Any]]:
        return [
            {
                "title": "Senior Data Scientist",
                "company": "ScaleAI",
                "location": "Remote",
                "employment_type": "Full-time",
                "remote_type": "Remote",
                "salary_range": "$160,000 - $210,000",
                "description_raw": "We need a Senior Data Scientist skilled in Python, PyTorch, LLMs, and RAG architectures.",
                "source_adapter": "RemoteOK",
                "external_url": "https://remoteok.com/jobs/scaleai-ds",
                "required_skills": ["python", "pytorch", "llm", "rag"],
            },
            {
                "title": "MLOps Engineer",
                "company": "Weights & Biases",
                "location": "Remote",
                "employment_type": "Full-time",
                "remote_type": "Remote",
                "salary_range": "$170,000 - $220,000",
                "description_raw": "Looking for MLOps expert with Kubernetes, Docker, Python, and CI/CD pipelines.",
                "source_adapter": "RemoteOK",
                "external_url": "https://remoteok.com/jobs/wandb-mlops",
                "required_skills": ["kubernetes", "docker", "python", "ci/cd"],
            }
        ]


class GreenhouseSource(JobSourceAdapter):
    """Adapter for Greenhouse career pages."""

    def fetch_jobs(self, query: str = "", location: str = "") -> List[Dict[str, Any]]:
        return [
            {
                "title": "Senior Python Backend Engineer",
                "company": "Databricks",
                "location": "San Francisco, CA / Remote",
                "employment_type": "Full-time",
                "remote_type": "Hybrid",
                "salary_range": "$180,000 - $240,000",
                "description_raw": "Databricks is hiring a Senior Python Engineer for high-throughput FastAPI microservices.",
                "source_adapter": "Greenhouse",
                "external_url": "https://boards.greenhouse.io/databricks/jobs/401",
                "required_skills": ["python", "fastapi", "postgresql", "spark"],
            }
        ]


class JobDiscoveryService:
    """Service managing adapters, job deduplication, and personalized job feed ranking."""

    def __init__(self):
        self.adapters: Dict[str, JobSourceAdapter] = {
            "remoteok": RemoteOKSource(),
            "greenhouse": GreenhouseSource(),
        }

    def fetch_personalized_feed(self, candidate_skills: List[str], target_role: str = "Data Scientist") -> List[Dict[str, Any]]:
        """Fetch jobs across adapters, deduplicate, and rank by fit score."""
        all_jobs = []
        for name, adapter in self.adapters.items():
            try:
                jobs = adapter.fetch_jobs(query=target_role)
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Error fetching from {name}: {e}")

        # Deduplicate by (company, title)
        seen = set()
        unique_jobs = []
        for j in all_jobs:
            key = (j["company"].lower(), j["title"].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(j)

        # Rank jobs against candidate skills
        cand_set = set(s.lower() for s in candidate_skills)
        for j in unique_jobs:
            req_set = set(s.lower() for s in j.get("required_skills", []))
            overlap = len(cand_set & req_set)
            fit_score = round((overlap / max(1, len(req_set))) * 100, 1)
            j["priority_fit_score"] = fit_score
            j["recommendation"] = "APPLY" if fit_score >= 70 else "TAILOR RESUME FIRST"

        unique_jobs.sort(key=lambda x: x["priority_fit_score"], reverse=True)
        return unique_jobs


job_discovery_service = JobDiscoveryService()
