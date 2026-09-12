import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Sparkles, Brain, Shield, Target, Zap, BarChart3, GitBranch } from 'lucide-react';
import { uploadResume } from '../api/client';

const FEATURES = [
  { icon: <Brain size={16} />, label: 'Multi-Agent AI System', color: '#6394ff' },
  { icon: <Sparkles size={16} />, label: 'Semantic Understanding', color: '#a78bfa' },
  { icon: <GitBranch size={16} />, label: 'Skill Graph Intelligence', color: '#34d399' },
  { icon: <Shield size={16} />, label: 'Bias Detection Engine', color: '#fbbf24' },
  { icon: <Target size={16} />, label: 'XAI Scoring', color: '#f472b6' },
  { icon: <Zap size={16} />, label: 'Smart Gap Analyzer', color: '#fb923c' },
  { icon: <BarChart3 size={16} />, label: 'Hiring Analytics', color: '#60a5fa' },
];

const PROGRESS_STEPS = [
  [10, 'Uploading resume…'],
  [20, 'Extracting text…'],
  [30, '🤖 Parser Agent running…'],
  [45, '🤖 Job Understanding Agent…'],
  [60, '🤖 Matching Agent scoring…'],
  [75, '🤖 Critic Agent reviewing…'],
  [85, '🤖 Explanation Agent writing…'],
  [92, '🧬 Building Skill Graph…'],
  [96, '⚖️ Running Bias Detection…'],
];

function UploadPage() {
  const [file, setFile] = useState(null);
  const [note, setNote] = useState('');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressLabel, setLabel] = useState('');
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef(null);
  const navigate = useNavigate();

  function handleFile(f) {
    if (!f) return;
    setFile(f);
    setError('');
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setProgress(5);
    setLabel('Preparing upload…');

    let stepIdx = 0;
    const ticker = setInterval(() => {
      if (stepIdx < PROGRESS_STEPS.length) {
        const [pct, lbl] = PROGRESS_STEPS[stepIdx++];
        setProgress(pct);
        setLabel(lbl);
      } else {
        clearInterval(ticker);
      }
    }, 800);

    try {
      const data = await uploadResume(file, note);
      clearInterval(ticker);
      setProgress(100);
      setLabel('✅ Analysis complete!');

      sessionStorage.setItem('resumeiqData', JSON.stringify(data));
      setTimeout(() => navigate('/dashboard'), 700);
    } catch (err) {
      clearInterval(ticker);
      setUploading(false);
      setProgress(0);
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', paddingTop: '2rem' }}>
      {/* Hero */}
      <div className="animate-in" style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div className="tag tag-info" style={{ marginBottom: '1.5rem', fontSize: '0.75rem' }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#6394ff', display: 'inline-block', animation: 'pulse 2s infinite' }} />
          Powered by Multi-Agent AI + SBERT
        </div>
        <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3.5rem)', fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1.1 }}>
          Your Resume,<br />
          <span style={{ background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Intelligently Decoded
          </span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '1rem', fontSize: '1rem', maxWidth: 500, margin: '1rem auto 0', lineHeight: 1.7 }}>
          Semantic AI scoring, skill graph mapping, bias detection, and personalized career roadmaps — powered by 5 AI agents working in concert.
        </p>
      </div>

      {/* Upload Card */}
      <div className="card card-glow animate-in animate-in-delay-1" style={{ padding: '2rem' }}>
        <div
          className={`upload-zone ${dragging ? 'dragging' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
        >
          <span className="upload-icon">📄</span>
          <h3 style={{ fontWeight: 700, marginBottom: '0.4rem' }}>Drop your resume here</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>PDF or DOCX · Max 10 MB</p>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt"
            onChange={e => handleFile(e.target.files[0])}
          />
        </div>

        {file && (
          <div className="tag tag-success" style={{ marginTop: '1rem', padding: '0.5rem 0.75rem', fontSize: '0.8rem' }}>
            <FileText size={14} /> {file.name}
          </div>
        )}

        <div style={{ marginTop: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: 500 }}>
            Version note (optional)
          </label>
          <input
            type="text"
            value={note}
            onChange={e => setNote(e.target.value)}
            placeholder="e.g. Added AWS certification"
            style={{
              width: '100%', background: 'var(--bg-input)', border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)', padding: '0.65rem 1rem', color: 'var(--text-primary)',
              fontFamily: 'var(--font-primary)', fontSize: '0.9rem', outline: 'none',
              transition: 'border-color var(--transition-fast)',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--accent-primary)'}
            onBlur={e => e.target.style.borderColor = 'var(--border-subtle)'}
          />
        </div>

        <button
          className="btn btn-primary btn-full btn-lg"
          style={{ marginTop: '1.5rem' }}
          disabled={!file || uploading}
          onClick={handleUpload}
        >
          {uploading ? 'Analyzing…' : 'Analyze Resume →'}
        </button>

        {uploading && (
          <div className="progress-container">
            <div className="progress-header">
              <span>{progressLabel}</span>
              <span>{progress}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}

        {error && (
          <div className="tag tag-danger" style={{ marginTop: '1rem', padding: '0.75rem', width: '100%', justifyContent: 'center' }}>
            {error}
          </div>
        )}
      </div>

      {/* Features */}
      <div className="animate-in animate-in-delay-2" style={{
        display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center',
        marginTop: '2rem', paddingBottom: '2rem',
      }}>
        {FEATURES.map(f => (
          <div key={f.label} className="tag tag-default" style={{ gap: '0.4rem' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: f.color, display: 'inline-block' }} />
            {f.label}
          </div>
        ))}
      </div>
    </div>
  );
}

export default UploadPage;
