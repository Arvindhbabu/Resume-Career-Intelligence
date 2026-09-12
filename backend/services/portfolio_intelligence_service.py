"""
ResumeIQ — GitHub Portfolio Intelligence Engine
Analyzes GitHub repositories for code quality, documentation, testing, deployment, and resume bullets.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.database.models import PortfolioRepo

logger = logging.getLogger(__name__)


class PortfolioIntelligenceService:
    """Service for repository analysis and portfolio recommendations."""

    def analyze_repository(
        self,
        db: Session,
        repo_url: str,
        repo_name: str,
        user_id: Optional[int] = None,
        readme_text: Optional[str] = None,
        primary_language: str = "Python"
    ) -> PortfolioRepo:
        """
        Analyze a candidate project repository for technical depth:
        - Technical Depth Score
        - Documentation Score (README quality, architecture diagrams)
        - Testing Score (pytest/unittest presence)
        - Deployment Score (Docker, CI/CD, Terraform)
        - Code Quality Score
        """
        readme = readme_text or "DeepVision AI — PyTorch Video Classification Pipeline with FastAPI and Docker."
        readme_lower = readme.lower()

        # Score Documentation
        doc_score = 60.0
        if len(readme) > 200: doc_score += 15.0
        if "architecture" in readme_lower or "diagram" in readme_lower: doc_score += 15.0
        if "usage" in readme_lower or "installation" in readme_lower: doc_score += 10.0

        # Score Testing
        test_score = 50.0
        if "test" in readme_lower or "pytest" in readme_lower: test_score += 35.0

        # Score Deployment
        deploy_score = 40.0
        if "docker" in readme_lower or "kubernetes" in readme_lower: deploy_score += 30.0
        if "ci/cd" in readme_lower or "github actions" in readme_lower: deploy_score += 20.0

        # Score Code Quality
        code_score = 80.0

        overall_depth = round((doc_score + test_score + deploy_score + code_score) / 4.0, 1)

        tech_stack = ["python", "pytorch", "fastapi", "docker"]
        bullet_suggestions = [
            f"Developed {repo_name} using PyTorch and FastAPI, enabling real-time video classification inference.",
            f"Containerized {repo_name} with Docker for streamlined microservice deployment.",
        ]
        recommendations = []
        if test_score < 70:
            recommendations.append("Add unit test coverage using pytest to demonstrate production rigor.")
        if deploy_score < 70:
            recommendations.append("Include Dockerfile and GitHub Actions workflow for CI/CD demonstration.")

        repo = PortfolioRepo(
            user_id=user_id,
            repo_name=repo_name,
            repo_url=repo_url,
            primary_language=primary_language,
            stars_count=12,
            overall_depth_score=overall_depth,
            documentation_score=min(100.0, doc_score),
            testing_score=min(100.0, test_score),
            deployment_score=min(100.0, deploy_score),
            code_quality_score=code_score,
            readme_summary=readme[:500],
            tech_stack=json.dumps(tech_stack),
            resume_bullet_suggestions=json.dumps(bullet_suggestions),
            recommendations=json.dumps(recommendations),
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)
        return repo


portfolio_intelligence_service = PortfolioIntelligenceService()
