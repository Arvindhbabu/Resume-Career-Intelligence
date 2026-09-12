"""
ResumeIQ v2 — Resume Parser Agent
Extracts structured data from resumes with semantic understanding.
Uses LLM for intelligent parsing, with rule-based fallback.
"""

import re
import logging
from backend.agents.base_agent import BaseAgent
from backend.ai.skill_graph import skill_graph

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    name = "parser_agent"
    description = "Extracts structured data from resumes with semantic understanding"

    async def execute(self, input_data: dict) -> dict:
        """
        Parse a resume using LLM for semantic understanding.

        Input: {"raw_text": str, "filename": str}
        Output: {"name", "email", "skills", "experience", "education", ...}
        """
        raw_text = input_data.get("raw_text", "")

        # Try LLM-powered parsing first
        llm_result = self.call_llm(
            prompt=self._build_prompt(raw_text),
            system_prompt=(
                "You are an expert resume parser. Extract structured information "
                "from the resume text. Return valid JSON only."
            ),
            response_format="json"
        )

        parsed = self.parse_llm_json(llm_result)
        if parsed and parsed.get("name"):
            # Enhance with skill graph
            parsed["skill_graph_mappings"] = self._map_skills_to_graph(
                parsed.get("skills", [])
            )
            return parsed

        # If LLM failed, use fallback
        return await self.fallback(input_data)

    async def fallback(self, input_data: dict) -> dict:
        """Rule-based resume parsing (enhanced from v1)."""
        raw_text = input_data.get("raw_text", "")
        text_lower = raw_text.lower()
        lines = raw_text.splitlines()

        # Extract contact info
        email = self._find_pattern(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", raw_text
        )
        phone = self._find_pattern(
            r"(\+?\d[\d\s\-().]{7,15}\d)", raw_text
        )
        linkedin = self._find_pattern(
            r"linkedin\.com/in/[\w\-]+", raw_text
        )
        github = self._find_pattern(
            r"github\.com/[\w\-]+", raw_text
        )

        # Extract name (first meaningful line)
        name = self._extract_name(lines)

        # Extract skills using skill graph (semantic)
        skill_results = skill_graph.extract_skills_semantic(text_lower)
        skills = list({s["skill"] for s in skill_results})
        skill_categories = {}
        for s in skill_results:
            cat = s.get("category", "other")
            if cat not in skill_categories:
                skill_categories[cat] = []
            skill_categories[cat].append(s["skill"])

        # Extract sections
        sections = self._extract_sections(raw_text)

        # Estimate experience
        yoe = self._estimate_experience(raw_text)

        # Inferred skills from the graph
        all_inferred = set()
        for s in skill_results:
            all_inferred.update(s.get("inferred_skills", []))
        inferred_skills = list(all_inferred - set(skills))

        result = {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "skills": skills,
            "skill_categories": skill_categories,
            "inferred_skills": inferred_skills,
            "skill_graph_mappings": [s for s in skill_results],
            "education": sections.get("education", ""),
            "experience": sections.get("experience", ""),
            "projects": sections.get("projects", ""),
            "certifications": sections.get("certifications", ""),
            "summary": sections.get("summary", ""),
            "years_of_experience": yoe,
            "section_flags": self._check_sections(text_lower),
            "language": self._detect_language(raw_text),
            "raw_text": raw_text,
        }

        return result

    def _build_prompt(self, text: str) -> str:
        return f"""
Parse this resume and extract structured information. Return JSON:

{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1234567890",
  "linkedin": "linkedin.com/in/name",
  "github": "github.com/name",
  "skills": ["skill1", "skill2"],
  "years_of_experience": 3,
  "education": "University, Degree, Year",
  "experience": "Summary of work experience",
  "projects": "Summary of key projects",
  "summary": "Professional summary",
  "certifications": "Any certifications"
}}

Resume text:
{text[:3000]}
"""

    def _find_pattern(self, pattern: str, text: str) -> str | None:
        m = re.search(pattern, text, re.I)
        return m.group(0) if m else None

    def _extract_name(self, lines: list[str]) -> str:
        """Enhanced name extraction using spaCy if available, with heuristic fallback."""
        try:
            from backend.parser.pdf_parser import nlp as spacy_nlp, NLP_SUPPORT
            if NLP_SUPPORT:
                doc = spacy_nlp("\n".join(lines[:10]))
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                        return ent.text
        except Exception as e:
            logger.debug(f"spaCy name extraction failed: {e}")

        email_re = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        phone_re = re.compile(r"(\+?\d[\d\s\-().]{7,15}\d)")

        for line in lines[:8]:
            line = line.strip()
            if (line and 2 <= len(line.split()) <= 4 and not email_re.search(line)
                    and not phone_re.search(line)
                    and not any(k in line.lower() for k in ("resume", "curriculum", "cv", "http", "page"))):
                return line
        return "Unknown"

    def _detect_language(self, text: str) -> str:
        """Detect language script (English, Tamil, Hindi)."""
        # Tamil range: U+0B80–U+0BFF
        if re.search(r"[\u0b80-\u0bff]", text):
            return "ta"
        # Devanagari (Hindi) range: U+0900–U+097F
        if re.search(r"[\u0900-\u097f]", text):
            return "hi"
        return "en"

    def _extract_sections(self, text: str) -> dict:
        section_patterns = {
            "education": r"(?i)(education|academic|qualification)",
            "experience": r"(?i)(experience|employment|work history|career)",
            "skills": r"(?i)(skill|technical|competenc|expertise)",
            "projects": r"(?i)(project|portfolio|work sample)",
            "certifications": r"(?i)(certif|course|training|credential|award)",
            "summary": r"(?i)(summary|objective|profile|about)",
        }

        sections = {}
        lines = text.splitlines()

        for section, pattern in section_patterns.items():
            capturing, buffer, found = False, [], False
            for line in lines:
                if re.search(pattern, line) and len(line.strip()) < 60:
                    capturing = True
                    found = True
                    continue
                if capturing:
                    is_header = any(
                        re.search(p, line) and len(line.strip()) < 60
                        for k, p in section_patterns.items() if k != section
                    )
                    if is_header:
                        break
                    buffer.append(line)
            sections[section] = "\n".join(buffer).strip() if found else ""

        return sections

    def _estimate_experience(self, text: str) -> float:
        years = [int(y) for y in re.findall(r"\b(19|20)\d{2}\b", text)
                 if 1990 <= int(y) <= 2030]
        if len(years) >= 2:
            return float(max(years) - min(years))
        return 0.0

    def _check_sections(self, text_lower: str) -> dict:
        patterns = {
            "education": r"(?i)(education|academic)",
            "experience": r"(?i)(experience|employment)",
            "skills": r"(?i)(skill|technical)",
            "projects": r"(?i)(project|portfolio)",
            "certifications": r"(?i)(certif|course|training)",
            "summary": r"(?i)(summary|objective|profile)",
        }
        return {s: bool(re.search(p, text_lower)) for s, p in patterns.items()}

    def _map_skills_to_graph(self, skills: list[str]) -> list[dict]:
        """Map extracted skills to the skill ontology graph."""
        mappings = []
        for skill in skills:
            resolved = skill_graph.resolve_skill(skill)
            if resolved:
                mappings.append({
                    "skill": skill,
                    **resolved,
                })
        return mappings


parser_agent = ParserAgent()
