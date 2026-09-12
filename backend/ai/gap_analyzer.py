"""
ResumeIQ v2 — Smart Gap Analyzer + Roadmap Generator
Detects skill gaps and generates personalized learning roadmaps.
"""

import logging
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)

# ── Learning resource templates ──────────────────────────────────────────────────
LEARNING_RESOURCES = {
    "docker": {
        "estimated_weeks": 2,
        "prerequisites": [],
        "resources": [
            {"type": "Course", "name": "Docker for Beginners", "platform": "Udemy", "url": "https://www.udemy.com/topic/docker/"},
            {"type": "Hands-on", "name": "Play with Docker", "url": "https://labs.play-with-docker.com/"},
            {"type": "Project", "name": "Containerize your ML model"},
        ],
    },
    "kubernetes": {
        "estimated_weeks": 3,
        "prerequisites": ["docker"],
        "resources": [
            {"type": "Course", "name": "Kubernetes for Developers", "platform": "Coursera"},
            {"type": "Hands-on", "name": "Minikube Tutorial", "url": "https://minikube.sigs.k8s.io/docs/start/"},
            {"type": "Project", "name": "Deploy app on K8s cluster"},
        ],
    },
    "aws": {
        "estimated_weeks": 4,
        "prerequisites": [],
        "resources": [
            {"type": "Course", "name": "AWS Cloud Practitioner", "platform": "AWS Skill Builder"},
            {"type": "Certification", "name": "AWS Certified Cloud Practitioner"},
            {"type": "Hands-on", "name": "AWS Free Tier Labs"},
        ],
    },
    "machine learning": {
        "estimated_weeks": 8,
        "prerequisites": ["python", "statistics"],
        "resources": [
            {"type": "Course", "name": "Machine Learning Specialization", "platform": "Coursera", "instructor": "Andrew Ng"},
            {"type": "Book", "name": "Hands-On ML with Scikit-Learn (Aurélien Géron)"},
            {"type": "Project", "name": "Build an end-to-end ML pipeline"},
        ],
    },
    "deep learning": {
        "estimated_weeks": 6,
        "prerequisites": ["machine learning", "python"],
        "resources": [
            {"type": "Course", "name": "Deep Learning Specialization", "platform": "Coursera"},
            {"type": "Course", "name": "fast.ai Practical Deep Learning"},
            {"type": "Project", "name": "Fine-tune a pre-trained model"},
        ],
    },
    "mlops": {
        "estimated_weeks": 4,
        "prerequisites": ["machine learning", "docker"],
        "resources": [
            {"type": "Course", "name": "MLOps Specialization", "platform": "Coursera"},
            {"type": "Tool", "name": "MLflow Quickstart", "url": "https://mlflow.org/"},
            {"type": "Project", "name": "Build ML pipeline with CI/CD"},
        ],
    },
    "terraform": {
        "estimated_weeks": 2,
        "prerequisites": ["aws"],
        "resources": [
            {"type": "Course", "name": "Terraform Associate Cert Prep", "platform": "HashiCorp Learn"},
            {"type": "Hands-on", "name": "Terraform Tutorials", "url": "https://developer.hashicorp.com/terraform/tutorials"},
        ],
    },
    "react": {
        "estimated_weeks": 4,
        "prerequisites": ["javascript", "html", "css"],
        "resources": [
            {"type": "Course", "name": "React - The Complete Guide", "platform": "Udemy"},
            {"type": "Docs", "name": "Official React Docs", "url": "https://react.dev/"},
            {"type": "Project", "name": "Build a full-stack React app"},
        ],
    },
    "sql": {
        "estimated_weeks": 2,
        "prerequisites": [],
        "resources": [
            {"type": "Course", "name": "SQL for Data Science", "platform": "Coursera"},
            {"type": "Practice", "name": "LeetCode SQL Problems", "url": "https://leetcode.com/problemset/database/"},
        ],
    },
    "llm": {
        "estimated_weeks": 4,
        "prerequisites": ["deep learning", "nlp"],
        "resources": [
            {"type": "Course", "name": "LLM University", "platform": "Cohere"},
            {"type": "Hands-on", "name": "Build a RAG app with LangChain"},
            {"type": "Project", "name": "Fine-tune an LLM on custom data"},
        ],
    },
    "ci/cd": {
        "estimated_weeks": 2,
        "prerequisites": ["git"],
        "resources": [
            {"type": "Course", "name": "GitHub Actions CI/CD", "platform": "GitHub Learning"},
            {"type": "Project", "name": "Set up CI/CD for a Python project"},
        ],
    },
}

# Default resource template
DEFAULT_RESOURCE = {
    "estimated_weeks": 3,
    "prerequisites": [],
    "resources": [
        {"type": "Search", "name": "Learn {skill}", "url": "https://www.google.com/search?q=learn+{skill}+course+2025"},
    ],
}


