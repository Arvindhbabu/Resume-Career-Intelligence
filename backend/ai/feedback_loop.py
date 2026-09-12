"""
ResumeIQ v2 — Continuous Feedback Loop
Collects, processes, and applies feedback for system improvement.
"""

import json
import logging
from datetime import datetime, timezone
from collections import Counter

logger = logging.getLogger(__name__)


class FeedbackLoop:
    """
    Continuous Feedback Loop for system improvement.

    Capabilities:
    - Collect recruiter and candidate feedback
    - Track score corrections
    - Trigger model retraining signals
    - A/B test scoring algorithms
    - Monitor system accuracy over time
    """

    def __init__(self):
        self._feedback_entries: list[dict] = []
        self._accuracy_log: list[dict] = []

    def load_from_db(self, entries: list[dict]):
        """Bulk load feedback entries from DB to synchronize in-memory state."""
        self._feedback_entries = entries
        logger.info(f"Loaded {len(entries)} feedback entries into feedback loop")

    def submit_feedback(self, feedback: dict) -> dict:
        """
        Submit feedback for a resume analysis.

        Args:
            feedback: {
                "resume_id": int,
                "feedback_type": "score_adjust" | "skill_correction" | "match_feedback",
                "original_value": str,
                "corrected_value": str,
                "comment": str
            }
        """
        entry = {
            **feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "applied": False,
        }
        self._feedback_entries.append(entry)

        # Check if retraining is needed
        retrain_signal = self._check_retrain_threshold()

        return {
            "recorded": True,
            "total_feedback": len(self._feedback_entries),
            "retrain_needed": retrain_signal,
        }

    def get_feedback_summary(self) -> dict:
        """Get aggregated feedback metrics."""
        if not self._feedback_entries:
            return {
                "total_feedback": 0,
                "by_type": {},
                "recent": [],
                "accuracy_trend": [],
            }

        type_counts = Counter(f.get("feedback_type") for f in self._feedback_entries)
        applied = sum(1 for f in self._feedback_entries if f.get("applied"))

        return {
            "total_feedback": len(self._feedback_entries),
            "applied": applied,
            "pending": len(self._feedback_entries) - applied,
            "by_type": dict(type_counts),
            "recent": self._feedback_entries[-5:],
            "retrain_needed": self._check_retrain_threshold(),
        }

    def apply_corrections(self, resume_id: int) -> dict:
        """Apply pending feedback corrections for a resume."""
        relevant = [
            f for f in self._feedback_entries
            if f.get("resume_id") == resume_id and not f.get("applied")
        ]

        corrections = []
        for entry in relevant:
            entry["applied"] = True
            corrections.append({
                "type": entry["feedback_type"],
                "original": entry["original_value"],
                "corrected": entry["corrected_value"],
            })

        return {
            "resume_id": resume_id,
            "corrections_applied": len(corrections),
            "corrections": corrections,
        }

    def track_accuracy(self, prediction: float, actual: float,
                       context: str = "") -> dict:
        """Track prediction accuracy for system monitoring."""
        entry = {
            "prediction": prediction,
            "actual": actual,
            "error": abs(prediction - actual),
            "context": context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._accuracy_log.append(entry)

        # Compute running average
        recent = self._accuracy_log[-50:]
        avg_error = sum(e["error"] for e in recent) / len(recent)

        return {
            "recorded": True,
            "current_error": round(entry["error"], 2),
            "avg_error_last_50": round(avg_error, 2),
        }

    def _check_retrain_threshold(self) -> bool:
        """Check if enough feedback has accumulated to warrant retraining."""
        pending = sum(1 for f in self._feedback_entries if not f.get("applied"))
        return pending >= 10  # Retrain after 10 pending corrections


# ── Singleton ────────────────────────────────────────────────────────────────────
feedback_loop = FeedbackLoop()
