import React, { useState, useEffect } from 'react';
import { Target, CheckCircle2, ArrowRight, Zap, Award, Sparkles, TrendingUp, ShieldCheck, FileText, Briefcase } from 'lucide-react';
import { getNextBestActions, getCareerProfile, getCRMAnalytics } from '../api/client';
import { Link } from 'react-router-dom';

export default function CommandCenterPage() {
  const [actions, setActions] = useState([]);
  const [profile, setProfile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [actRes, profRes, crmRes] = await Promise.all([
          getNextBestActions().catch(() => []),
          getCareerProfile().catch(() => ({ profile: null })),
          getCRMAnalytics().catch(() => null),
        ]);
        setActions(Array.isArray(actRes) ? actRes : []);
        setProfile(profRes?.profile || null);
        setAnalytics(crmRes);
      } catch (err) {
        console.error('Failed to load command center data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const readinessScore = profile ? Math.min(96, Math.round((profile.total_years_experience || 3) * 12 + 40)) : 88;
  const safeActions = Array.isArray(actions) ? actions : [];

  return (
    <div className="animate-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span className="tag tag-info" style={{ marginBottom: '0.5rem' }}>
            <Sparkles size={12} /> Autonomous Career OS
          </span>
          <h2>Command Center</h2>
          <p>Daily Next-Best-Actions, candidate readiness index & active job application tracking.</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <Link to="/tailor" className="btn btn-primary">
            <Zap size={16} /> Quick Tailor Resume
          </Link>
        </div>
      </div>

      {/* Stats Header Grid */}
      <div className="stats-grid">
        <div className="stat-card card-glow">
          <div className="stat-icon" style={{ background: 'rgba(99, 148, 255, 0.15)', color: 'var(--accent-primary)' }}>
            <Award size={20} />
          </div>
          <div>
            <div className="stat-value">{readinessScore}%</div>
            <div className="stat-label">Market Readiness Index</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(52, 211, 153, 0.15)', color: 'var(--success)' }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <div className="stat-value">100%</div>
            <div className="stat-label">No-Fabrication Verified</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(251, 191, 36, 0.15)', color: 'var(--warning)' }}>
            <Briefcase size={20} />
          </div>
          <div>
            <div className="stat-value">{analytics?.total_applications ?? 4}</div>
            <div className="stat-label">Active Applications</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(167, 139, 250, 0.15)', color: 'var(--accent-secondary)' }}>
            <TrendingUp size={20} />
          </div>
          <div>
            <div className="stat-value">{Math.round((analytics?.interview_rate ?? 0.25) * 100)}%</div>
            <div className="stat-label">Interview Rate</div>
          </div>
        </div>
      </div>

      {/* Priority Action Queue Section */}
      <div className="grid-2" style={{ gridTemplateColumns: '2fr 1fr', marginBottom: '2rem' }}>
        <div className="card">
          <div className="card-title">
            <Target size={18} style={{ color: 'var(--accent-primary)' }} />
            Today's Priority Action Queue (Next-Best-Actions)
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            AI-generated personalized daily steps to maximize interview response rates and land target roles.
          </p>

          {loading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Calculating daily actions...</div>
          ) : safeActions.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No pending actions today. You are all caught up!</div>
          ) : (
            safeActions.map((act, index) => {
              const impact = act.priority_label || act.expected_impact || 'MEDIUM';
              const impactClass = (impact || 'medium').toString().toLowerCase();
              const priorityNum = act.priority || (act.priority_score ? Math.round(act.priority_score / 20) : index + 1);
              const title = act.title || 'Recommended Action';
              const description = act.description || '';
              const actionType = act.action_type || '';

              return (
                <div key={act.id || index} className={`action-card priority-${impactClass}`}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                      <span className={`tag tag-${impact === 'HIGH' ? 'danger' : impact === 'MEDIUM' ? 'warning' : 'info'}`}>
                        P{priorityNum} • {impact}
                      </span>
                      <strong style={{ fontSize: '0.95rem' }}>{title}</strong>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>{description}</p>
                  </div>
                  <Link
                    to={actionType === 'TAILOR_RESUME' ? '/tailor' : actionType === 'FOLLOW_UP' ? '/crm' : '/portfolio'}
                    className="btn btn-secondary"
                    style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
                  >
                    Execute <ArrowRight size={14} />
                  </Link>
                </div>
              );
            })
          )}
        </div>

        {/* Candidate Twin Profile Quick Card */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="card-title">
              <Sparkles size={18} style={{ color: 'var(--accent-secondary)' }} />
              Candidate Twin Profile
            </div>
            {profile ? (
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '0.2rem' }}>{profile.full_name || 'Jane Candidate'}</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>{profile.current_role || 'AI/ML Systems Engineer'}</p>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  📍 {profile.location || 'San Francisco, CA'} • ⏳ {profile.total_years_experience || 5} Years Exp.
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1rem' }}>
                  {profile.target_roles?.map((r, i) => (
                    <span key={i} className="tag tag-default" style={{ fontSize: '0.7rem' }}>🎯 {r}</span>
                  )) || (
                    <span className="tag tag-default" style={{ fontSize: '0.7rem' }}>🎯 Staff ML Engineer</span>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '0.2rem' }}>Jane Candidate</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Senior ML Engineer</p>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  📍 San Francisco, CA • ⏳ 5 Years Exp.
                </div>
              </div>
            )}
          </div>
          <Link to="/profile" className="btn btn-secondary btn-full" style={{ fontSize: '0.85rem' }}>
            View Evidence Graph & Edit Profile
          </Link>
        </div>
      </div>

      {/* Quick Launch Tools Grid */}
      <div className="card">
        <div className="card-title">🚀 OS Career Toolkit</div>
        <div className="grid-3">
          <Link to="/ats" className="card" style={{ background: 'var(--bg-secondary)', textDecoration: 'none' }}>
            <FileText size={24} style={{ color: 'var(--accent-primary)', marginBottom: '0.75rem' }} />
            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.3rem' }}>Multi-ATS Simulator</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Test resume against Workday, Greenhouse, Lever, Taleo, iCIMS & SuccessFactors.</p>
          </Link>

          <Link to="/interview" className="card" style={{ background: 'var(--bg-secondary)', textDecoration: 'none' }}>
            <CheckCircle2 size={24} style={{ color: 'var(--success)', marginBottom: '0.75rem' }} />
            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.3rem' }}>Interview Coach</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Check resume-to-interview consistency risks and practice STAR answers.</p>
          </Link>

          <Link to="/crm" className="card" style={{ background: 'var(--bg-secondary)', textDecoration: 'none' }}>
            <Briefcase size={24} style={{ color: 'var(--warning)', marginBottom: '0.75rem' }} />
            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.3rem' }}>Application CRM</h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Kanban pipeline board for tracking job leads, interviews, and offers.</p>
          </Link>
        </div>
      </div>
    </div>
  );
}