class GapAnalyzer:
    """
    Smart Skill Gap Analyzer with Personalized Roadmap Generation.

    Capabilities:
    - Detect skill gaps relative to target roles
    - Prioritize gaps by job market demand
    - Generate personalized learning roadmaps with time estimates
    - Track prerequisite chains
    - Predict impact of learning each skill
    """

    def analyze(self, current_skills: list[str], target_role: str,
                job_matches: list[dict] = None) -> dict:
        """
        Perform gap analysis for a target role.

        Args:
            current_skills: Skills the candidate currently has
            target_role: Target job role
            job_matches: Optional job match data for context

        Returns:
            Comprehensive gap analysis with learning roadmap
        """
        current_set = set(s.lower() for s in current_skills)

        # Find target role requirements from job matches
        target_skills = self._get_target_skills(target_role, job_matches)
        target_set = set(s.lower() for s in target_skills)

        # Compute gaps
        direct_match = current_set & target_set
        missing = target_set - current_set
        extra = current_set - target_set

        # Check for semantic equivalents
        semantic_matches = []
        truly_missing = set()
        for m_skill in missing:
            found_equiv = False
            for e_skill in extra:
                if skill_graph.find_equivalent_skills(m_skill, e_skill):
                    semantic_matches.append({"have": e_skill, "equivalent_to": m_skill})
                    found_equiv = True
                    break
            if not found_equiv:
                truly_missing.add(m_skill)

        # Prioritize missing skills
        prioritized = self._prioritize_gaps(truly_missing, target_role)

        # Generate learning roadmap
        roadmap = self._generate_roadmap(prioritized, current_set)

        # Predict impact
        match_now = len(direct_match) + len(semantic_matches)
        match_total = len(target_set)
        current_pct = round((match_now / max(match_total, 1)) * 100, 1)
        projected_pct = min(100, round(((match_now + len(truly_missing)) / max(match_total, 1)) * 100, 1))

        # Total learning time
        total_weeks = sum(step.get("estimated_weeks", 3) for step in roadmap)

        return {
            "target_role": target_role,
            "current_match": current_pct,
            "projected_match": projected_pct,
            "skills_matched": sorted(list(direct_match)),
            "semantic_matches": semantic_matches,
            "skills_missing": prioritized,
            "total_gaps": len(truly_missing),
            "roadmap": roadmap,
            "total_learning_weeks": total_weeks,
            "quick_wins": [s for s in prioritized if s.get("priority") == "high"][:3],
        }

    def _get_target_skills(self, role: str, job_matches: list = None) -> list[str]:
        """Get required skills for a target role."""
        # Check job matches first
        if job_matches:
            for match in job_matches:
                if match.get("job_title", "").lower() == role.lower():
                    return match.get("required_skills", [])

        # Fallback: generic role skills
        role_skills = {
            "data scientist": ["python", "machine learning", "sql", "pandas", "numpy",
                               "scikit-learn", "statistics", "matplotlib", "deep learning"],
            "ml engineer": ["python", "machine learning", "tensorflow", "pytorch",
                            "docker", "aws", "mlops", "rest api", "ci/cd"],
            "data engineer": ["python", "sql", "spark", "kafka", "airflow", "etl",
                              "aws", "docker", "data pipeline"],
            "full-stack developer": ["javascript", "react", "node.js", "python",
                                     "sql", "html", "css", "docker", "rest api"],
            "devops engineer": ["docker", "kubernetes", "ci/cd", "terraform", "aws",
                                "python", "jenkins", "helm", "monitoring"],
            "genai engineer": ["python", "llm", "rag", "langchain", "hugging face",
                               "docker", "rest api", "vector database"],
        }
        return role_skills.get(role.lower(), ["python", "sql", "docker", "aws", "rest api"])

    def _prioritize_gaps(self, missing: set, role: str) -> list[dict]:
        """Prioritize missing skills by importance."""
        high_demand = {"python", "sql", "docker", "aws", "machine learning",
                       "kubernetes", "rest api", "ci/cd", "react"}
        medium_demand = {"terraform", "kafka", "spark", "pytorch", "tensorflow",
                         "mlops", "gcp", "azure"}

        prioritized = []
        for skill in sorted(missing):
            if skill in high_demand:
                priority = "high"
                impact = "+8-12% match improvement"
            elif skill in medium_demand:
                priority = "medium"
                impact = "+4-7% match improvement"
            else:
                priority = "low"
                impact = "+2-4% match improvement"

            resolved = skill_graph.resolve_skill(skill)
            prioritized.append({
                "skill": skill,
                "priority": priority,
                "impact": impact,
                "category": resolved["category"] if resolved else "General",
            })

        # Sort: high → medium → low
        order = {"high": 0, "medium": 1, "low": 2}
        prioritized.sort(key=lambda x: order.get(x["priority"], 3))

        return prioritized

    def _generate_roadmap(self, prioritized: list, current_skills: set) -> list[dict]:
        """Generate a learning roadmap with time estimates and resources."""
        roadmap = []

        for gap in prioritized[:10]:  # Top 10 gaps
            skill = gap["skill"]
            resource_data = LEARNING_RESOURCES.get(skill, DEFAULT_RESOURCE)

            # Check prerequisites  
            prereqs = resource_data.get("prerequisites", [])
            prereq_status = []
            for p in prereqs:
                prereq_status.append({
                    "skill": p,
                    "met": p.lower() in current_skills,
                })

            # Adjust time if prerequisites unmet
            unmet_prereqs = [p for p in prereq_status if not p["met"]]
            extra_weeks = len(unmet_prereqs) * 2

            step = {
                "skill": skill,
                "priority": gap["priority"],
                "impact": gap["impact"],
                "estimated_weeks": resource_data["estimated_weeks"] + extra_weeks,
                "prerequisites": prereq_status,
                "resources": [
                    {**r, "name": r["name"].replace("{skill}", skill)}
                    for r in resource_data["resources"]
                ],
            }

            if unmet_prereqs:
                step["note"] = f"Learn {', '.join(p['skill'] for p in unmet_prereqs)} first"

            roadmap.append(step)

        return roadmap


# ── Singleton ────────────────────────────────────────────────────────────────────
gap_analyzer = GapAnalyzer()
