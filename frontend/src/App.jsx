import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { 
  Target, 
  User, 
  Cpu, 
  Search, 
  Sparkles, 
  Briefcase, 
  MessageSquare, 
  Code, 
  BarChart3, 
  Brain, 
  Shield 
} from 'lucide-react';

import CommandCenterPage from './pages/CommandCenterPage';
import CareerProfilePage from './pages/CareerProfilePage';
import ATSSimulatorPage from './pages/ATSSimulatorPage';
import JobIntelligencePage from './pages/JobIntelligencePage';
import ResumeTailorPage from './pages/ResumeTailorPage';
import ApplicationCRMPage from './pages/ApplicationCRMPage';
import InterviewCoachPage from './pages/InterviewCoachPage';
import PortfolioIntelligencePage from './pages/PortfolioIntelligencePage';
import AnalyticsPage from './pages/AnalyticsPage';

function Sidebar() {
  const location = useLocation();
  const navItems = [
    { path: '/', icon: <Target size={18} />, label: 'Command Center' },
    { path: '/profile', icon: <User size={18} />, label: 'Career Profile Twin' },
    { path: '/ats', icon: <Cpu size={18} />, label: 'Multi-ATS Simulator' },
    { path: '/jobs', icon: <Search size={18} />, label: 'Job Intelligence' },
    { path: '/tailor', icon: <Sparkles size={18} />, label: 'Resume Tailor' },
    { path: '/crm', icon: <Briefcase size={18} />, label: 'Application CRM' },
    { path: '/interview', icon: <MessageSquare size={18} />, label: 'Interview Coach' },
    { path: '/portfolio', icon: <Code size={18} />, label: 'Portfolio Intelligence' },
    { path: '/analytics', icon: <BarChart3 size={18} />, label: 'Hiring Analytics' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>ResumeIQ</h1>
        <span>Career Intelligence OS v2.0</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={item.path === '/'}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}

        <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div className="nav-item" style={{ cursor: 'default', opacity: 0.8 }}>
            <Brain size={18} />
            <span>FastAPI Engine</span>
            <span className="tag tag-info" style={{ marginLeft: 'auto', fontSize: '0.6rem' }}>v1 OS</span>
          </div>
          <div className="nav-item" style={{ cursor: 'default', opacity: 0.8 }}>
            <Shield size={18} />
            <span>No-Fabrication</span>
            <span className="tag tag-success" style={{ marginLeft: 'auto', fontSize: '0.6rem' }}>0% Fake</span>
          </div>
        </div>
      </nav>
    </aside>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<CommandCenterPage />} />
            <Route path="/profile" element={<CareerProfilePage />} />
            <Route path="/ats" element={<ATSSimulatorPage />} />
            <Route path="/jobs" element={<JobIntelligencePage />} />
            <Route path="/tailor" element={<ResumeTailorPage />} />
            <Route path="/crm" element={<ApplicationCRMPage />} />
            <Route path="/interview" element={<InterviewCoachPage />} />
            <Route path="/portfolio" element={<PortfolioIntelligencePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
