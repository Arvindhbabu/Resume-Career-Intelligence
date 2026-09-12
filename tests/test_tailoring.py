"""
Unit tests for Evidence-Grounded Resume Tailoring & Document Generation.
"""

import os
from backend.services.resume_tailor_service import resume_tailor_service
from backend.services.document_generator import document_generator_service
from backend.services.cover_letter_service import cover_letter_service
from backend.database.models import Resume, CareerProfile, SkillEvidence


def test_no_fabrication_resume_tailoring(db_session):
    # Setup master resume
    resume = Resume(
        user_token="test-tailor-token",
        filename="master_resume.pdf",
        raw_text="Alice Johnson\nSenior Data Scientist\nExperience in Python, SQL, and PyTorch."
    )
    db_session.add(resume)
    db_session.flush()

    # Setup profile with evidence for Python and PyTorch (NOT AWS)
    profile = CareerProfile(full_name="Alice Johnson", user_token="test-tailor-token")
    db_session.add(profile)
    db_session.flush()

    db_session.add(SkillEvidence(profile_id=profile.id, skill_name="Python", evidence_type="resume", confidence=1.0))
    db_session.add(SkillEvidence(profile_id=profile.id, skill_name="PyTorch", evidence_type="github_repo", confidence=0.95))
    db_session.commit()

    required_job_skills = ["Python", "PyTorch", "AWS"]

    tailored = resume_tailor_service.tailor_resume_for_job(
        db_session,
        master_resume_id=resume.id,
        target_job_title="Lead AI Engineer",
        target_company="Google",
        required_job_skills=required_job_skills,
        profile_id=profile.id
    )

    assert tailored["no_fabrication_guarantee"] is True
    assert "Python" in tailored["structured_content"]["verified_skills"]
    assert len(tailored["unsupported_claims_flagged"]) == 1
    assert tailored["unsupported_claims_flagged"][0]["skill"] == "AWS"
    assert "INSUFFICIENT EVIDENCE" in tailored["unsupported_claims_flagged"][0]["status"]


def test_pdf_docx_generation():
    sample_content = {
        "name": "Jane Doe",
        "title": "Senior Data Scientist",
        "summary": "Experienced Data Scientist specializing in Deep Learning.",
        "verified_skills": ["Python", "PyTorch", "FastAPI"],
        "bullets": ["Spearheaded PyTorch model deployment increasing throughput by 40%."]
    }

    pdf_path = document_generator_service.generate_pdf(sample_content, "test_resume.pdf")
    assert os.path.exists(pdf_path)

    docx_path = document_generator_service.generate_docx(sample_content, "test_resume.docx")
    assert os.path.exists(docx_path)


def test_cover_letter_generation():
    cl = cover_letter_service.generate_cover_letter(
        candidate_name="Jane Doe",
        target_role="Senior Data Scientist",
        target_company="OpenAI",
        verified_skills=["Python", "PyTorch", "LLMs"],
        achievements=["Increased training efficiency by 40%."]
    )

    assert len(cl["sections"]) == 5
    assert "Jane Doe" in cl["cover_letter_text"]
    assert "OpenAI" in cl["cover_letter_text"]
    assert "Python" in cl["cover_letter_text"]
