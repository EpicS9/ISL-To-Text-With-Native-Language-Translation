import React from 'react';
import { 
  Zap, 
  Cpu, 
  Clock, 
  Sliders, 
  CheckCircle, 
  HelpCircle,
  Layers
} from 'lucide-react';

export default function RecognitionPanel({
  activeMode,
  prediction,
  latencyMs,
  fps,
  threshold,
  commitProgress = 0.0,
  isCameraActive,
  committedSign
}) {
  const sign = prediction?.sign;
  const confidence = prediction?.confidence || 0.0;
  const top3 = prediction?.top3 || [];
  const status = prediction?.status || 'idle';

  const isDetected = status === 'detected' && confidence >= threshold;
  const isRecognizing = status === 'recognizing' || (confidence > 0.3 && confidence < threshold);
  const isNoHand = status === 'no_hand';

  // Model architecture name
  const modelName = activeMode === 'STATIC' 
    ? 'Residual Dense MLP (35 Classes)' 
    : 'Conv1D + BiLSTM + Attention (11 Classes)';

  return (
    <div className="recognition-panel-container">
      {/* Panel Header */}
      <div className="panel-header">
        <span className="section-label">REAL-TIME INFERENCE PANEL</span>
        <div className="model-chip" title="Active Model Architecture">
          <Cpu size={13} />
          <span>{activeMode}: {activeMode === 'STATIC' ? 'Residual MLP' : 'BiLSTM-Attn'}</span>
        </div>
      </div>

      {/* Main Sign Display Box */}
      <div className={`sign-display-card ${isDetected ? 'card-committed' : ''}`}>
        <div className="sign-display-meta">
          <span className="sign-meta-label">RECOGNIZED SIGN GLOSS</span>
          {isDetected && (
            <span className="commit-badge">
              <CheckCircle size={12} /> Passed Threshold
            </span>
          )}
        </div>

        <div className="sign-primary-area">
          {!isCameraActive ? (
            <div className="sign-empty-state">
              <span className="empty-title">Camera Paused</span>
              <span className="empty-sub">Start camera stream to begin gesture recognition</span>
            </div>
          ) : isNoHand ? (
            <div className="sign-empty-state">
              <span className="empty-title">No Hands Detected</span>
              <span className="empty-sub">Bring hands into camera view to recognize signs</span>
            </div>
          ) : status === 'moving' ? (
            <div className="sign-empty-state">
              <span className="empty-title" style={{ color: '#F59E0B' }}>Hand In Motion</span>
              <span className="empty-sub">Hold hand steady to sign • Press [TAB] / [M] for Dynamic gestures</span>
            </div>
          ) : sign ? (
            <div className="sign-value-wrapper">
              <h1 className="sign-value font-display">{sign}</h1>
              <div className="sign-meta-type">
                <span>{activeMode} SIGN</span>
              </div>
            </div>
          ) : (
            <div className="sign-empty-state">
              <span className="empty-title">Scanning Pose...</span>
              <span className="empty-sub">Hold hand steady or perform dynamic sign</span>
            </div>
          )}
        </div>

        {/* Confidence Gauge Bar */}
        <div className="confidence-gauge-section">
          <div className="gauge-labels">
            <span className="gauge-title">Model Confidence</span>
            <span className="gauge-val font-mono">
              {(confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="gauge-track">
            <div 
              className={`gauge-fill ${confidence >= threshold ? 'fill-high' : 'fill-low'}`}
              style={{ width: `${Math.min(confidence * 100, 100)}%` }}
            ></div>
            <div 
              className="threshold-marker" 
              style={{ left: `${threshold * 100}%` }}
              title={`Commit Threshold: ${(threshold * 100).toFixed(0)}%`}
            ></div>
          </div>
          <div className="gauge-footer-note">
            <span>Threshold: {(threshold * 100).toFixed(0)}%</span>
            <span>{confidence >= threshold ? 'Confidence Passed' : 'Building Consensus'}</span>
          </div>
        </div>

        {/* Real-Time Commit Progress Bar (V3 Engine Feature Parity) */}
        {activeMode === 'STATIC' ? (
          <div className="confidence-gauge-section" style={{ marginTop: '14px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '10px' }}>
            <div className="gauge-labels">
              <span className="gauge-title" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Clock size={12} color="#00e5ff" />
                <span>Hold Stability Commit (0.4s)</span>
              </span>
              <span className="gauge-val font-mono" style={{ color: commitProgress >= 1.0 ? '#00e676' : '#00e5ff' }}>
                {(commitProgress * 100).toFixed(0)}%
              </span>
            </div>
            <div className="gauge-track" style={{ height: '7px' }}>
              <div 
                className="gauge-fill"
                style={{ 
                  width: `${Math.min(commitProgress * 100, 100)}%`,
                  background: commitProgress >= 1.0 ? 'linear-gradient(90deg, #00e676, #69f0ae)' : 'linear-gradient(90deg, #00b0ff, #00e5ff)',
                  transition: 'width 0.05s ease-out'
                }}
              ></div>
            </div>
            <div className="gauge-footer-note">
              <span>{commitProgress > 0 ? (commitProgress >= 1.0 ? '✓ Auto-Committed!' : 'Keep steady...') : 'Hold sign still to commit'}</span>
              <span>[SPACE] Instant Add</span>
            </div>
          </div>
        ) : (
          <div className="confidence-gauge-section" style={{ marginTop: '14px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '10px' }}>
            <div className="gauge-labels">
              <span className="gauge-title" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Zap size={12} color="#ff9100" />
                <span>BiLSTM Attention Window</span>
              </span>
              <span className="gauge-val font-mono" style={{ color: confidence >= threshold ? '#00e676' : '#ff9100' }}>
                {confidence >= threshold ? 'Ready' : 'Rolling (30F)'}
              </span>
            </div>
            <div className="gauge-track" style={{ height: '7px' }}>
              <div 
                className="gauge-fill"
                style={{ 
                  width: `${Math.min((confidence / Math.max(0.01, threshold)) * 100, 100)}%`,
                  background: confidence >= threshold ? 'linear-gradient(90deg, #00e676, #69f0ae)' : 'linear-gradient(90deg, #ff9100, #ffab40)',
                  transition: 'width 0.08s ease-out'
                }}
              ></div>
            </div>
            <div className="gauge-footer-note">
              <span>Continuous motion gesture</span>
              <span>1.0s cooldown</span>
            </div>
          </div>
        )}
      </div>

      {/* Top 3 Prediction Distribution */}
      <div className="top3-distribution-card">
        <div className="top3-header">
          <span className="sub-label">PROBABILITY DISTRIBUTION (TOP 3)</span>
          <Layers size={13} className="sub-icon" />
        </div>

        <div className="top3-list">
          {top3.length > 0 ? (
            top3.map(([candLabel, candProb], idx) => (
              <div key={idx} className="top3-row">
                <span className="top3-rank font-mono">0{idx + 1}</span>
                <span className="top3-name font-mono">{candLabel}</span>
                <div className="top3-bar-container">
                  <div 
                    className="top3-bar-fill" 
                    style={{ width: `${Math.min(candProb * 100, 100)}%` }}
                  ></div>
                </div>
                <span className="top3-percent font-mono">
                  {(candProb * 100).toFixed(1)}%
                </span>
              </div>
            ))
          ) : (
            <div className="top3-empty font-mono">
              <span>Awaiting model inference candidate stream...</span>
            </div>
          )}
        </div>
      </div>

      {/* Real Diagnostics Footer */}
      <div className="inference-diagnostics-grid">
        <div className="diagnostic-cell">
          <span className="diag-label">INFERENCE TIME</span>
          <span className="diag-val font-mono">
            {latencyMs > 0 ? `${latencyMs} ms` : '—'}
          </span>
        </div>

        <div className="diagnostic-cell">
          <span className="diag-label">STREAM FPS</span>
          <span className="diag-val font-mono">
            {fps > 0 ? `${fps} FPS` : '—'}
          </span>
        </div>

        <div className="diagnostic-cell">
          <span className="diag-label">ENGINE COMPILATION</span>
          <span className="diag-val font-mono">@tf.function</span>
        </div>
      </div>
    </div>
  );
}
