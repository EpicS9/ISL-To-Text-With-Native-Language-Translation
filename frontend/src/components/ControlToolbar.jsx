import React from 'react';
import { 
  Sliders, 
  Clock, 
  HelpCircle, 
  Check, 
  Layers, 
  ToggleLeft, 
  ToggleRight 
} from 'lucide-react';

export default function ControlToolbar({
  activeMode,
  threshold,
  debounceHold,
  onChangeMode,
  onChangeThreshold,
  onChangeDebounceHold,
}) {
  return (
    <div className="control-toolbar-container">
      <div className="toolbar-inner">
        {/* Mode Toggle Switch */}
        <div className="toolbar-section mode-toggle-section">
          <span className="control-label">RECOGNITION MODE</span>
          <div className="mode-segmented-control">
            <button
              onClick={() => onChangeMode('STATIC')}
              className={`mode-segment-btn ${activeMode === 'STATIC' ? 'active' : ''}`}
              title="Recognize static alphabets (A-Z) and numbers (0-9)"
            >
              <span className="segment-indicator"></span>
              <div className="segment-texts">
                <span className="segment-title">STATIC</span>
                <span className="segment-subtitle">35 Signs (A-Z, 0-9)</span>
              </div>
            </button>

            <button
              onClick={() => onChangeMode('DYNAMIC')}
              className={`mode-segment-btn ${activeMode === 'DYNAMIC' ? 'active' : ''}`}
              title="Recognize temporal movement gestures (Hello, Thank You, etc.)"
            >
              <span className="segment-indicator"></span>
              <div className="segment-texts">
                <span className="segment-title">DYNAMIC</span>
                <span className="segment-subtitle">11 Signs (Motion)</span>
              </div>
            </button>
          </div>
        </div>

        {/* Confidence Threshold Slider */}
        <div className="toolbar-section slider-section">
          <div className="slider-header">
            <span className="control-label">CONFIDENCE THRESHOLD</span>
            <span className="slider-value-display font-mono">
              {(threshold * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0.60"
            max="0.95"
            step="0.05"
            value={threshold}
            onChange={(e) => onChangeThreshold(parseFloat(e.target.value))}
            className="styled-slider"
          />
          <div className="slider-hints">
            <span>60% (Lenient)</span>
            <span style={{ color: '#00e5ff', fontWeight: 600 }}>
              {activeMode === 'STATIC' ? '70% (V3 Default)' : '75% (V3 Default)'}
            </span>
            <span>95% (Strict)</span>
          </div>
        </div>

        {/* Debounce Hold Interval Slider */}
        <div className="toolbar-section slider-section">
          <div className="slider-header">
            <span className="control-label">COMMIT STABILITY HOLD</span>
            <span className="slider-value-display font-mono">
              {debounceHold.toFixed(2)}s
            </span>
          </div>
          <input
            type="range"
            min="0.20"
            max="1.20"
            step="0.10"
            value={debounceHold}
            onChange={(e) => onChangeDebounceHold(parseFloat(e.target.value))}
            className="styled-slider"
          />
          <div className="slider-hints">
            <span>0.2s (Fast)</span>
            <span>0.4s (Balanced)</span>
            <span>1.2s (Deliberate)</span>
          </div>
        </div>

        {/* Informative Guidance Note */}
        <div className="toolbar-section info-section">
          <div className="info-box">
            <HelpCircle size={14} className="info-icon" />
            <p className="info-text">
              <strong>Engine Note:</strong> Switching to <code>{activeMode}</code> completely isolates the active model branch to prevent false triggers. Gestures must hold steady for {debounceHold}s to commit.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
