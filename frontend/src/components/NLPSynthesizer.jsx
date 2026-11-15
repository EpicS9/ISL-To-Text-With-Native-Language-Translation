import React, { useState } from 'react';
import { 
  Sparkles, 
  Copy, 
  Check, 
  RefreshCw, 
  ArrowRight, 
  BookType 
} from 'lucide-react';

export default function NLPSynthesizer({
  glosses,
  synthesizedEnglish,
  isSynthesizing,
  onTriggerSynthesize,
  onUpdateEnglish,
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (synthesizedEnglish) {
      navigator.clipboard.writeText(synthesizedEnglish);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="nlp-synthesizer-container">
      <div className="synthesizer-header">
        <div className="synthesizer-title-group">
          <Sparkles size={16} className="sparkles-icon" />
          <span className="section-label">NLP GRAMMAR & SENTENCE SYNTHESIS</span>
        </div>

        <div className="synthesizer-actions">
          <button
            onClick={onTriggerSynthesize}
            disabled={glosses.length === 0 || isSynthesizing}
            className="synthesize-btn"
            title="Restructure glosses into fluent English"
          >
            <RefreshCw size={13} className={isSynthesizing ? 'spin' : ''} />
            <span>{isSynthesizing ? 'Restructuring...' : 'Synthesize English'}</span>
          </button>
        </div>
      </div>

      <div className="synthesizer-body">
        {/* Comparison Row: Raw ISL -> Structured English */}
        <div className="synthesis-comparison-grid">
          {/* Left: Input Gloss */}
          <div className="synthesis-card input-card">
            <span className="card-micro-label">INPUT ISL GLOSS SEQUENCE</span>
            <div className="card-content-area">
              {glosses.length > 0 ? (
                <div className="glosses-pill-preview font-mono">
                  {glosses.join(' ')}
                </div>
              ) : (
                <span className="card-placeholder-text">
                  Awaiting sign tokens from sentence builder...
                </span>
              )}
            </div>
            <div className="card-footer-info">
              <span>Grammar: Subject-Object-Verb (SOV)</span>
            </div>
          </div>

          <div className="synthesis-arrow-divider">
            <ArrowRight size={18} />
          </div>

          {/* Right: Synthesized English Output */}
          <div className="synthesis-card output-card">
            <div className="output-card-header">
              <span className="card-micro-label">SYNTHESIZED NATURAL ENGLISH</span>
              {synthesizedEnglish && (
                <button 
                  onClick={handleCopy} 
                  className="copy-btn" 
                  title="Copy English sentence"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              )}
            </div>

            <div className="card-content-area">
              <textarea
                value={synthesizedEnglish}
                onChange={(e) => onUpdateEnglish(e.target.value)}
                placeholder="Synthesized natural English output will appear here. You can also edit it directly before translation."
                className="english-textarea font-display"
                rows={2}
              />
            </div>

            <div className="card-footer-info">
              <span>Grammar: SVO Standard English • Punctuation Applied</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
