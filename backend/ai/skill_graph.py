"""
ResumeIQ v2 — Skill Graph Intelligence Engine
Hierarchical skill ontology with semantic resolution, inference, and similarity scoring.

Features:
    - Loads skill ontology from JSON knowledge graph
    - Resolves raw text mentions to canonical skill nodes
    - Infers parent/related skills (e.g., "TensorFlow CNN" → Deep Learning, Computer Vision)
    - Computes skill similarity using graph distance
    - Expands skill profiles with inferred competencies
"""

import json
import logging
from pathlib import Path
from collections import defaultdict

from backend.config import get_settings

logger = logging.getLogger(__name__)


class SkillNode:
    """A node in the skill ontology tree."""

    def __init__(self, name: str, display_name: str, depth: int = 0,
                 parent: "SkillNode | None" = None):
        self.name = name
        self.display_name = display_name
        self.depth = depth
        self.parent = parent
        self.children: dict[str, "SkillNode"] = {}
        self.skills: list[str] = []  # Leaf skills belonging to this category

    def path(self) -> list[str]:
        """Return full path from root to this node."""
        parts = []
        node = self
        while node:
            parts.append(node.display_name)
            node = node.parent
        return list(reversed(parts))

    def __repr__(self):
        return f"SkillNode({self.display_name}, depth={self.depth}, skills={len(self.skills)})"


