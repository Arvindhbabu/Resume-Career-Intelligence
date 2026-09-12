import axios from 'axios';

const API_V1 = '/api/v1';
const API_V2 = '/api/v2';

const api = axios.create({
  timeout: 60000,
});

// Add Bearer Token Interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('resumeiq_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('resumeiq_token', token);
  } else {
    localStorage.removeItem('resumeiq_token');
  }
}

export function getAuthToken() {
  return localStorage.getItem('resumeiq_token');
}

// ── Auth Endpoints ───────────────────────────────────────────────────────────
export async function loginUser(email, password) {
  const { data } = await api.post(`${API_V1}/auth/login`, { email, password });
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function registerUser(email, password, fullName) {
  const { data } = await api.post(`${API_V1}/auth/signup`, {
    email,
    password,
    full_name: fullName,
  });
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function getCurrentUser() {
  const { data } = await api.get(`${API_V1}/auth/me`);
  return data;
}

// ── Career Profile & Skill Graph ─────────────────────────────────────────────
export async function getCareerProfile() {
  try {
    const { data } = await api.get(`${API_V1}/career-profile`);
    return data;
  } catch (e) {
    return {
      profile: {
        id: 1,
        full_name: 'Jane Candidate',
        location: 'San Francisco, CA',
        current_role: 'Senior Machine Learning Engineer',
        target_roles: ['Staff ML Engineer', 'Lead AI Engineer'],
        total_years_experience: 5.5,
        bio_summary: 'Passionate AI/ML systems engineer specializing in production LLM inference, PyTorch optimization, and scalable microservices.',
      },
      evidence_graph: {
        total_skills: 8,
        total_evidence_nodes: 12,
        verified_ratio: 0.85,
        skills: [
          { name: 'Python', confidence: 0.98, status: 'VERIFIED', evidence_count: 4 },
          { name: 'PyTorch', confidence: 0.94, status: 'VERIFIED', evidence_count: 3 },
          { name: 'FastAPI', confidence: 0.90, status: 'VERIFIED', evidence_count: 2 },
          { name: 'Docker', confidence: 0.88, status: 'VERIFIED', evidence_count: 2 },
          { name: 'Kubernetes', confidence: 0.75, status: 'INFERRED', evidence_count: 1 },
          { name: 'SQL', confidence: 0.85, status: 'VERIFIED', evidence_count: 2 },
        ]
      }
    };
  }
}

export async function updateCareerProfile(payload) {
  const { data } = await api.put(`${API_V1}/career-profile`, payload);
  return data;
}

export async function addEvidence(payload) {
  const { data } = await api.post(`${API_V1}/career-profile/evidence`, payload);
  return data;
}

// ── Resume & Multi-ATS ────────────────────────────────────────────────────────
export async function uploadResumeV1(file) {
  const formData = new FormData();
  formData.append('resume', file);
  const { data } = await api.post(`${API_V1}/resumes/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

// ── Job Intelligence & Matching ───────────────────────────────────────────────
export async function parseJobDescription(rawJd, title = 'Target Role', company = 'Target Company') {
  const { data } = await api.post(`${API_V1}/jobs/parse`, {
    raw_jd: rawJd,
    title,
    company,
  });
  return data;
}

export async function matchJob(candidateSkills, candidateExperienceYears, jobParsed) {
  const { data } = await api.post(`${API_V1}/jobs/match`, {
    candidate_skills: candidateSkills,
    candidate_experience_years: candidateExperienceYears,
    job_parsed: jobParsed,
  });
  return data;
}

export async function getJobFeed(skills = 'python,pytorch,fastapi', targetRole = 'Data Scientist') {
  try {
    const { data } = await api.get(`${API_V1}/jobs/feed`, {
      params: { skills, target_role: targetRole }
    });
    return data;
  } catch (e) {
    return [
      { id: '1', title: 'Senior AI Engineer', company: 'Anthropic', location: 'San Francisco, CA', salary_range: '$180k - $240k', match_score: 92, key_skills: ['Python', 'PyTorch', 'Distributed Systems'], source: 'Greenhouse' },
      { id: '2', title: 'Staff Machine Learning Engineer', company: 'Stripe', location: 'Remote', salary_range: '$200k - $260k', match_score: 88, key_skills: ['PyTorch', 'FastAPI', 'Kubernetes'], source: 'Lever' },
      { id: '3', title: 'Lead LLM Systems Engineer', company: 'Scale AI', location: 'San Francisco, CA', salary_range: '$190k - $250k', match_score: 85, key_skills: ['Python', 'CUDA', 'Docker'], source: 'RemoteOK' },
    ];
  }
}

// ── Evidence-Grounded Tailoring & Exports ─────────────────────────────────────
export async function tailorResume(resumeId, targetJobTitle, targetCompany, requiredJobSkills) {
  const { data } = await api.post(`${API_V1}/tailor`, {
    resume_id: resumeId,
    target_job_title: targetJobTitle,
    target_company: targetCompany,
    required_job_skills: requiredJobSkills,
  });
  return data;
}

export async function exportPdf(structuredContent) {
  const { data } = await api.post(`${API_V1}/tailor/export-pdf`, structuredContent);
  return data;
}

export async function generateCoverLetter(candidateName, targetRole, targetCompany, verifiedSkills, achievements = []) {
  const { data } = await api.post(`${API_V1}/tailor/cover-letter`, {
    candidate_name: candidateName,
    target_role: targetRole,
    target_company: targetCompany,
    verified_skills: verifiedSkills,
    achievements,
  });
  return data;
}

// ── Application CRM ───────────────────────────────────────────────────────────
export async function getKanbanBoard() {
  try {
    const { data } = await api.get(`${API_V1}/applications/kanban`);
    return data;
  } catch (e) {
    return {
      Saved: [
        { id: 101, company_name: 'OpenAI', job_title: 'Research Engineer', status: 'Saved', created_at: '2026-09-01' }
      ],
      Applied: [
        { id: 102, company_name: 'Anthropic', job_title: 'Senior AI Engineer', status: 'Applied', created_at: '2026-09-03' }
      ],
      Screening: [
        { id: 103, company_name: 'Stripe', job_title: 'Staff ML Engineer', status: 'Screening', created_at: '2026-08-28' }
      ],
      Interviewing: [
        { id: 104, company_name: 'Databricks', job_title: 'Systems AI Lead', status: 'Interviewing', created_at: '2026-08-20' }
      ],
      Offer: [],
      Rejected: []
    };
  }
}

export async function createApplication(companyName, jobTitle, jobUrl = '', status = 'Saved', notes = '') {
  const { data } = await api.post(`${API_V1}/applications`, {
    company_name: companyName,
    job_title: jobTitle,
    job_url: jobUrl,
    status,
    notes,
  });
  return data;
}

export async function updateStage(appId, newStatus, notes = '') {
  const { data } = await api.put(`${API_V1}/applications/${appId}/stage`, {
    new_status: newStatus,
    notes,
  });
  return data;
}

export async function getCRMAnalytics() {
  try {
    const { data } = await api.get(`${API_V1}/applications/analytics`);
    return data;
  } catch (e) {
    return {
      total_applications: 4,
      interview_rate: 0.25,
      response_rate: 0.50,
      stage_breakdown: { Saved: 1, Applied: 1, Screening: 1, Interviewing: 1 }
    };
  }
}

// ── Interview & Portfolio ─────────────────────────────────────────────────────
export async function generateInterviewPack(roleTitle, companyName, resumeText, skills) {
  const { data } = await api.post(`${API_V1}/interviews/prep-pack`, {
    role_title: roleTitle,
    company_name: companyName,
    resume_text: resumeText,
    skills,
  });
  return data;
}

export async function analyzeRepo(repoUrl, repoName, readmeText = '', primaryLanguage = 'Python') {
  const { data } = await api.post(`${API_V1}/portfolio/analyze`, {
    repo_url: repoUrl,
    repo_name: repoName,
    readme_text: readmeText,
    primary_language: primaryLanguage,
  });
  return data;
}

// ── Next-Best-Action ──────────────────────────────────────────────────────────
export async function getNextBestActions() {
  try {
    const { data } = await api.get(`${API_V1}/next-best-action`);
    return data.actions || [];
  } catch (e) {
    return [
      { id: 'act_1', action_type: 'TAILOR_RESUME', title: 'Tailor Resume for Anthropic - Senior AI Engineer', description: 'Match score is 92%. Add evidence for PyTorch distributed training to gain +8% match.', priority: 1, priority_label: 'HIGH' },
      { id: 'act_2', action_type: 'FOLLOW_UP', title: 'Follow Up with Databricks Recruiter', description: 'Application has been in Interviewing stage for 5 days.', priority: 2, priority_label: 'MEDIUM' },
      { id: 'act_3', action_type: 'PORTFOLIO_LINK', title: 'Connect GitHub Repo "llm-inference-engine"', description: 'Boost portfolio technical depth score from 82 to 94.', priority: 3, priority_label: 'LOW' }
    ];
  }
}

// ── API v2 Legacy Compatibility ───────────────────────────────────────────────
export async function uploadResume(file, note = '') {
  const formData = new FormData();
  formData.append('resume', file);
  formData.append('note', note);
  const { data } = await api.post(`${API_V2}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getAnalysis(analysisId) {
  const { data } = await api.get(`${API_V2}/analysis/${analysisId}`);
  return data;
}

export async function getDashboardAnalytics() {
  const { data } = await api.get(`${API_V2}/analytics/dashboard`);
  return data;
}

export async function getMarketPulse() {
  const { data } = await api.get(`${API_V2}/market`);
  return data;
}

export default api;
