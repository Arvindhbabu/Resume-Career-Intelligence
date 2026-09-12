import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart, registerables } from 'chart.js';
import { AlertTriangle, CheckCircle, XCircle, ArrowRight, Brain, Shield, Target, Sparkles, Clock, Map, Calendar, ExternalLink } from 'lucide-react';

Chart.register(...registerables);

function DashboardPage() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();
  const scoreRingRef = useRef(null);
  const radarRef = useRef(null);
  const chartInstances = useRef({});

  useEffect(() => {
    const raw = sessionStorage.getItem('resumeiqData');
    if (!raw) { navigate('/'); return; }
    setData(JSON.parse(raw));
  }, [navigate]);

  useEffect(() => {
    if (!data) return;

    // Score ring
    if (scoreRingRef.current) {
      if (chartInstances.current.ring) chartInstances.current.ring.destroy();
      const overall = data.scores?.overall_score || 0;
      const color = overall >= 70 ? '#34d399' : overall >= 45 ? '#6394ff' : '#f87171';
      chartInstances.current.ring = new Chart(scoreRingRef.current, {
        type: 'doughnut',
        data: {
          datasets: [{ data: [overall, 100 - overall], backgroundColor: [color, 'rgba(255,255,255,0.04)'], borderWidth: 0 }],
        },
        options: { cutout: '78%', plugins: { legend: { display: false }, tooltip: { enabled: false } }, animation: { duration: 1400, easing: 'easeInOutQuart' } },
      });
    }

    // Career DNA radar
    if (radarRef.current && data.career_dna) {
      if (chartInstances.current.radar) chartInstances.current.radar.destroy();
      const labels = Object.keys(data.career_dna).map(l => l.replace('The ', ''));
      const values = Object.values(data.career_dna).map(v => v.score);
      chartInstances.current.radar = new Chart(radarRef.current, {
        type: 'radar',
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: 'rgba(99,148,255,0.12)',
            borderColor: '#6394ff',
            borderWidth: 2,
            pointBackgroundColor: '#6394ff',
            pointRadius: 4,
          }],
        },
        options: {
          scales: { r: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.04)' }, angleLines: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b', backdropColor: 'transparent', stepSize: 25 }, pointLabels: { color: '#94a3b8', font: { size: 11, family: 'Inter' } } } },
          plugins: { legend: { display: false } },
          animation: { duration: 1000 },
        },
      });
    }

    return () => {
      Object.values(chartInstances.current).forEach(c => c?.destroy());
    };
  }, [data]);

  if (!data) return null;

  const { 
    parsed, scores, xai_breakdown, career_dna, job_matches, 
    explanation, bias_report, skills_found, skills_missing, 
    recommendations, roadmap, roadmap_summary,
    agent_logs, total_duration_ms 
  } = data;
  const overall = scores?.overall_score || 0;
  const scoreColor = overall >= 70 ? '#34d399' : overall >= 45 ? '#6394ff' : '#f87171';

  const scoreBars = [
    { label: 'Skills Match', value: scores?.skills_match || 0, color: '#6394ff' },
    { label: 'Experience', value: scores?.experience_match || 0, color: '#a78bfa' },
    { label: 'Domain Relevance', value: scores?.domain_relevance || 0, color: '#34d399' },
    { label: 'Project Depth', value: scores?.project_complexity || 0, color: '#f472b6' },
    { label: 'Format Quality', value: scores?.format_quality || 0, color: '#fbbf24' },
  ];

  return (
    <div>
      {/* Page Header */}
      <div className="page-header animate-in">
        <h2>{parsed?.name || 'Candidate'}</h2>
        <p style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
          {parsed?.email && <span className="tag tag-default">📧 {parsed.email}</span>}
          {parsed?.linkedin && <span className="tag tag-default">🔗 LinkedIn</span>}
          {parsed?.github && <span className="tag tag-default">💻 GitHub</span>}
          {parsed?.years_of_experience > 0 && <span className="tag tag-default">⏱ {parsed.years_of_experience} yrs</span>}
          <span className="tag tag-info"><Clock size={12} /> {total_duration_ms}ms</span>
        </p>
      </div>

      {/* Agent Pipeline */}
      <div className="card animate-in" style={{ marginBottom: '1.5rem', padding: '1rem 1.5rem' }}>
        <div className="card-title"><Brain size={16} /> Multi-Agent Pipeline</div>
        <div className="agent-pipeline">
          {(agent_logs || []).map((log, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {i > 0 && <span className="agent-arrow">→</span>}
              <div className={`agent-step ${log.status}`}>
                <span className="agent-step-dot" />
                <span>{log.agent?.replace('_agent', '').replace('_', ' ')}</span>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem' }}>{log.duration_ms}ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Score Hero */}
      <div className="card card-glow animate-in animate-in-delay-1" style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '2.5rem', alignItems: 'center', marginBottom: '1.5rem', padding: '2rem' }}>
        <div className="score-ring-container">
          <canvas ref={scoreRingRef} width={160} height={160} />
          <div className="score-ring-center">
            <div className="score-ring-value" style={{ color: scoreColor }}>{Math.round(overall)}</div>
            <div className="score-ring-label">Overall Score</div>
          </div>
        </div>
        <div>
          {scoreBars.map(bar => (
            <div className="score-bar-row" key={bar.label}>
              <div className="score-bar-name">{bar.label}</div>
              <div className="score-bar-track">
                <div className="score-bar-fill" style={{ width: `${bar.value}%`, background: bar.color }} />
              </div>
              <div className="score-bar-value" style={{ color: bar.color }}>{Math.round(bar.value)}</div>
            </div>
          ))}
          {scores?.confidence && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Confidence: {(scores.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      </div>

      {/* XAI Explanation */}
      {explanation?.summary && (
        <div className="card animate-in animate-in-delay-2" style={{ marginBottom: '1.5rem' }}>
          <div className="card-title"><Sparkles size={16} /> AI Explanation</div>
          <p style={{ fontSize: '0.9rem', lineHeight: 1.7, color: 'var(--text-secondary)' }}>{explanation.summary}</p>
          {explanation.strengths?.length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--success)' }}>💪 Strengths</div>
              {explanation.strengths.map((s, i) => (
                <span key={i} className="tag tag-success" style={{ marginRight: '0.4rem', marginBottom: '0.4rem' }}><CheckCircle size={12} /> {s}</span>
              ))}
            </div>
          )}
          {explanation.areas_for_improvement?.length > 0 && (
            <div style={{ marginTop: '0.75rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--warning)' }}>📈 Areas for Improvement</div>
              {explanation.areas_for_improvement.map((a, i) => (
                <span key={i} className="tag tag-warning" style={{ marginRight: '0.4rem', marginBottom: '0.4rem' }}>{a}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Career DNA Radar */}
      <div className="card animate-in animate-in-delay-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title">🧬 Career DNA Map</div>
        <canvas ref={radarRef} height={280} />
        <div className="grid-4" style={{ marginTop: '1rem' }}>
          {career_dna && Object.entries(career_dna).map(([name, d]) => (
            <div key={name} style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '0.75rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, marginBottom: '0.4rem' }}>{name}</div>
              <div className="score-bar-track"><div className="score-bar-fill" style={{ width: `${d.score}%`, background: 'var(--accent-gradient)' }} /></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.3rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                <span>{d.matched_skills?.slice(0, 2).join(', ') || 'None'}</span>
                <span>{Math.round(d.score)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Skills + Bias */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card animate-in animate-in-delay-2">
          <div className="card-title"><CheckCircle size={16} style={{ color: 'var(--success)' }} /> Skill Graph Hierarchies</div>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>Semantic resolution of your skills into industry categories.</p>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {(parsed?.skill_graph_mappings || []).map((m, i) => (
              <div key={i} className="skill-hierarchy-tag">
                <span className="skill-hierarchy-parent">{m.category}</span>
                <span style={{ opacity: 0.3 }}>/</span>
                <span className="skill-hierarchy-child">{m.skill}</span>
              </div>
            ))}
          </div>
          {(!parsed?.skill_graph_mappings?.length) && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {(skills_found || []).slice(0, 30).map(s => (
                <span key={s} className="tag tag-success">{s}</span>
              ))}
            </div>
          )}
        </div>
        <div className="card animate-in animate-in-delay-2">
          <div className="card-title"><Shield size={16} style={{ color: 'var(--warning)' }} /> Bias Detection</div>
          {bias_report?.findings?.length > 0 ? (
            bias_report.findings.slice(0, 5).map((f, i) => (
              <div key={i} className={`bias-alert ${f.severity}`}>
                <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{f.message}</span>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>✅ No significant bias detected in this evaluation.</p>
          )}
          {bias_report?.overall_bias_risk !== undefined && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.8rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Bias Risk Level: </span>
              <span className={`tag ${bias_report.overall_bias_risk > 30 ? 'tag-danger' : bias_report.overall_bias_risk > 10 ? 'tag-warning' : 'tag-success'}`}>
                {bias_report.overall_bias_risk}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Gap Analysis Roadmap */}
      {roadmap?.length > 0 && (
        <div className="card animate-in animate-in-delay-3" style={{ marginBottom: '1.5rem' }}>
          <div className="card-title" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Map size={16} /> Smart Career Roadmap</div>
            <div className="tag tag-info">Target: {roadmap_summary?.target_role}</div>
          </div>
          <div style={{ display: 'flex', gap: '2rem', marginBottom: '2rem', padding: '1rem', background: 'rgba(99, 148, 255, 0.03)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Effort</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-primary)' }}>~{roadmap_summary?.total_weeks} Weeks</div>
            </div>
            <div style={{ width: 1, background: 'var(--border-subtle)' }} />
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Projected Match</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--success)' }}>{roadmap_summary?.projected_match}%</div>
            </div>
          </div>
          
          <div className="roadmap-timeline">
            {roadmap.map((step, i) => (
              <div className="roadmap-step" key={i}>
                <div className="roadmap-step-dot" />
                <div className="roadmap-step-week">Step {i + 1} • {step.estimated_weeks} Weeks</div>
                <div className="roadmap-step-title">{step.skill} <span className="roadmap-impact-badge">{step.impact}</span></div>
                <div className="roadmap-step-details">
                  {step.note && <p style={{ fontSize: '0.8rem', color: 'var(--warning)', marginBottom: '0.75rem', fontWeight: 500 }}>⚠️ {step.note}</p>}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                      <div style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>📚 RESOURCES</div>
                      {step.resources?.map((res, j) => (
                        <div key={j} className="roadmap-resource">
                          {res.type === 'Course' ? <Calendar size={12} /> : <ExternalLink size={12} />}
                          <a href={res.url || '#'} target="_blank" rel="noreferrer" style={{ fontSize: '0.75rem' }}>{res.name}</a>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Job Matches */}
      <div className="card animate-in animate-in-delay-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title"><Target size={16} /> Job Matches</div>
        {(job_matches || []).slice(0, 5).map((m, i) => (
          <div key={i} style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '0.6rem',
            display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem',
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, marginBottom: '0.3rem' }}>{m.job_title}</div>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span>🏢 {m.company_type}</span>
                <span>💰 {m.salary_range}</span>
              </div>
              {m.dimension_scores && (
                <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                  <span className="tag tag-default">Skills: {Math.round(m.dimension_scores.skills_match || 0)}%</span>
                  <span className="tag tag-default">Exp: {Math.round(m.dimension_scores.experience_alignment || 0)}%</span>
                  <span className="tag tag-default">Domain: {Math.round(m.dimension_scores.domain_relevance || 0)}%</span>
                </div>
              )}
              {m.skill_details?.missing?.length > 0 && (
                <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                  {m.skill_details.missing.slice(0, 4).map(s => (
                    <span key={s} className="tag tag-warning">{s}</span>
                  ))}
                </div>
              )}
            </div>
            <div style={{ textAlign: 'center', flexShrink: 0 }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
                {Math.round(m.final_score || m.match_score || 0)}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>MATCH %</div>
            </div>
          </div>
        ))}
      </div>

      {/* Recommendations */}
      <div className="card animate-in animate-in-delay-3" style={{ marginBottom: '2rem' }}>
        <div className="card-title">💡 Recommendations</div>
        {(recommendations || []).map((r, i) => (
          <div key={i} className="rec-item">
            {typeof r === 'string' ? r : (
              <>
                <span>{r.icon}</span>
                <span style={{ flex: 1 }}>{r.text}</span>
                {r.impact && <span className={`rec-impact ${r.impact === 'high' ? 'impact-high' : 'impact-medium'}`}>{r.impact}</span>}
              </>
            )}
          </div>
        ))}
        {(!recommendations || recommendations.length === 0) && (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>🎉 No major improvements needed — great resume!</p>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;
