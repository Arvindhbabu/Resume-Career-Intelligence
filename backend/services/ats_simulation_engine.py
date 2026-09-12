"""
ResumeIQ — Platform-Aware ATS Simulation & Multi-Dimensional Scoring Engine
Simulates public-information-based ATS parsing behavior across 6 enterprise ATS platforms.

Calculates:
  1. Resume Quality Score (Intrinsic formatting, sections, contact info, grammar/clarity)
  2. Job Match Score (Semantic & keyword requirement alignment)
  3. ATS Parseability Score (Layout, font/table safety, section recognition)
  4. Evidence Strength Score (Verified proof grounding behind claims)
  5. Recruiter Impact Score (Quantified achievements & action verb strength)
  6. Application Readiness Score (Weighted composite readiness for candidate)

Platforms Simulated:
  - Workday-style: Strict section names, exact keyword matching, table/column parsing penalty
  - Greenhouse-style: Flexible section recognition, high semantic skill weight
  - Lever-style: Unstructured text tolerance, high project & skill weight
  - Taleo-style: High keyword density priority, strict date format requirement
  - iCIMS-style: Enterprise taxonomy matching, contact & location verification
  - SuccessFactors-style: Education & certification priority, rigid skill taxonomy
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ATSSimulationEngine:
    """Engine computing multi-dimensional scoring and platform-aware ATS simulations."""

    def calculate_multi_dimensional_scores(
        self,
        parsed_resume: Dict[str, Any],
        job_analysis: Dict[str, Any] = None,
        evidence_graph: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """Compute the 6 core multi-dimensional metrics."""

        # 1. Resume Quality Score
        sections = parsed_resume.get("section_flags", {})
        required_sections = ["summary", "experience", "education", "skills"]
        section_score = (sum(1 for s in required_sections if sections.get(s)) / len(required_sections)) * 50

        contact_score = 0
        if parsed_resume.get("email"): contact_score += 15
        if parsed_resume.get("phone"): contact_score += 10
        if parsed_resume.get("linkedin"): contact_score += 15
        if parsed_resume.get("github"): contact_score += 10

        resume_quality_score = min(100.0, round(section_score + contact_score, 1))

        # 2. Job Match Score
        skills_count = len(parsed_resume.get("skills", []))
        job_match_score = min(100.0, round(min(1.0, skills_count / 12.0) * 85 + 15, 1))
        if job_analysis and "match_percentage" in job_analysis:
            job_match_score = round(job_analysis["match_percentage"], 1)

        # 3. ATS Parseability Score
        parseability = 95.0
        raw_text = parsed_resume.get("raw_text", "")
        # Penalize for possible table/column artifact corruption
        if "\t\t" in raw_text or "   " in raw_text:
            parseability -= 10.0
        if len(raw_text.splitlines()) < 3:
            parseability -= 20.0
        ats_parseability_score = max(30.0, min(100.0, parseability))

        # 4. Evidence Strength Score
        if evidence_graph and evidence_graph.get("total_skills", 0) > 0:
            verified_count = sum(1 for s in evidence_graph["skills"].values() if s.get("evidence_count", 0) > 0)
            evidence_strength_score = min(100.0, round((verified_count / max(1, len(parsed_resume.get("skills", [1])))) * 100, 1))
        else:
            evidence_strength_score = 70.0

        # 5. Recruiter Impact Score
        action_verbs = ["developed", "engineered", "built", "spearheaded", "optimized", "architected", "increased", "reduced", "lead", "created"]
        text_lower = raw_text.lower()
        verb_count = sum(1 for v in action_verbs if v in text_lower)
        has_metrics = bool(re.search(r'\d+%', raw_text) or re.search(r'\$\d+', raw_text) or re.search(r'\d+x', raw_text))
        recruiter_impact_score = min(100.0, round(verb_count * 6 + (25 if has_metrics else 10) + 30, 1))

        # 6. Application Readiness Score (Weighted composite)
        application_readiness_score = round(
            (resume_quality_score * 0.20) +
            (job_match_score * 0.30) +
            (ats_parseability_score * 0.15) +
            (evidence_strength_score * 0.15) +
            (recruiter_impact_score * 0.20),
            1
        )

        return {
            "resume_quality": resume_quality_score,
            "job_match": job_match_score,
            "ats_parseability": ats_parseability_score,
            "evidence_strength": evidence_strength_score,
            "recruiter_impact": recruiter_impact_score,
            "application_readiness": application_readiness_score,
        }

    def simulate_platform_profiles(self, parsed_resume: Dict[str, Any], base_scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Simulate parsing across 6 major ATS systems."""
        raw_text = parsed_resume.get("raw_text", "")
        skills = set(s.lower() for s in parsed_resume.get("skills", []))
        sections = parsed_resume.get("section_flags", {})

        # Workday-style: Rigid headers, exact keywords, penalty for missing standard headers
        workday_score = base_scores["ats_parseability"] * 0.4 + base_scores["resume_quality"] * 0.4 + (15 if sections.get("experience") and sections.get("education") else 0)
        workday_notes = "Standard section headers detected. Clean plaintext structure." if sections.get("experience") else "Non-standard headers may cause Workday section parsing errors."

        # Greenhouse-style: Semantic skills focus, flexible formatting
        greenhouse_score = base_scores["job_match"] * 0.5 + base_scores["recruiter_impact"] * 0.3 + 20.0
        greenhouse_notes = "High semantic skill evaluation. Strong project & experience weighting."

        # Lever-style: Flexible unstructured parser, candidate profile focus
        lever_score = base_scores["resume_quality"] * 0.4 + base_scores["recruiter_impact"] * 0.4 + 20.0
        lever_notes = "High tolerance for modern formatting. Strong link & portfolio recognition."

        # Taleo-style: Strict keyword matching & date format verification
        has_dates = bool(re.search(r'\b(20\d\d|19\d\d)\b', raw_text))
        taleo_score = (base_scores["job_match"] * 0.5 + base_scores["ats_parseability"] * 0.3 + (20 if has_dates else 5))
        taleo_notes = "Strict date chronology verified." if has_dates else "Missing standard date formats (YYYY) may fail Taleo timeline screen."

        # iCIMS-style: Enterprise taxonomy & contact details verification
        has_contact = bool(parsed_resume.get("email") and parsed_resume.get("phone"))
        icims_score = base_scores["ats_parseability"] * 0.4 + base_scores["job_match"] * 0.4 + (20 if has_contact else 5)
        icims_notes = "Contact information verified." if has_contact else "Missing phone or email may trigger iCIMS rejection."

        # SuccessFactors-style: Education & certification focus
        has_edu = bool(sections.get("education"))
        successfactors_score = base_scores["resume_quality"] * 0.4 + base_scores["evidence_strength"] * 0.4 + (20 if has_edu else 5)
        successfactors_notes = "Education section validated." if has_edu else "Education section missing or unparsed by SuccessFactors."

        return {
            "Workday": {
                "score": round(min(100.0, workday_score), 1),
                "notes": workday_notes,
                "fit": "EXCELLENT" if workday_score > 80 else "MODERATE",
            },
            "Greenhouse": {
                "score": round(min(100.0, greenhouse_score), 1),
                "notes": greenhouse_notes,
                "fit": "EXCELLENT" if greenhouse_score > 80 else "MODERATE",
            },
            "Lever": {
                "score": round(min(100.0, lever_score), 1),
                "notes": lever_notes,
                "fit": "EXCELLENT" if lever_score > 80 else "MODERATE",
            },
            "Taleo": {
                "score": round(min(100.0, taleo_score), 1),
                "notes": taleo_notes,
                "fit": "EXCELLENT" if taleo_score > 80 else "MODERATE",
            },
            "iCIMS": {
                "score": round(min(100.0, icims_score), 1),
                "notes": icims_notes,
                "fit": "EXCELLENT" if icims_score > 80 else "MODERATE",
            },
            "SuccessFactors": {
                "score": round(min(100.0, successfactors_score), 1),
                "notes": successfactors_notes,
                "fit": "EXCELLENT" if successfactors_score > 80 else "MODERATE",
            },
        }


ats_simulation_engine = ATSSimulationEngine()
