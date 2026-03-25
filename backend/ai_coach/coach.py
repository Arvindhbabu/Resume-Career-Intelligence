"""
ResumeIQ — AI Interview Prep Coach
Generates tailored interview questions from a parsed resume using an LLM.
Falls back to a curated rule-based bank if no API key is configured.
"""

import os
import json
import logging
import random

logger = logging.getLogger(__name__)

# ── Curated fallback question bank ────────────────────────────────────────────
FALLBACK_QUESTIONS = {
    "behavioral": [
        {"q": "Tell me about a time you solved a complex technical problem under pressure.", "difficulty": "Medium"},
        {"q": "Describe a project where you had to learn a new technology quickly.", "difficulty": "Medium"},
        {"q": "Give an example of how you handled a conflict within a team.", "difficulty": "Medium"},
        {"q": "Tell me about your most impactful project and why it mattered.", "difficulty": "Hard"},
        {"q": "Describe a situation where you had to prioritise multiple deadlines.", "difficulty": "Hard"},
    ],
    "python": [
        {"q": "What is the difference between a list and a tuple in Python?", "difficulty": "Easy"},
        {"q": "Explain Python's GIL and how it affects multi-threading.", "difficulty": "Hard"},
        {"q": "How do generators differ from regular functions? When would you use one?", "difficulty": "Medium"},
        {"q": "Describe Python's memory management and garbage collection.", "difficulty": "Hard"},
    ],
    "machine learning": [
        {"q": "Explain the bias-variance tradeoff with a real example.", "difficulty": "Medium"},
        {"q": "How would you handle a heavily imbalanced dataset?", "difficulty": "Medium"},
        {"q": "Walk me through how gradient descent works.", "difficulty": "Medium"},
        {"q": "What's the difference between L1 and L2 regularisation?", "difficulty": "Medium"},
        {"q": "How would you detect and handle data leakage in a pipeline?", "difficulty": "Hard"},
    ],
    "deep learning": [
        {"q": "Explain the vanishing gradient problem and how to mitigate it.", "difficulty": "Hard"},
        {"q": "What are attention mechanisms and why are they important in transformers?", "difficulty": "Hard"},
        {"q": "Compare CNNs vs RNNs for sequence modelling tasks.", "difficulty": "Medium"},
    ],
    "sql": [
        {"q": "What is the difference between INNER JOIN and LEFT JOIN?", "difficulty": "Easy"},
        {"q": "How would you optimise a slow SQL query on a table with 100M rows?", "difficulty": "Hard"},
        {"q": "Explain window functions and give a practical use case.", "difficulty": "Medium"},
    ],
    "aws": [
        {"q": "Describe the difference between EC2, Lambda, and Fargate.", "difficulty": "Medium"},
        {"q": "How would you design a fault-tolerant data pipeline on AWS?", "difficulty": "Hard"},
    ],
    "docker": [
        {"q": "What is the difference between a Docker image and a container?", "difficulty": "Easy"},
        {"q": "How do you reduce Docker image size in production?", "difficulty": "Medium"},
    ],
    "default": [
        {"q": "What motivated you to pursue a career in technology?", "difficulty": "Easy"},
        {"q": "How do you stay current with developments in your field?", "difficulty": "Easy"},
        {"q": "Where do you see yourself in 3 years?", "difficulty": "Easy"},
    ],
}


class InterviewCoach:
    """
    Generates interview questions tailored to the candidate's skills and target role.
    Uses LLM API if key is available, otherwise rule-based fallback.
    """

    def __init__(self):
        self.api_key      = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.use_gemini   = bool(os.getenv("GEMINI_API_KEY"))
        self.use_openai   = bool(os.getenv("OPENAI_API_KEY"))

    def generate(self, parsed: dict, target_role: str, num_questions: int = 10) -> list[dict]:
        """
        Returns a list of interview questions:
        [{q, hint, difficulty, category}, ...]
        """
        if self.use_gemini:
            return self._gemini_generate(parsed, target_role, num_questions)
        elif self.use_openai:
            return self._openai_generate(parsed, target_role, num_questions)
        else:
            return self._fallback_generate(parsed.get("skills", []), num_questions)

    # ── LLM: Gemini ────────────────────────────────────────────────────────────
    def _gemini_generate(self, parsed: dict, role: str, n: int) -> list[dict]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model  = genai.GenerativeModel("gemini-1.5-flash")
            prompt = self._build_prompt(parsed, role, n)
            resp   = model.generate_content(prompt)
            return self._parse_llm_response(resp.text)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return self._fallback_generate(parsed.get("skills", []), n)

    # ── LLM: OpenAI ────────────────────────────────────────────────────────────
    def _openai_generate(self, parsed: dict, role: str, n: int) -> list[dict]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = self._build_prompt(parsed, role, n)
            resp   = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return self._parse_llm_response(resp.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return self._fallback_generate(parsed.get("skills", []), n)

    # ── Prompt builder ─────────────────────────────────────────────────────────
    def _build_prompt(self, parsed: dict, role: str, n: int) -> str:
        name   = parsed.get("name", "the candidate")
        skills = ", ".join(parsed.get("skills", [])[:20])
        exp    = parsed.get("years_of_experience", 0)
        return f"""
You are an expert technical interviewer. Generate {n} interview questions for
a candidate applying for the role of "{role}".

Candidate profile:
- Name: {name}
- Skills: {skills}
- Estimated experience: {exp} years
- Has projects: {bool(parsed.get("projects"))}

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "q": "<question text>",
      "hint": "<what a good answer covers, 1 sentence>",
      "difficulty": "Easy|Medium|Hard",
      "category": "<Behavioral|Technical|System Design|Domain>"
    }}
  ]
}}

Mix: 3 behavioral, 5 technical (based on their skills), 2 domain/role-specific.
Make questions specific to their skill set, not generic.
"""

    def _parse_llm_response(self, text: str) -> list[dict]:
        try:
            clean = text.strip().replace("```json", "").replace("```", "")
            data  = json.loads(clean)
            return data.get("questions", [])
        except Exception:
            return []

    # ── Rule-based fallback ────────────────────────────────────────────────────
    def _fallback_generate(self, skills: list[str], n: int) -> list[dict]:
        pool = list(FALLBACK_QUESTIONS["behavioral"])
        pool.extend(FALLBACK_QUESTIONS["default"])

        for skill in skills:
            for key, qs in FALLBACK_QUESTIONS.items():
                if key in skill.lower() or skill.lower() in key:
                    pool.extend(qs)

        random.shuffle(pool)
        result = []
        for q in pool[:n]:
            result.append({
                "q":          q["q"],
                "hint":       "Think about a concrete example from your experience.",
                "difficulty": q.get("difficulty", "Medium"),
                "category":   "Technical" if q in pool[2:] else "Behavioral",
            })
        return result


coach = InterviewCoach()
