"""
ResumeIQ v2 — FAISS Vector Store
Manages vector indices for semantic search over resumes and jobs.
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Lazy-loaded FAISS
_faiss = None


def _get_faiss():
    global _faiss
    if _faiss is None:
        try:
            import faiss
            _faiss = faiss
            logger.info("FAISS loaded ✓")
        except ImportError:
            logger.warning("FAISS not installed — vector search disabled.")
    return _faiss


class VectorStore:
    """
    FAISS-based vector store for semantic search.

    Supports:
    - Adding resume/job embeddings with metadata
    - k-NN similarity search
    - Persistent save/load of indices
    - Fallback to numpy cosine similarity if FAISS unavailable
    """

    def __init__(self, name: str = "resumes", dimension: int = 384):
        self.name = name
        self.dimension = dimension
        self.index = None
        self.metadata: list[dict] = []  # Parallel metadata for each vector
        self._initialized = False

    def _ensure_index(self):
        """Initialize the FAISS index if not already done."""
        if self._initialized:
            return

        faiss = _get_faiss()
        if faiss:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine with normalized vectors)
            logger.info(f"FAISS index '{self.name}' initialized (dim={self.dimension})")
        else:
            self.index = None
            logger.info(f"Using numpy fallback for '{self.name}'")

        # Try loading persisted index
        self._load()
        self._initialized = True

    def add(self, vector: list[float], metadata: dict):
        """Add a vector with associated metadata."""
        self._ensure_index()

        vec_np = np.array([vector], dtype=np.float32)

        faiss = _get_faiss()
        if faiss and self.index is not None:
            self.index.add(vec_np)
        self.metadata.append(metadata)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        """
        Search for the most similar vectors.

        Returns:
            List of {metadata: ..., score: float, rank: int}
        """
        self._ensure_index()

        if not self.metadata:
            return []

        query_np = np.array([query_vector], dtype=np.float32)

        faiss = _get_faiss()
        if faiss and self.index is not None:
            scores, indices = self.index.search(query_np, min(top_k, len(self.metadata)))
            results = []
            for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                results.append({
                    "metadata": self.metadata[idx],
                    "score": float(score),
                    "rank": rank + 1,
                })
            return results
        else:
            return self._numpy_search(query_np, top_k)

    def _numpy_search(self, query_np: np.ndarray, top_k: int) -> list[dict]:
        """Fallback search using numpy cosine similarity."""
        if not self.metadata:
            return []

        vectors = np.array(
            [m.get("_vector", [0.0] * self.dimension) for m in self.metadata],
            dtype=np.float32
        )

        # Cosine similarity
        query_flat = query_np.flatten()
        norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_flat)
        norms[norms == 0] = 1e-10
        similarities = np.dot(vectors, query_flat) / norms

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                "metadata": {k: v for k, v in self.metadata[idx].items() if k != "_vector"},
                "score": float(similarities[idx]),
                "rank": rank + 1,
            })
        return results

    def save(self):
        """Persist the index and metadata to disk."""
        settings = get_settings()
        save_dir = Path(settings.FAISS_INDEX_PATH)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        meta_path = save_dir / f"{self.name}_metadata.json"
        clean_metadata = [
            {k: v for k, v in m.items() if k != "_vector"}
            for m in self.metadata
        ]
        with open(meta_path, "w") as f:
            json.dump(clean_metadata, f)

        # Save FAISS index
        faiss = _get_faiss()
        if faiss and self.index is not None and self.index.ntotal > 0:
            index_path = save_dir / f"{self.name}.index"
            faiss.write_index(self.index, str(index_path))
            logger.info(f"Saved {self.name} index: {self.index.ntotal} vectors")

    def _load(self):
        """Load persisted index and metadata from disk."""
        settings = get_settings()
        save_dir = Path(settings.FAISS_INDEX_PATH)

        meta_path = save_dir / f"{self.name}_metadata.json"
        if meta_path.exists():
            try:
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded {len(self.metadata)} metadata entries for '{self.name}'")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")

        faiss = _get_faiss()
        index_path = save_dir / f"{self.name}.index"
        if faiss and index_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self.index = faiss.IndexFlatIP(self.dimension)

    @property
    def count(self) -> int:
        return len(self.metadata)

    def clear(self):
        """Clear the index and metadata."""
        self._initialized = False
        self.metadata = []
        self.index = None
        self._ensure_index()


# ── Pre-built stores ─────────────────────────────────────────────────────────────
resume_store = VectorStore("resumes")
job_store = VectorStore("jobs")