class SkillGraphEngine:
    """
    Intelligent Skill Graph that understands skill relationships.

    Key capabilities:
    1. Resolve raw skill mentions → canonical names
    2. Infer parent categories (TensorFlow CNN → Deep Learning)
    3. Find related/similar skills
    4. Expand skill profiles with inferred competencies
    5. Compute skill-to-skill similarity via graph distance
    """

    def __init__(self):
        self._root: dict[str, SkillNode] = {}
        self._skill_to_node: dict[str, SkillNode] = {}  # skill -> category node
        self._skill_to_canonical: dict[str, str] = {}  # alias -> canonical name
        self._all_skills: set[str] = set()
        self._equivalences: dict[str, list[str]] = {}
        self._loaded = False

    def load(self):
        """Load skill ontology from JSON file."""
        if self._loaded:
            return

        settings = get_settings()
        ontology_path = Path(settings.SKILL_ONTOLOGY_PATH)

        if not ontology_path.exists():
            logger.warning(f"Skill ontology not found at {ontology_path}")
            return

        with open(ontology_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build tree from taxonomy
        taxonomy = data.get("taxonomy", {})
        for key, category_data in taxonomy.items():
            node = self._build_tree(key, category_data, depth=0, parent=None)
            self._root[key] = node

        # Load equivalences
        self._equivalences = data.get("equivalences", {})
        for canonical, aliases in self._equivalences.items():
            for alias in aliases:
                self._skill_to_canonical[alias.lower()] = canonical.lower()

        self._loaded = True
        logger.info(
            f"Skill graph loaded: {len(self._all_skills)} skills, "
            f"{len(self._skill_to_node)} mappings, "
            f"{len(self._equivalences)} equivalence groups"
        )

    def _build_tree(self, name: str, data: dict, depth: int,
                    parent: SkillNode | None) -> SkillNode:
        """Recursively build skill tree from ontology data."""
        display_name = data.get("display_name", name.replace("_", " ").title())
        node = SkillNode(name, display_name, depth, parent)

        # Register skills at this level
        for skill in data.get("skills", []):
            skill_lower = skill.lower()
            node.skills.append(skill_lower)
            self._skill_to_node[skill_lower] = node
            self._all_skills.add(skill_lower)
            self._skill_to_canonical[skill_lower] = skill_lower

        # Recurse into children
        for child_key, child_data in data.get("children", {}).items():
            child_node = self._build_tree(child_key, child_data, depth + 1, node)
            node.children[child_key] = child_node

        return node

    # ── Public API ──────────────────────────────────────────────────────────────

    def resolve_skill(self, raw_skill: str) -> dict | None:
        """
        Resolve a raw skill mention to its canonical form and position in the graph.

        Returns:
            {
                "canonical": "machine learning",
                "category": "Machine Learning",
                "parent": "Artificial Intelligence",
                "path": ["Artificial Intelligence", "Machine Learning"],
                "depth": 1
            }
        """
        self.load()
        skill_lower = raw_skill.lower().strip()

        # Check direct match
        if skill_lower in self._skill_to_node:
            node = self._skill_to_node[skill_lower]
            return {
                "canonical": skill_lower,
                "category": node.display_name,
                "parent": node.parent.display_name if node.parent else None,
                "path": node.path(),
                "depth": node.depth,
            }

        # Check equivalences
        canonical = self._skill_to_canonical.get(skill_lower)
        if canonical and canonical in self._skill_to_node:
            node = self._skill_to_node[canonical]
            return {
                "canonical": canonical,
                "category": node.display_name,
                "parent": node.parent.display_name if node.parent else None,
                "path": node.path(),
                "depth": node.depth,
            }

        # Fuzzy match: check if raw_skill is a substring of any known skill
        for known_skill in self._all_skills:
            if skill_lower in known_skill or known_skill in skill_lower:
                node = self._skill_to_node[known_skill]
                return {
                    "canonical": known_skill,
                    "category": node.display_name,
                    "parent": node.parent.display_name if node.parent else None,
                    "path": node.path(),
                    "depth": node.depth,
                }

        return None

    def extract_skills_semantic(self, text: str) -> list[dict]:
        """
        Extract skills from text using the ontology graph.
        More intelligent than simple keyword matching — understands context.

        Returns list of:
            {
                "skill": "tensorflow",
                "canonical": "tensorflow",
                "category": "Deep Learning Frameworks",
                "confidence": 0.95,
                "inferred_skills": ["deep learning", "neural networks"]
            }
        """
        self.load()
        text_lower = text.lower()
        found = []
        seen = set()

        # Direct skill matching
        for skill in self._all_skills:
            if skill in text_lower and skill not in seen:
                seen.add(skill)
                node = self._skill_to_node[skill]
                inferred = self._infer_parent_skills(skill)
                found.append({
                    "skill": skill,
                    "canonical": skill,
                    "category": node.display_name,
                    "parent": node.parent.display_name if node.parent else None,
                    "confidence": 1.0,
                    "inferred_skills": inferred,
                })

        # Check equivalences
        for alias, canonical in self._skill_to_canonical.items():
            if alias in text_lower and canonical not in seen and alias not in seen:
                seen.add(canonical)
                if canonical in self._skill_to_node:
                    node = self._skill_to_node[canonical]
                    inferred = self._infer_parent_skills(canonical)
                    found.append({
                        "skill": canonical,
                        "canonical": canonical,
                        "category": node.display_name,
                        "parent": node.parent.display_name if node.parent else None,
                        "confidence": 0.9,
                        "inferred_skills": inferred,
                    })

        return found

    def _infer_parent_skills(self, skill: str) -> list[str]:
        """
        Given a skill, infer higher-level competencies.
        E.g., "cnn" → ["deep learning", "computer vision", "machine learning"]
        """
        inferred = []
        if skill not in self._skill_to_node:
            return inferred

        node = self._skill_to_node[skill]
        parent = node.parent
        while parent:
            # Add category-level skills
            for parent_skill in parent.skills[:3]:
                if parent_skill != skill:
                    inferred.append(parent_skill)
            parent = parent.parent

        return inferred[:5]  # Cap at 5 inferred skills

    def get_related_skills(self, skill: str, max_results: int = 10) -> list[dict]:
        """
        Find skills related to the given skill (siblings in the graph).
        """
        self.load()
        skill_lower = skill.lower()
        resolved = self._skill_to_canonical.get(skill_lower, skill_lower)

        if resolved not in self._skill_to_node:
            return []

        node = self._skill_to_node[resolved]
        related = []

        # Sibling skills (same category)
        for sibling in node.skills:
            if sibling != resolved:
                related.append({
                    "skill": sibling,
                    "relationship": "sibling",
                    "category": node.display_name,
                })

        # Parent category skills
        if node.parent:
            for parent_skill in node.parent.skills:
                related.append({
                    "skill": parent_skill,
                    "relationship": "parent_category",
                    "category": node.parent.display_name,
                })

            # Cousin skills (other children of parent)
            for child_name, child_node in node.parent.children.items():
                if child_node.name != node.name:
                    for cousin_skill in child_node.skills[:3]:
                        related.append({
                            "skill": cousin_skill,
                            "relationship": "cousin",
                            "category": child_node.display_name,
                        })

        return related[:max_results]

    def compute_skill_similarity(self, skill_a: str, skill_b: str) -> float:
        """
        Compute similarity between two skills based on graph distance.
        Returns 0.0 (unrelated) to 1.0 (same skill).
        """
        self.load()
        a = self._skill_to_canonical.get(skill_a.lower(), skill_a.lower())
        b = self._skill_to_canonical.get(skill_b.lower(), skill_b.lower())

        if a == b:
            return 1.0

        node_a = self._skill_to_node.get(a)
        node_b = self._skill_to_node.get(b)

        if not node_a or not node_b:
            return 0.0

        # Find common ancestor depth
        path_a = set(id(n) for n in self._get_ancestors(node_a))
        path_b = self._get_ancestors(node_b)

        common_depth = 0
        for ancestor in path_b:
            if id(ancestor) in path_a:
                common_depth = ancestor.depth + 1
                break

        # Similarity based on graph distance
        max_depth = max(node_a.depth, node_b.depth, 1)
        return common_depth / (max_depth + 1)

    def _get_ancestors(self, node: SkillNode) -> list[SkillNode]:
        """Get all ancestors of a node from leaf to root."""
        ancestors = [node]
        while node.parent:
            ancestors.append(node.parent)
            node = node.parent
        return ancestors

    def get_skill_tree_summary(self) -> dict:
        """Return a summary of the full skill tree for visualization."""
        self.load()
        return {
            name: self._serialize_node(node)
            for name, node in self._root.items()
        }

    def _serialize_node(self, node: SkillNode) -> dict:
        result = {
            "name": node.display_name,
            "skills_count": len(node.skills),
            "skills_sample": node.skills[:5],
        }
        if node.children:
            result["children"] = {
                k: self._serialize_node(v) for k, v in node.children.items()
            }
        return result

    def find_equivalent_skills(self, skill_a: str, skill_b: str) -> bool:
        """Check if two skills are equivalent (aliases of each other)."""
        self.load()
        a = self._skill_to_canonical.get(skill_a.lower(), skill_a.lower())
        b = self._skill_to_canonical.get(skill_b.lower(), skill_b.lower())
        return a == b

    def get_all_skills_flat(self) -> set[str]:
        """Return all known skills as a flat set."""
        self.load()
        return self._all_skills.copy()


# ── Singleton ────────────────────────────────────────────────────────────────────
skill_graph = SkillGraphEngine()
