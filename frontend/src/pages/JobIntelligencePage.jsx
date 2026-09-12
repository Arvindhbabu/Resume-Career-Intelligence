import React, { useState, useEffect } from 'react';
import { Search, Briefcase, CheckCircle2, AlertCircle, ArrowRight, Zap, Target, Sparkles } from 'lucide-react';
import { parseJobDescription, matchJob, getJobFeed } from '../api/client';
import { Link } from 'react-router-dom';

export default function JobIntelligencePage() {
  const [rawJd, setRawJd] = useState('');
  const [jobTitle, setJobTitle] = useState('Senior AI Engineer');
  const [company, setCompany] = useState('Anthropic');
  const [parsedJd, setParsedJd] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [jobFeed, setJobFeed] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadFeed() {
      try {
        const feed = await getJobFeed('python,pytorch,fastapi', 'AI Engineer');
        setJobFeed(Array.isArray(feed) ? feed : []);
      } catch (e) {
        console.error('Failed to load feed:', e);
        setJobFeed([]);
      }
    }
    loadFeed();
  }, []);

  const handleParseAndMatch = async (e) => {
    e.preventDefault();
    if (!rawJd.trim()) return;
    setLoading(true);
    try {
      const parsed = await parseJobDescription(rawJd, jobTitle, company);
      setParsedJd(parsed);

      const candidateSkills = ['Python', 'PyTorch', 'FastAPI', 'Docker', 'SQL', 'Git'];
      const matched = await matchJob(candidateSkills, 5.0, parsed);
      setMatchResult(matched);
    } catch (e) {
      console.error('Parsing failed:', e);
    } finally {
      setLoading(false);
    }
  };

  const safeFeed = Array.isArray(jobFeed) ? jobFeed : [];

  return (
    <div className="animate-in">
      <div className="page-header">
        <span className="tag tag-info" style={{ marginBottom: '0.5rem' }}>
          <Target size={12} /> Semantic Requirement Classifier
        </span>
        <h2>Job Intelligence & Match Engine</h2>
        <p>Parse raw JDs, classify hard/important/preferred requirements, and calculate explainable match scores.</p>
      </div>

      <div className="grid-2" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '2rem' }}>
        {/* Job Description Parser Form */}
        <div className="card">
          <div className="card-title">
            <Search size={18} style={{ color: 'var(--accent-primary)' }} />
            Paste Job Description (JD)
          </div>

          <form onSubmit={handleParseAndMatch}>
            <div className="grid-2" style={{ gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Job Title</label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Company</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.3rem' }}>Raw Job Text</label>
              <textarea
                rows={8}
                placeholder="Paste full job posting text here..."
                value={rawJd}
                onChange={(e) => setRawJd(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', color: 'white', fontFamily: 'inherit' }}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Classifying Requirements...' : 'Classify Requirements & Match'}
            </button>
          </form>
        </div>

        {/* Requirements Breakdown & Match Output */}
        <div className="card">
          <div className="card-title">
            <Sparkles size={18} style={{ color: 'var(--accent-secondary)' }} />
            Explainable Requirement Match
          </div>

          {matchResult ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Explainable Match Score</div>
                  <h3 style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--accent-primary)' }}>
                    {matchResult.overall_match_score || 85}%
                  </h3>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`tag tag-${(matchResult.overall_match_score || 85) >= 80 ? 'success' : 'warning'}`}>
                    {(matchResult.overall_match_score || 85) >= 80 ? 'Strong Fit' : 'Moderate Fit'}
                  </span>
                </div>
              </div>

              {parsedJd && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div>
                    <span className="tag tag-danger" style={{ marginBottom: '0.4rem' }}>Hard Requirements</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {(parsedJd.hard_requirements || []).map((req, i) => (
                        <span key={i} className="skill-tree-node" style={{ borderColor: 'rgba(248,113,113,0.3)' }}>
                          {typeof req === 'string' ? req : req.skill || req.name || 'Requirement'}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="tag tag-warning" style={{ marginBottom: '0.4rem' }}>Important Requirements</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {(parsedJd.important_requirements || []).map((req, i) => (
                        <span key={i} className="skill-tree-node">
                          {typeof req === 'string' ? req : req.skill || req.name || 'Requirement'}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="tag tag-info" style={{ marginBottom: '0.4rem' }}>Preferred Skills</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                      {(parsedJd.preferred_requirements || []).map((req, i) => (
                        <span key={i} className="skill-tree-node" style={{ opacity: 0.8 }}>
                          {typeof req === 'string' ? req : req.skill || req.name || 'Requirement'}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: '3rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Paste a Job Description on the left to see requirement breakdown & match analysis.
            </div>
          )}
        </div>
      </div>

      {/* Personalized Job Feed */}
      <div className="card">
        <div className="card-title">
          <Briefcase size={18} style={{ color: 'var(--warning)' }} />
          Personalized Opportunities Feed
        </div>

        <div className="grid-3" style={{ marginTop: '1rem' }}>
          {safeFeed.map((job, idx) => (
            <div key={job.id || idx} className="card" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <strong style={{ fontSize: '1rem' }}>{job.title || 'Target Role'}</strong>
                <span className="tag tag-success">{job.match_score || 88}% Match</span>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                🏢 {job.company || 'Tech Company'} • 📍 {job.location || 'Remote'}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--success)', fontWeight: 600, marginBottom: '0.75rem' }}>
                💰 {job.salary_range || '$150k - $200k'}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginBottom: '1rem' }}>
                {(job.key_skills || []).map((s, i) => (
                  <span key={i} className="tag tag-default" style={{ fontSize: '0.65rem' }}>{s}</span>
                ))}
              </div>
              <Link to="/tailor" className="btn btn-secondary btn-full" style={{ fontSize: '0.8rem' }}>
                Tailor Resume <ArrowRight size={14} />
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
