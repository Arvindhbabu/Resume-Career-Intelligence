"""
ResumeIQ v2 — Semantic Embedding Engine
SBERT-based embeddings for semantic resume understanding.

Replaces TF-IDF with dense vector representations that capture meaning, not just keywords.
Uses sentence-transformers (free, local, no API key needed).
"""

import json
import logging
import numpy as np
from typing import Optional

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Lazy-loaded model
_model = None
_model_name = None


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model, _model_name
    settings = get_settings()

    if _model is None or _model_name != settings.EMBEDDING_MODEL:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}...")
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            _model_name = settings.EMBEDDING_MODEL
            logger.info(f"Embedding model loaded ✓ (dim={_model.get_sentence_embedding_dimension()})")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback TF-IDF embeddings.")
            _model = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            _model = None

    return _model


class EmbeddingEngine:
    """
    Semantic embedding engine using SBERT.

    Capabilities:
    1. Encode resume text → dense vector (384-dim with MiniLM)
    2. Encode skill descriptions → vectors for semantic matching
    3. Compute semantic similarity between any two texts
    4. Batch encoding for efficiency
    5. Fallback to simple bag-of-words when SBERT unavailable
    """

    def encode(self, text: str) -> list[float]:
        """
        Encode a text string into a dense embedding vector.

        Args:
            text: Any text (resume, job description, skill phrase)

        Returns:
            List of floats (embedding vector)
        """
        model = _get_model()

        if model is not None:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        else:
            return self._fallback_encode(text)

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode multiple texts efficiently in a single batch."""
        model = _get_model()

        if model is not None:
            embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
            return embeddings.tolist()
        else:
            return [self._fallback_encode(t) for t in texts]

    def similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute semantic similarity between two texts.
        Returns float between 0 (unrelated) and 1 (identical meaning).
        """
        vec_a = np.array(self.encode(text_a))
        vec_b = np.array(self.encode(text_b))
        return float(np.dot(vec_a, vec_b))

    def similarity_vectors(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two pre-computed vectors."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def encode_resume(self, parsed: dict) -> list[float]:
        """
        Create a comprehensive embedding for a parsed resume.
        Combines multiple sections with weighted importance.
        """
        sections = []

        # Skills (most important)
        skills = parsed.get("skills", [])
        if skills:
            sections.append(f"Technical skills: {', '.join(skills[:30])}")

        # Summary
        summary = parsed.get("summary", "")
        if summary:
            sections.append(f"Professional summary: {summary[:500]}")

        # Experience
        experience = parsed.get("experience", "")
        if experience:
            sections.append(f"Work experience: {experience[:500]}")

        # Projects
        projects = parsed.get("projects", "")
        if projects:
            sections.append(f"Projects: {projects[:500]}")

        # Education
        education = parsed.get("education", "")
        if education:
            sections.append(f"Education: {education[:300]}")

        combined_text = " | ".join(sections) if sections else parsed.get("raw_text", "")[:1500]
        return self.encode(combined_text)

    def encode_job(self, job: dict) -> list[float]:
        """
        Create an embedding for a job description.
        """
        parts = [
            f"Job title: {job.get('title', '')}",
            f"Required skills: {', '.join(job.get('skills', []))}",
            f"Domain: {job.get('domain', '')}",
        ]
        if job.get("description"):
            parts.append(f"Description: {job['description'][:500]}")

        return self.encode(" | ".join(parts))

    def semantic_skill_match(self, resume_skills: list[str],
                              required_skills: list[str]) -> dict:
        """
        Semantic skill matching — understands that "PyTorch" is similar to "TensorFlow".

        Returns:
            {
                "score": 0.85,
                "matched": [{"resume": "pytorch", "required": "tensorflow", "similarity": 0.82}],
                "missing": ["docker"],
                "extra": ["kubernetes"]
            }
        """
        from backend.ai.skill_graph import skill_graph

        resume_set = set(s.lower() for s in resume_skills)
        required_set = set(s.lower() for s in required_skills)

        matched = []
        remaining_required = set()
        
        # 1. Direct & Synonym Matches (Graph-aware)
        for req in required_set:
            found = False
            for res in resume_set:
                if req == res or skill_graph.find_equivalent_skills(req, res):
                    matched.append({
                        "resume": res,
                        "required": req,
                        "similarity": 1.0,
                        "method": "exact_or_synonym"
                    })
                    found = True
                    resume_set.discard(res)
                    break
            if not found:
                remaining_required.add(req)
        
        # 2. Hierarchical Matches (Parent-Child in Graph)
        remaining_resume = list(resume_set)
        for req in list(remaining_required):
            best_graph_sim = 0.0
            best_match = None
            for res in remaining_resume:
                g_sim = skill_graph.compute_skill_similarity(req, res)
                if g_sim > best_graph_sim:
                    best_graph_sim = g_sim
                    best_match = res
            
            if best_graph_sim >= 0.7:  # High confidence hierarchical match
                matched.append({
                    "resume": best_match,
                    "required": req,
                    "similarity": round(best_graph_sim, 3),
                    "method": "hierarchical"
                })
                remaining_required.discard(req)
                if best_match in resume_set:
                    resume_set.discard(best_match)
                    remaining_resume.remove(best_match)

        # 3. Semantic matches for truly remaining skills (SBERT)
        if remaining_required and resume_set:
            required_list = list(remaining_required)
            resume_list = list(resume_set)

            req_vecs = self.encode_batch(required_list)
            res_vecs = self.encode_batch(resume_list)

            for i, req_skill in enumerate(required_list):
                best_sim = 0.0
                best_match = None
                for j, res_skill in enumerate(resume_list):
                    sim = self.similarity_vectors(req_vecs[i], res_vecs[j])
                    if sim > best_sim:
                        best_sim = sim
                        best_match = res_skill

                if best_sim >= 0.6:  # Threshold for semantic match
                    matched.append({
                        "resume": best_match,
                        "required": req_skill,
                        "similarity": round(best_sim, 3),
                    })
                    remaining_required.discard(req_skill)
                    remaining_resume.discard(best_match)

        total_required = len(required_skills) if required_skills else 1
        score = len(matched) / total_required

        return {
            "score": round(score * 100, 1),
            "matched": matched,
            "missing": list(remaining_required),
            "extra": list(remaining_resume),
        }

    def _fallback_encode(self, text: str) -> list[float]:
        """
        Simple bag-of-words fallback when SBERT is not available.
        Creates a fixed-size vector using character n-gram hashing.
        """
        dim = 384
        vector = [0.0] * dim
        words = text.lower().split()

        for word in words:
            # Hash each word to a dimension
            h = hash(word) % dim
            vector[h] += 1.0

        # Normalize
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def serialize_vector(self, vector: list[float]) -> str:
        """Serialize embedding vector to JSON string for DB storage."""
        return json.dumps([round(v, 6) for v in vector])

    def deserialize_vector(self, vector_str: str) -> list[float]:
        """Deserialize embedding vector from JSON string."""
        return json.loads(vector_str)


# ── Singleton ────────────────────────────────────────────────────────────────────
embedding_engine = EmbeddingEngine()
