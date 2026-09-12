import React, { useState } from 'react';
import { MessageSquare, AlertTriangle, ShieldCheck, CheckCircle2, HelpCircle, Sparkles } from 'lucide-react';
import { generateInterviewPack } from '../api/client';

export default function InterviewCoachPage() {
  const [roleTitle, setRoleTitle] = useState('Senior AI Engineer');
  const [companyName, setCompanyName] = useState('Databricks');
  const [resumeText, setResumeText] = useState(
    "Jane Candidate - Senior ML Engineer.\n- Built distributed multi-GPU training infrastructure across 256 H100 nodes handling petabytes of telemetry data.\n- Implemented FastAPI microservices with PyTorch model inference."
  );
  const [skills, setSkills] = useState('Python, PyTorch, Distributed Systems, CUDA');
  const [loading, setLoading] = useState(false);
  const [pack, setPack] = useState(null);

  const handleGeneratePack = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const skillList = skills.split(',').map((s) => s.trim()).filter(Boolean);
      const res = await generateInterviewPack(roleTitle, companyName, resumeText, skillList);
      setPack(res);
    } catch (e) {
      console.error('Failed generating pack:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-in">
      <div className="page-header">
        <span className="tag tag-success" style={{ marginBottom: '0.5rem' }}>
          <ShieldCheck size={12} /> Resume-to-Interview Consistency Checker
        </span>
        <h2>Interview Intelligence & Consistency Risk Coach</h2>
        <p>Detect high-risk resume exaggerations before interviewers do and practice grounded STAR answers.</p>
      </div>

      <div className="grid-2" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '2rem' }}>
        {/* Interview Pack Form */}
        <div className="card">
          <div className="card-title">
            <MessageSquare size={18} style={{ color: 'var(--accent-primary)' }} />
            Interview Target & Resume Context
          </div>

          <form onSubmit={handleGeneratePack}>
            <div className="grid-2" style={{ gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Target Role Title</label>
                <input
                  type="text"
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Target Company</label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                  required
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Key Skills to Test</label>
              <input
                type="text"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
              />
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Resume Text Snippet</label>
              <textarea
                rows={5}
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white', fontFamily: 'inherit' }}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Auditing Consistency Risks...' : 'Run Consistency Audit & Pack'}
            </button>
          </form>
        </div>

        {/* Consistency Risk Audit Report */}
        <div className="card">
          <div className="card-title">
            <AlertTriangle size={18} style={{ color: 'var(--warning)' }} />
            Consistency Risk Assessment
          </div>

          {pack ? (
            <div>
              <div style={{ padding: '1rem', background: pack.consistency_check?.risk_flags?.length > 0 ? 'var(--warning-bg)' : 'var(--success-bg)', border: `1px solid ${pack.consistency_check?.risk_flags?.length > 0 ? 'var(--warning-border)' : 'var(--success-border)'}`, borderRadius: 'var(--radius-md)', marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: pack.consistency_check?.risk_flags?.length > 0 ? 'var(--warning)' : 'var(--success)', marginBottom: '0.2rem' }}>
                  Risk Level: {pack.consistency_check?.overall_risk || 'LOW'}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {pack.consistency_check?.recommendation}
                </div>
              </div>

              {pack.consistency_check?.risk_flags?.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <span className="tag tag-danger" style={{ marginBottom: '0.5rem' }}>Detected Consistency Risks</span>
                  {pack.consistency_check.risk_flags.map((flag, idx) => (
                    <div key={idx} style={{ padding: '0.65rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', marginBottom: '0.4rem', fontSize: '0.8rem' }}>
                      <strong style={{ color: 'var(--danger)' }}>🚨 Risk Flag: </strong> {flag.reason || flag}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: '3rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Submit your target company and resume text to run consistency risk detection.
            </div>
          )}
        </div>
      </div>

      {/* Generated Questions Pack */}
      {pack && pack.questions && (
        <div className="card animate-in">
          <div className="card-title">
            <HelpCircle size={18} style={{ color: 'var(--accent-secondary)' }} />
            Targeted Technical & Behavioral Question Pack ({pack.questions.length} Questions)
          </div>

          <div className="grid-2" style={{ gap: '1rem', marginTop: '1rem' }}>
            {pack.questions.map((q, idx) => (
              <div key={idx} className="card" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <span className="tag tag-info">Q{idx + 1} • {q.category || 'Technical'}</span>
                  <span className="tag tag-default">{q.difficulty || 'Medium'}</span>
                </div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem', lineHeight: 1.5 }}>
                  {q.question}
                </h4>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', background: 'var(--bg-elevated)', padding: '0.75rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <strong style={{ color: 'var(--accent-primary)', display: 'block', marginBottom: '0.2rem' }}>💡 Expected STAR Structure:</strong>
                  {q.star_guide || 'Detail the specific Situation, Task, Action, and Result with quantifiable metrics.'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
