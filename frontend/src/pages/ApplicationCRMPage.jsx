import React, { useState, useEffect } from 'react';
import { Briefcase, Plus, TrendingUp, Calendar, ChevronRight, CheckCircle2, Clock } from 'lucide-react';
import { getKanbanBoard, createApplication, updateStage, getCRMAnalytics } from '../api/client';

export default function ApplicationCRMPage() {
  const [board, setBoard] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  // New Application Modal / Form
  const [showAdd, setShowAdd] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadCRM();
  }, []);

  async function loadCRM() {
    try {
      const [kRes, aRes] = await Promise.all([getKanbanBoard(), getCRMAnalytics()]);
      setBoard(kRes);
      setAnalytics(aRes);
    } catch (e) {
      console.error('Failed loading CRM:', e);
    } finally {
      setLoading(false);
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!companyName || !jobTitle) return;
    try {
      await createApplication(companyName, jobTitle, jobUrl, 'Saved', notes);
      setCompanyName('');
      setJobTitle('');
      setJobUrl('');
      setNotes('');
      setShowAdd(false);
      loadCRM();
    } catch (e) {
      console.error('Failed creating application:', e);
    }
  };

  const handleMoveStage = async (appId, currentStage) => {
    const stages = ['Saved', 'Applied', 'Screening', 'Interviewing', 'Offer', 'Rejected'];
    const idx = stages.indexOf(currentStage);
    if (idx < stages.length - 1) {
      const nextStage = stages[idx + 1];
      try {
        await updateStage(appId, nextStage, `Moved to ${nextStage}`);
        loadCRM();
      } catch (e) {
        console.error('Failed moving stage:', e);
      }
    }
  };

  const stages = ['Saved', 'Applied', 'Screening', 'Interviewing', 'Offer', 'Rejected'];

  return (
    <div className="animate-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span className="tag tag-warning" style={{ marginBottom: '0.5rem' }}>
            <Briefcase size={12} /> Application CRM Pipeline
          </span>
          <h2>Job Application Intelligence CRM</h2>
          <p>Track your applications across 6 pipeline stages with response rate conversion analytics.</p>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="btn btn-primary">
          <Plus size={16} /> Add Application Lead
        </button>
      </div>

      {/* CRM Analytics Banner */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 148, 255, 0.15)', color: 'var(--accent-primary)' }}>
            <Briefcase size={20} />
          </div>
          <div>
            <div className="stat-value">{analytics?.total_applications || 4}</div>
            <div className="stat-label">Total Applications</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(52, 211, 153, 0.15)', color: 'var(--success)' }}>
            <TrendingUp size={20} />
          </div>
          <div>
            <div className="stat-value">{Math.round((analytics?.response_rate || 0.5) * 100)}%</div>
            <div className="stat-label">Employer Response Rate</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(251, 191, 36, 0.15)', color: 'var(--warning)' }}>
            <Clock size={20} />
          </div>
          <div>
            <div className="stat-value">{Math.round((analytics?.interview_rate || 0.25) * 100)}%</div>
            <div className="stat-label">Interview Conversion Rate</div>
          </div>
        </div>
      </div>

      {/* Add Lead Form Slide-down */}
      {showAdd && (
        <div className="card animate-in" style={{ marginBottom: '1.5rem', background: 'var(--bg-secondary)' }}>
          <div className="card-title">Add New Job Application</div>
          <form onSubmit={handleCreate}>
            <div className="grid-2" style={{ gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Company Name</label>
                <input
                  type="text"
                  placeholder="e.g. Stripe"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Job Title</label>
                <input
                  type="text"
                  placeholder="e.g. Staff ML Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                  required
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Job Posting URL (Optional)</label>
              <input
                type="url"
                placeholder="https://jobs.stripe.com/..."
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => setShowAdd(false)} className="btn btn-secondary">Cancel</button>
              <button type="submit" className="btn btn-primary">Save to Kanban</button>
            </div>
          </form>
        </div>
      )}

      {/* 6-Stage Kanban Board */}
      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading CRM Pipeline...</div>
      ) : (
        <div className="kanban-board">
          {stages.map((stg) => {
            const cards = board ? board[stg] || [] : [];
            return (
              <div key={stg} className="kanban-column">
                <div className="kanban-column-header">
                  <div className="kanban-column-title">
                    <span>{stg}</span>
                  </div>
                  <span className="tag tag-default" style={{ fontSize: '0.65rem' }}>{cards.length}</span>
                </div>

                <div style={{ flex: 1 }}>
                  {cards.map((app) => (
                    <div key={app.id} className="kanban-card" onClick={() => handleMoveStage(app.id, stg)}>
                      <strong style={{ fontSize: '0.9rem', color: 'var(--text-primary)', display: 'block' }}>
                        {app.company_name}
                      </strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                        {app.job_title}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        <span>📅 {app.created_at || 'Today'}</span>
                        <ChevronRight size={14} style={{ opacity: 0.6 }} />
                      </div>
                    </div>
                  ))}

                  {cards.length === 0 && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', paddingTop: '2rem' }}>
                      No applications
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
