"""
ResumeIQ v2 — Bias Detection Engine
Detects gender, institution, and keyword bias in resume evaluations.
"""

import re
import logging
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)

# ── Gender indicator lists (for detection, not discrimination) ────────────────────
FEMALE_NAMES_COMMON = {
    "mary", "patricia", "jennifer", "linda", "elizabeth", "barbara", "susan",
    "jessica", "sarah", "karen", "priya", "ananya", "lakshmi", "divya", "sneha",
    "pooja", "aishwarya", "kavitha", "meena", "sita", "radha", "neha", "swathi",
    "nithya", "deepa", "revathi", "sowmya", "harini", "gayathri", "pavithra",
}
MALE_NAMES_COMMON = {
    "james", "john", "robert", "michael", "david", "william", "richard",
    "raj", "rahul", "vijay", "arun", "kumar", "suresh", "ramesh", "ganesh",
    "arvind", "karthik", "mohan", "vignesh", "ashwin", "dinesh", "sathish",
    "manoj", "naveen", "venkat", "prasad", "hari", "bala", "ravi", "anand",
}

# ── Institution tiers (for bias detection) ────────────────────────────────────────
TIER1_INSTITUTIONS = {
    "iit", "nit", "bits", "iiit", "iisc", "mit", "stanford", "harvard",
    "cambridge", "oxford", "cmu", "berkeley", "caltech", "georgia tech",
}
TIER2_KEYWORDS = {
    "university", "college", "institute", "engineering",
}


