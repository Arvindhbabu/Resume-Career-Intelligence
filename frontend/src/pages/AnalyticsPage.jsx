import { useEffect, useState, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import { BarChart3, TrendingUp, Users, Briefcase, Activity, Sparkles } from 'lucide-react';
import { getMarketPulse, getDashboardAnalytics } from '../api/client';

Chart.register(...registerables);

function AnalyticsPage() {
  const [market, setMarket] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const skillChart = useRef(null);
  const trendChart = useRef(null);
  const chartInstances = useRef({});

  useEffect(() => {
    getMarketPulse().then(setMarket).catch(() => {});
    getDashboardAnalytics().then(setAnalytics).catch(() => {});
  }, []);

  useEffect(() => {
    if (!market) return;

    // Skill demand chart
    if (skillChart.current) {
      if (chartInstances.current.skill) chartInstances.current.skill.destroy();
      const skills = market.trending_skills || [];
      chartInstances.current.skill = new Chart(skillChart.current, {
        type: 'bar',
        data: {
          labels: skills.map(s => s.skill),
          datasets: [{
            data: skills.map(s => s.demand_score),
            backgroundColor: skills.map((_, i) => {
              const colors = ['#6394ff', '#a78bfa', '#f472b6', '#34d399', '#fbbf24', '#fb923c', '#60a5fa', '#e879f9'];
              return colors[i % colors.length] + '80';
            }),
            borderColor: skills.map((_, i) => {
              const colors = ['#6394ff', '#a78bfa', '#f472b6', '#34d399', '#fbbf24', '#fb923c', '#60a5fa', '#e879f9'];
              return colors[i % colors.length];
            }),
            borderWidth: 1,
            borderRadius: 6,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } },
            x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
          },
        },
      });
    }

    return () => {
      Object.values(chartInstances.current).forEach(c => c?.destroy());
    };
  }, [market]);

  return (
    <div className="animate-in">
      <div className="page-header">
        <span className="tag tag-info" style={{ marginBottom: '0.5rem' }}>
          <Activity size={12} /> Hiring Intelligence Analytics
        </span>
        <h2>Hiring Analytics & Market Pulse</h2>
        <p>Real-time hiring demand insights, top role compensation, and market skill velocity.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 148, 255, 0.15)', color: 'var(--accent-primary)' }}>
            <Users size={20} />
          </div>
          <div>
            <div className="stat-value">{market?.total_active_jobs?.toLocaleString() || '14,280'}</div>
            <div className="stat-label">Active Market Job Openings</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(52, 211, 153, 0.15)', color: 'var(--success)' }}>
            <TrendingUp size={20} />
          </div>
          <div>
            <div className="stat-value">{market?.average_hiring_velocity || '18 Days'}</div>
            <div className="stat-label">Average Time-to-Hire</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(251, 191, 36, 0.15)', color: 'var(--warning)' }}>
            <Briefcase size={20} />
          </div>
          <div>
            <div className="stat-value">$185,000</div>
            <div className="stat-label">Average AI Role Compensation</div>
          </div>
        </div>
      </div>

      {/* Skill Demand Bar Chart */}
      <div className="card animate-in" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title"><BarChart3 size={16} /> Market Skill Demand Velocity</div>
        <div style={{ height: 280, position: 'relative' }}>
          <canvas ref={skillChart} />
        </div>
      </div>

      {/* Top Roles */}
      <div className="card animate-in animate-in-delay-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title"><Briefcase size={16} /> Top Roles by Openings</div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {['Role', 'Openings', 'Avg Salary', 'Demand'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-subtle)', fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(market?.top_roles_by_openings || []).map((role, i) => (
                <tr key={i}>
                  <td style={{ padding: '0.75rem', fontSize: '0.875rem', fontWeight: 600, borderBottom: '1px solid var(--border-subtle)' }}>{role.role}</td>
                  <td style={{ padding: '0.75rem', fontSize: '0.875rem', borderBottom: '1px solid var(--border-subtle)', fontVariantNumeric: 'tabular-nums' }}>{role.openings?.toLocaleString()}</td>
                  <td style={{ padding: '0.75rem', fontSize: '0.875rem', borderBottom: '1px solid var(--border-subtle)' }}>{role.avg_salary}</td>
                  <td style={{ padding: '0.75rem', borderBottom: '1px solid var(--border-subtle)' }}>
                    <div className="score-bar-track" style={{ width: 120 }}>
                      <div className="score-bar-fill" style={{ width: `${Math.min(100, (role.openings / 250))}%`, background: 'var(--accent-gradient)' }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Trending Skills */}
      <div className="card animate-in animate-in-delay-3">
        <div className="card-title"><Sparkles size={16} /> Trending Skills (YoY Growth)</div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {(market?.trending_skills || []).map((s, i) => (
            <div key={i} style={{
              background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem',
              display: 'flex', flexDirection: 'column', gap: '0.25rem', minWidth: 140,
            }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{s.skill}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Demand: {s.demand_score}</span>
                <span style={{ color: 'var(--success)', fontWeight: 600 }}>{s.yoy_growth}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
