import React from 'react';
import { 
  Activity, 
  Settings, 
  Sun, 
  Moon, 
  BookOpen, 
  CheckCircle2, 
  AlertCircle, 
  Radio
} from 'lucide-react';

export default function Header({ 
  backendStatus, 
  activeMode, 
  theme, 
  onToggleTheme, 
  onOpenSettings, 
  onOpenGlossary 
}) {
  const isConnected = backendStatus === 'healthy';

  return (
    <header className="header-container">
      <div className="header-inner">
        {/* Brand & Wordmark */}
        <div className="header-brand">
          <div className="brand-logo" title="ISL Translation Studio">
            <svg 
              width="22" 
              height="22" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="2.2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            >
              <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"/>
              <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"/>
              <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"/>
              <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>
            </svg>
          </div>
          <div className="brand-titles">
            <span className="brand-name font-display">ISL Translation Studio</span>
            <span className="brand-tagline">Dual-Branch V3 • NLP • Multilingual</span>
          </div>
        </div>

        {/* Status Indicators & Controls */}
        <div className="header-actions">
          {/* Real Backend Connection Badge */}
          <div className={`status-badge ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
            <span className="status-dot"></span>
            <span className="status-label">
              {isConnected ? 'Backend Online (V3)' : 'Connecting Engine...'}
            </span>
          </div>

          {/* Mode Pill */}
          <div className="mode-pill" title="Current Active Recognition Mode">
            <Radio size={13} className="mode-pill-icon" />
            <span className="mode-pill-text">{activeMode} MODE</span>
          </div>

          <div className="header-divider"></div>

          {/* Glossary Button */}
          <button 
            onClick={onOpenGlossary} 
            className="action-btn"
            title="Browse 46 Supported ISL Signs"
          >
            <BookOpen size={16} />
            <span className="action-btn-text">Sign Lexicon</span>
          </button>

          {/* Settings Button */}
          <button 
            onClick={onOpenSettings} 
            className="action-btn"
            title="Configure Google Translate API Key & Thresholds"
          >
            <Settings size={16} />
          </button>

          {/* Theme Toggle */}
          <button 
            onClick={onToggleTheme} 
            className="action-btn theme-toggle-btn"
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>
        </div>
      </div>
    </header>
  );
}
