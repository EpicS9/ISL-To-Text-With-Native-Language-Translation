import React, { useState } from 'react';
import { 
  Plus, 
  Trash2, 
  RotateCcw, 
  CornerDownLeft, 
  Space, 
  Edit3, 
  X,
  ListFilter
} from 'lucide-react';

export default function SentenceBuilder({
  glosses,
  onAddGloss,
  onRemoveGloss,
  onUndoLast,
  onClearAll,
  onInsertSpace,
}) {
  const [manualInput, setManualInput] = useState('');

  const handleManualSubmit = (e) => {
    e.preventDefault();
    if (manualInput.trim()) {
      onAddGloss(manualInput.trim().toUpperCase());
      setManualInput('');
    }
  };

  return (
    <div className="sentence-builder-container">
      <div className="builder-header">
        <div className="builder-title-group">
          <span className="section-label">SENTENCE BUILDER — GLOSS TIMELINE</span>
          <span className="token-counter font-mono">
            {glosses.length} {glosses.length === 1 ? 'TOKEN' : 'TOKENS'}
          </span>
        </div>

        {/* Builder Quick Actions */}
        <div className="builder-actions">
          <button
            onClick={onInsertSpace}
            className="builder-action-btn"
            title="Insert space boundary between words"
          >
            <Space size={14} /> Space
          </button>

          <button
            onClick={onUndoLast}
            disabled={glosses.length === 0}
            className="builder-action-btn"
            title="Undo last recognized sign token"
          >
            <RotateCcw size={14} /> Undo
          </button>

          <button
            onClick={onClearAll}
            disabled={glosses.length === 0}
            className="builder-action-btn btn-danger"
            title="Clear all accumulated tokens"
          >
            <Trash2 size={14} /> Clear
          </button>
        </div>
      </div>

      {/* Horizontal Token Flow Ribbon */}
      <div className="gloss-ribbon-wrapper">
        <div className="gloss-ribbon">
          {glosses.length === 0 ? (
            <div className="gloss-empty-state">
              <span className="empty-hint">
                Committed signs from the camera will appear here sequentially as tokens (e.g. <code>[HELLO]</code> <code>[NAME]</code> <code>[YOU]</code>).
              </span>
            </div>
          ) : (
            glosses.map((token, index) => {
              if (token === ' ') {
                return (
                  <div key={index} className="space-token-pill" title="Space separator">
                    <span className="space-dash">—</span>
                    <button 
                      onClick={() => onRemoveGloss(index)} 
                      className="token-remove-btn"
                    >
                      <X size={10} />
                    </button>
                  </div>
                );
              }
              return (
                <div key={index} className="gloss-token-chip">
                  <span className="token-index font-mono">{index + 1}</span>
                  <span className="token-text font-mono">{token}</span>
                  <button
                    onClick={() => onRemoveGloss(index)}
                    className="token-remove-btn"
                    title={`Remove '${token}'`}
                  >
                    <X size={11} />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Manual Input Bar */}
      <div className="builder-footer-bar">
        <form onSubmit={handleManualSubmit} className="manual-input-form">
          <Edit3 size={14} className="manual-input-icon" />
          <input
            type="text"
            placeholder="Manual sign entry (e.g. type 'THANKYOU' or letters 'R-O-O-P')..."
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            className="manual-input-field font-mono"
          />
          <button 
            type="submit" 
            disabled={!manualInput.trim()} 
            className="manual-add-btn"
          >
            <Plus size={13} /> Add Token
          </button>
        </form>

        <div className="builder-help-hint">
          <span>Click any token's ✕ to delete • Hold signs in camera to auto-commit</span>
        </div>
      </div>
    </div>
  );
}