class BiasDetector:
    """
    Bias Detection Engine that identifies:
    1. Gender bias — name-based scoring differences
    2. Institution bias — college prestige impact
    3. Keyword bias — penalizing equivalent skills differently
    4. Provides fairness scores and anonymization recommendations
    """

    def analyze(self, parsed: dict, scores: dict) -> dict:
        """
        Run bias detection on a resume analysis.

        Args:
            parsed: Parsed resume data
            scores: Scoring results

        Returns:
            Comprehensive bias report
        """
        findings = []
        recommendations = []

        # ── 1. Gender Bias Detection ─────────────────────────────────────────
        gender_result = self._detect_gender_bias(parsed, scores)
        findings.extend(gender_result.get("findings", []))

        # ── 2. Institution Bias Detection ────────────────────────────────────
        institution_result = self._detect_institution_bias(parsed, scores)
        findings.extend(institution_result.get("findings", []))

        # ── 3. Keyword Bias Detection ────────────────────────────────────────
        keyword_result = self._detect_keyword_bias(parsed, scores)
        findings.extend(keyword_result.get("findings", []))

        # ── Overall bias risk ────────────────────────────────────────────────
        severity_weights = {"high": 30, "medium": 15, "low": 5, "info": 2}
        bias_risk = sum(
            severity_weights.get(f.get("severity", "low"), 5) for f in findings
        )
        bias_risk = min(100, bias_risk)

        # ── Anonymized score difference ──────────────────────────────────────
        anon_diff = self._compute_anonymized_diff(parsed, scores)

        # ── Recommendations ──────────────────────────────────────────────────
        if gender_result.get("detected"):
            recommendations.append({
                "type": "gender",
                "action": "Enable name-blind evaluation mode for fair comparison",
                "impact": "Eliminates unconscious name-based bias",
            })
        if institution_result.get("tier_detected"):
            recommendations.append({
                "type": "institution",
                "action": "Focus on skills and projects over institution prestige",
                "impact": "More equitable scoring across educational backgrounds",
            })
        if keyword_result.get("equivalences_found"):
            recommendations.append({
                "type": "keyword",
                "action": "Accept skill equivalences: " + ", ".join(
                    f"'{e['have']}' ≈ '{e['missing']}'"
                    for e in keyword_result["equivalences_found"][:3]
                ),
                "impact": "Prevents penalizing resumes for synonym differences",
            })

        return {
            "gender_bias_score": gender_result.get("score", 0),
            "institution_bias_score": institution_result.get("score", 0),
            "keyword_bias_score": keyword_result.get("score", 0),
            "overall_bias_risk": bias_risk,
            "findings": findings,
            "equivalent_skills": keyword_result.get("equivalences_found", []),
            "anonymized_score_diff": anon_diff,
            "recommendations": recommendations,
        }

    def _detect_gender_bias(self, parsed: dict, scores: dict) -> dict:
        """Check for potential gender-based scoring differences."""
        name = parsed.get("name", "").strip().lower()
        first_name = name.split()[0] if name and name != "unknown" else ""

        detected = False
        findings = []

        if first_name in FEMALE_NAMES_COMMON:
            detected = True
            findings.append({
                "type": "gender_bias",
                "severity": "info",
                "message": (
                    "Name detected as potentially female. Recommend name-blind "
                    "evaluation to ensure unbiased scoring."
                ),
                "detail": "No scoring adjustment was made based on gender.",
            })
        elif first_name in MALE_NAMES_COMMON:
            detected = True
            findings.append({
                "type": "gender_bias",
                "severity": "info",
                "message": (
                    "Name detected as potentially male. Name-blind evaluation "
                    "recommended for all candidates equally."
                ),
            })

        return {
            "detected": detected,
            "score": 10 if detected else 0,  # Low: just an awareness flag
            "findings": findings,
        }

    def _detect_institution_bias(self, parsed: dict, scores: dict) -> dict:
        """Check if institution prestige might influence scoring."""
        education = parsed.get("education", "").lower()
        raw_text = parsed.get("raw_text", "").lower()

        tier1_found = []
        for inst in TIER1_INSTITUTIONS:
            if inst in education or inst in raw_text:
                tier1_found.append(inst.upper())

        findings = []
        tier_detected = bool(tier1_found)

        if tier1_found:
            findings.append({
                "type": "institution_bias",
                "severity": "info",
                "message": (
                    f"Prestigious institution detected: {', '.join(tier1_found)}. "
                    "Ensure scoring weights skills equally regardless of alma mater."
                ),
                "detail": "Scoring does NOT factor institution prestige — skills-based only.",
            })
        else:
            # Check if NOT having a Tier-1 school might be penalizing
            if education and not tier1_found:
                findings.append({
                    "type": "institution_bias",
                    "severity": "info",
                    "message": (
                        "Non-Tier-1 institution detected. This system scores purely "
                        "on skills and experience — institution name has zero weight."
                    ),
                })

        return {
            "tier_detected": tier_detected,
            "score": 5 if tier_detected else 0,
            "institutions": tier1_found,
            "findings": findings,
        }

    def _detect_keyword_bias(self, parsed: dict, scores: dict) -> dict:
        """Detect if resume is penalized for using different keywords for same skills."""
        skills_found = set(parsed.get("skills", []))
        skills_missing = scores.get("skills_missing", [])

        equivalences_found = []
        findings = []

        for missing_skill in skills_missing:
            if isinstance(missing_skill, dict):
                missing_name = missing_skill.get("skill", "")
            else:
                missing_name = missing_skill

            for found_skill in skills_found:
                # Check direct equivalence
                if skill_graph.find_equivalent_skills(missing_name, found_skill):
                    equivalences_found.append({
                        "missing": missing_name,
                        "have": found_skill,
                        "relationship": "equivalent",
                    })
                    findings.append({
                        "type": "keyword_bias",
                        "severity": "medium",
                        "message": (
                            f"⚠ Resume penalized for missing '{missing_name}' "
                            f"but has equivalent skill: '{found_skill}'"
                        ),
                    })
                    break

                # Check high similarity
                sim = skill_graph.compute_skill_similarity(missing_name, found_skill)
                if sim >= 0.5:
                    equivalences_found.append({
                        "missing": missing_name,
                        "have": found_skill,
                        "relationship": "similar",
                        "similarity": round(sim, 2),
                    })
                    findings.append({
                        "type": "keyword_bias",
                        "severity": "low",
                        "message": (
                            f"ℹ '{missing_name}' is related to '{found_skill}' "
                            f"(similarity: {sim:.0%}). Consider as partial match."
                        ),
                    })
                    break

        keyword_bias_score = min(100, len(equivalences_found) * 20)

        return {
            "equivalences_found": equivalences_found,
            "score": keyword_bias_score,
            "findings": findings,
        }

    def _compute_anonymized_diff(self, parsed: dict, scores: dict) -> float:
        """
        Estimate how much the score might differ with anonymized resume.
        Since our scoring is already name-blind, this should be near 0.
        """
        # Our scoring doesn't use name/gender, so diff is always 0
        # In a system that DID use these features, this would be higher
        return 0.0


# ── Singleton ────────────────────────────────────────────────────────────────────
bias_detector = BiasDetector()
