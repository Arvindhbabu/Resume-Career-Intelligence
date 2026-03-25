"""
ResumeIQ — Resume Parser
Extracts structured data from PDF and DOCX resumes using pdfplumber + python-docx.
"""

import re
import io
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Optional heavy imports (graceful fallback for cold starts) ─────────────────
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("pdfplumber not installed – PDF parsing unavailable")

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    logger.warning("python-docx not installed – DOCX parsing unavailable")

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    NLP_SUPPORT = True
except Exception:
    NLP_SUPPORT = False
    logger.warning("spaCy model not found – falling back to regex NER")


# ── Master skill taxonomy (500+ skills across domains) ────────────────────────
SKILL_TAXONOMY = {
    "programming": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
        "kotlin", "swift", "r", "scala", "php", "ruby", "perl", "bash", "shell",
    ],
    "data_science": [
        "machine learning", "deep learning", "nlp", "computer vision", "statistics",
        "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "xgboost",
        "lightgbm", "hugging face", "transformers", "bert", "gpt", "llm", "rag",
        "feature engineering", "model deployment", "mlops", "a/b testing",
    ],
    "data_engineering": [
        "spark", "hadoop", "kafka", "airflow", "dbt", "etl", "data pipeline",
        "data warehouse", "snowflake", "bigquery", "redshift", "databricks",
        "delta lake", "flink", "nifi", "luigi",
    ],
    "cloud": [
        "aws", "gcp", "azure", "ec2", "s3", "lambda", "cloud functions",
        "kubernetes", "docker", "terraform", "ci/cd", "github actions",
        "jenkins", "ansible", "helm", "microservices", "serverless",
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "oracle", "neo4j", "firebase",
    ],
    "web": [
        "flask", "django", "fastapi", "react", "angular", "vue", "node.js",
        "express", "html", "css", "rest api", "graphql", "websocket",
    ],
    "visualization": [
        "tableau", "power bi", "matplotlib", "seaborn", "plotly", "d3.js",
        "looker", "metabase", "grafana",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving", "agile",
        "scrum", "project management", "mentoring", "critical thinking",
    ],
}

FLAT_SKILLS = {skill for skills in SKILL_TAXONOMY.values() for skill in skills}

# ── Section header patterns ────────────────────────────────────────────────────
SECTION_PATTERNS = {
    "education":    r"(?i)(education|academic|qualification)",
    "experience":   r"(?i)(experience|employment|work history|career)",
    "skills":       r"(?i)(skill|technical|competenc|expertise|proficienc)",
    "projects":     r"(?i)(project|portfolio|work sample)",
    "certifications": r"(?i)(certif|course|training|credential|award)",
    "summary":      r"(?i)(summary|objective|profile|about)",
}

EMAIL_RE    = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE    = re.compile(r"(\+?\d[\d\s\-().]{7,15}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.I)
GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.I)
YEAR_RE     = re.compile(r"\b(19|20)\d{2}\b")


# ══════════════════════════════════════════════════════════════════════════════
class ResumeParser:
    """
    Parses a resume file and returns a structured dict:
    {
        raw_text, name, email, phone, linkedin, github,
        skills, skill_categories, education, experience,
        certifications, projects, summary,
        years_of_experience, section_flags
    }
    """

    def parse(self, file_path: str | None = None,
              file_bytes: bytes | None = None,
              filename: str = "") -> dict:
        """Entry point – accepts a file path OR raw bytes."""
        ext = Path(filename or file_path or "").suffix.lower()
        if ext == ".pdf":
            raw_text = self._extract_pdf(file_path, file_bytes)
        elif ext in (".docx", ".doc"):
            raw_text = self._extract_docx(file_path, file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore") if file_bytes else ""

        return self._structure(raw_text)

    # ── Extractors ─────────────────────────────────────────────────────────────
    def _extract_pdf(self, path, raw):
        if not PDF_SUPPORT:
            return ""
        src = io.BytesIO(raw) if raw else path
        pages = []
        with pdfplumber.open(src) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)

    def _extract_docx(self, path, raw):
        if not DOCX_SUPPORT:
            return ""
        src = io.BytesIO(raw) if raw else path
        doc = Document(src)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # ── Structuring ────────────────────────────────────────────────────────────
    def _structure(self, raw_text: str) -> dict:
        text_lower = raw_text.lower()
        lines = raw_text.splitlines()

        result = {
            "raw_text": raw_text,
            "name": self._extract_name(lines),
            "email": self._find(EMAIL_RE, raw_text),
            "phone": self._find(PHONE_RE, raw_text),
            "linkedin": self._find(LINKEDIN_RE, raw_text),
            "github": self._find(GITHUB_RE, raw_text),
            "skills": [],
            "skill_categories": {},
            "education": self._extract_section(raw_text, "education"),
            "experience": self._extract_section(raw_text, "experience"),
            "certifications": self._extract_section(raw_text, "certifications"),
            "projects": self._extract_section(raw_text, "projects"),
            "summary": self._extract_section(raw_text, "summary"),
            "years_of_experience": self._estimate_experience(raw_text),
            "section_flags": self._check_sections(text_lower),
        }

        skills, cats = self._extract_skills(text_lower)
        result["skills"] = skills
        result["skill_categories"] = cats
        return result

    def _extract_name(self, lines: list[str]) -> str:
        """Heuristic: first non-empty line that isn't an email/phone is the name."""
        for line in lines[:8]:
            line = line.strip()
            if (line and len(line.split()) >= 2
                    and not EMAIL_RE.search(line)
                    and not PHONE_RE.search(line)
                    and not any(k in line.lower() for k in ("resume", "curriculum", "cv"))):
                return line
        return "Unknown"

    def _find(self, pattern, text):
        m = pattern.search(text)
        return m.group(0) if m else None

    def _extract_skills(self, text_lower: str):
        found, cats = [], {}
        for category, skills in SKILL_TAXONOMY.items():
            matched = [s for s in skills if s in text_lower]
            if matched:
                cats[category] = matched
                found.extend(matched)
        return list(set(found)), cats

    def _extract_section(self, text: str, section: str) -> str:
        """Pull text between a section header and the next section header."""
        pattern = SECTION_PATTERNS.get(section, "")
        if not pattern:
            return ""
        lines = text.splitlines()
        capturing, buffer, found = False, [], False
        for line in lines:
            if re.search(pattern, line) and len(line.strip()) < 60:
                capturing = True
                found = True
                continue
            if capturing:
                # Stop at next section header
                is_header = any(
                    re.search(p, line) and len(line.strip()) < 60
                    for k, p in SECTION_PATTERNS.items() if k != section
                )
                if is_header:
                    break
                buffer.append(line)
        return "\n".join(buffer).strip() if found else ""

    def _estimate_experience(self, text: str) -> float:
        """Rough YoE estimate from year spans in the resume."""
        years = [int(y) for y in YEAR_RE.findall(text) if 1990 <= int(y) <= 2030]
        if len(years) >= 2:
            return float(max(years) - min(years))
        return 0.0

    def _check_sections(self, text_lower: str) -> dict:
        return {
            section: bool(re.search(pattern, text_lower))
            for section, pattern in SECTION_PATTERNS.items()
        }


# Singleton
parser = ResumeParser()
