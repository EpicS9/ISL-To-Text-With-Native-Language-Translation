import React, { useState } from 'react';
import { 
  X, 
  Key, 
  ShieldCheck, 
  Cpu, 
  Info, 
  Check, 
  ExternalLink,
  Camera
} from 'lucide-react';

export default function SettingsModal({
  isOpen,
  onClose,
  googleApiKey,
  onSaveApiKey,
  customBackendUrl,
  modelsInfo,
  backendStatus,
  threshold = 0.80,
  onChangeThreshold,
  debounceHold = 0.80,
  onChangeDebounceHold,
}) {
  const [keyInput, setKeyInput] = useState(googleApiKey || '');
  const [backendUrlInput, setBackendUrlInput] = useState(customBackendUrl || '');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [savedBackendSuccess, setSavedBackendSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSaveApiKey(keyInput.trim());
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
  };

  const handleClear = () => {
    setKeyInput('');
    onSaveApiKey('');
  };

  const handleSaveBackend = (e) => {
    e.preventDefault();
    onSaveBackendUrl(backendUrlInput.trim());
    setSavedBackendSuccess(true);
    setTimeout(() => setSavedBackendSuccess(false), 2000);
  };

  const handleResetBackend = () => {
    setBackendUrlInput('');
    onSaveBackendUrl('');
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="section-label">STUDIO SETTINGS & DIAGNOSTICS</span>
            <h3 className="modal-title font-display">System Configuration</h3>
          </div>
          <button onClick={onClose} className="modal-close-btn">
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Section 1: Google Cloud Translation API */}
          <div className="settings-section">
            <div className="settings-section-header">
              <Key size={16} className="settings-icon" />
              <div>
                <h4 className="settings-h4">Google Cloud Translation API</h4>
                <p className="settings-desc">
                  Provide your Google Cloud API key for direct access to Neural Machine Translation (NMT). The key is stored locally in your browser.
                </p>
              </div>
            </div>

            <form onSubmit={handleSave} className="api-key-form">
              <input
                type="password"
                placeholder="AIzaSy..."
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                className="api-key-input font-mono"
              />
              <div className="api-key-actions">
                <button type="submit" className="save-btn">
                  {savedSuccess ? (
                    <>
                      <Check size={14} /> Saved
                    </>
                  ) : (
                    'Save Key'
                  )}
                </button>
                {googleApiKey && (
                  <button type="button" onClick={handleClear} className="clear-btn">
                    Remove
                  </button>
                )}
              </div>
            </form>

            <div className="key-status-indicator">
              <ShieldCheck size={14} className={googleApiKey ? 'text-green' : 'text-gray'} />
              <span>
                {googleApiKey 
                  ? 'Active: Google Cloud Translation API will be used for multilingual requests.' 
                  : 'Inactive: System is currently using the offline linguistic dictionary.'}
              </span>
            </div>
          </div>

          <div className="settings-divider"></div>

          {/* Section 2: Backend Server Engine URL (Vercel & Cloud Deployments) */}
          <div className="settings-section">
            <div className="settings-section-header">
              <Cpu size={16} className="settings-icon" />
              <div>
                <h4 className="settings-h4">Backend Engine Server URL</h4>
                <p className="settings-desc">
                  When deployed on Vercel or cloud hosting, specify your Python backend server URL (e.g. <code>https://your-backend.onrender.com</code>). Leave blank for default local server.
                </p>
              </div>
            </div>

            <form onSubmit={handleSaveBackend} className="api-key-form">
              <input
                type="text"
                placeholder="http://127.0.0.1:8000 or https://..."
                value={backendUrlInput}
                onChange={(e) => setBackendUrlInput(e.target.value)}
                className="api-key-input font-mono"
              />
              <div className="api-key-actions">
                <button type="submit" className="save-btn">
                  {savedBackendSuccess ? (
                    <>
                      <Check size={14} /> Saved
                    </>
                  ) : (
                    'Set URL'
                  )}
                </button>
                {customBackendUrl && (
                  <button type="button" onClick={handleResetBackend} className="clear-btn">
                    Reset
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="settings-divider"></div>

          {/* Section 2.5: Recognition Confidence & Commit Time Gap Controls */}
          <div className="settings-section">
            <div className="settings-section-header">
              <Cpu size={16} className="settings-icon" />
              <div>
                <h4 className="settings-h4">Recognition Sensitivity & Commit Timing</h4>
                <p className="settings-desc">
                  Tune confidence threshold and hold duration to guarantee the system only prints when you are confident in the symbol.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '10px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '13px' }}>
                  <span>Confidence Threshold</span>
                  <span className="font-mono font-semibold" style={{ color: '#00E5FF' }}>
                    {(threshold * 100).toFixed(0)}% Certainty
                  </span>
                </div>
                <input
                  type="range"
                  min="0.50"
                  max="0.95"
                  step="0.05"
                  value={threshold}
                  onChange={(e) => onChangeThreshold && onChangeThreshold(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#00E5FF', cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                  <span>50% (Permissive)</span>
                  <span>80% (Recommended)</span>
                  <span>95% (Strict)</span>
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '13px' }}>
                  <span>Hold Time Gap Before Commit</span>
                  <span className="font-mono font-semibold" style={{ color: '#69F0AE' }}>
                    {debounceHold.toFixed(2)}s Duration
                  </span>
                </div>
                <input
                  type="range"
                  min="0.40"
                  max="2.00"
                  step="0.10"
                  value={debounceHold}
                  onChange={(e) => onChangeDebounceHold && onChangeDebounceHold(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: '#69F0AE', cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                  <span>0.4s (Fast)</span>
                  <span>0.8s (Steady deliberate hold)</span>
                  <span>2.0s (Very slow)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="settings-divider"></div>

          {/* Section 3: Technical Diagnostics */}
          <div className="settings-section">
            <div className="settings-section-header">
              <ShieldCheck size={16} className="settings-icon" />
              <div>
                <h4 className="settings-h4">Engine Diagnostics</h4>
                <p className="settings-desc">
                  Active TensorFlow graphs, model parameters, and runtime environment.
                </p>
              </div>
            </div>

            <div className="diagnostics-table font-mono">
              <div className="diag-table-row">
                <span className="diag-col-name">Backend Status</span>
                <span className="diag-col-val font-semibold">
                  {backendStatus === 'healthy' ? 'Online & Healthy' : 'Degraded / Reconnecting'}
                </span>
              </div>
              <div className="diag-table-row">
                <span className="diag-col-name">Static Model</span>
                <span className="diag-col-val">Residual Dense MLP (35 Classes: 0-9, A-Z)</span>
              </div>
              <div className="diag-table-row">
                <span className="diag-col-name">Dynamic Model</span>
                <span className="diag-col-val">Conv1D + BiLSTM + Attention (11 Motion Classes)</span>
              </div>
              <div className="diag-table-row">
                <span className="diag-col-name">Feature Dimensions</span>
                <span className="diag-col-val">534 Normalized Landmarks (Pose + Hands + Face)</span>
              </div>
              <div className="diag-table-row">
                <span className="diag-col-name">Temporal Window</span>
                <span className="diag-col-val">30 Frames FIFO Buffer (1.0 second context)</span>
              </div>
              <div className="diag-table-row">
                <span className="diag-col-name">Graph Acceleration</span>
                <span className="diag-col-val">@tf.function compiled DirectML/CPU (~2ms)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button onClick={onClose} className="primary-btn">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
