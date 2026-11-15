import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Upload, 
  Image as ImageIcon, 
  Sparkles, 
  CheckCircle2, 
  Plus, 
  RefreshCw, 
  Volume2, 
  Copy, 
  Check, 
  FileImage, 
  Layers, 
  Cpu, 
  AlertCircle, 
  Eye, 
  EyeOff,
  Clock,
  ArrowRight
} from 'lucide-react';

export default function ImageDetector({
  onAddSign,
  getApiUrl,
  threshold = 0.70
}) {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [annotatedImage, setAnnotatedImage] = useState(null);
  const [activeView, setActiveView] = useState('annotated'); // 'annotated' | 'original'
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [detectionResult, setDetectionResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const [addedFeedback, setAddedFeedback] = useState(false);
  
  // Sample test images
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [loadingSamples, setLoadingSamples] = useState(true);

  const fileInputRef = useRef(null);
  const dropZoneRef = useRef(null);

  // 1. Fetch Sample Test Images on mount
  useEffect(() => {
    let isMounted = true;
    const fetchSamples = async () => {
      try {
        const res = await fetch(getApiUrl('/api/detect/sample-images'));
        if (res.ok) {
          const data = await res.json();
          if (isMounted && data.samples) {
            setSamples(data.samples);
          }
        }
      } catch (err) {
        console.warn('Could not load sample images:', err);
      } finally {
        if (isMounted) setLoadingSamples(false);
      }
    };
    fetchSamples();
    return () => { isMounted = false; };
  }, [getApiUrl]);

  // 2. Core Image Analysis API Call
  const analyzeImage = useCallback(async (base64Data) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const res = await fetch(getApiUrl('/api/detect/image'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: base64Data,
          draw_landmarks: showSkeleton
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
        throw new Error(errData.detail || `Server error: ${res.status}`);
      }

      const data = await res.json();
      setDetectionResult(data);
      if (data.annotated_image) {
        setAnnotatedImage(data.annotated_image);
        setActiveView('annotated');
      } else {
        setActiveView('original');
      }
    } catch (err) {
      console.error('Image Detection Error:', err);
      setError(err.message || 'Failed to analyze sign image. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  }, [getApiUrl, showSkeleton]);

  // 3. Process File into Base64
  const processFile = useCallback((file) => {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please upload a valid image file (PNG, JPG, WEBP).');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const b64 = e.target.result;
      setUploadedImage(b64);
      setSelectedSample(null);
      analyzeImage(b64);
    };
    reader.onerror = () => {
      setError('Failed to read image file.');
    };
    reader.readAsDataURL(file);
  }, [analyzeImage]);

  // 4. File Drag & Drop Handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  // 5. Global Paste Listener for easy Ctrl+V image testing
  useEffect(() => {
    const handlePaste = (e) => {
      if (e.clipboardData && e.clipboardData.files.length > 0) {
        const file = e.clipboardData.files[0];
        if (file.type.startsWith('image/')) {
          processFile(file);
        }
      }
    };
    window.addEventListener('paste', handlePaste);
    return () => window.removeEventListener('paste', handlePaste);
  }, [processFile]);

  // 6. Load Pre-loaded Sample Sign Image
  const handleSelectSample = async (sample) => {
    setSelectedSample(sample.sign);
    setIsAnalyzing(true);
    setError(null);
    try {
      const url = getApiUrl(sample.image_url);
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Could not load sample image for ${sample.sign}`);
      const blob = await res.blob();
      const reader = new FileReader();
      reader.onload = (e) => {
        const b64 = e.target.result;
        setUploadedImage(b64);
        analyzeImage(b64);
      };
      reader.readAsDataURL(blob);
    } catch (err) {
      console.error('Error loading sample image:', err);
      setError(`Failed to load sample image for ${sample.sign}.`);
      setIsAnalyzing(false);
    }
  };

  // 7. Add Recognized Sign to Sentence Builder
  const handleAddToSentence = () => {
    if (!detectionResult?.sign || detectionResult.sign === 'No Hand Detected') return;
    if (onAddSign) {
      onAddSign(detectionResult.sign);
      setAddedFeedback(true);
      setTimeout(() => setAddedFeedback(false), 2000);
    }
  };

  // 8. Text-to-Speech
  const handleSpeak = () => {
    if (!detectionResult?.sign || detectionResult.sign === 'No Hand Detected') return;
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(detectionResult.sign);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  // 9. Copy to Clipboard
  const handleCopy = () => {
    if (!detectionResult?.sign || detectionResult.sign === 'No Hand Detected') return;
    navigator.clipboard.writeText(detectionResult.sign);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Reset to upload state
  const handleReset = () => {
    setUploadedImage(null);
    setAnnotatedImage(null);
    setDetectionResult(null);
    setError(null);
    setSelectedSample(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const sign = detectionResult?.sign;
  const confidence = detectionResult?.confidence || 0.0;
  const top3 = detectionResult?.top3 || [];
  const handsDetected = detectionResult?.hands_detected;
  const isHighConf = confidence >= threshold;

  return (
    <div className="image-detector-root">
      {/* 1. Header & Pre-loaded Quick Samples Bar */}
      <div className="image-detector-top-bar">
        <div className="detector-title-group">
          <div className="detector-icon-badge">
            <FileImage size={20} />
          </div>
          <div>
            <h2 className="detector-title font-display">Static Photo Symbol Detector</h2>
            <p className="detector-desc">
              Upload sign photos to extract Google MediaPipe skeletons and classify ISL symbols with the Residual MLP engine.
            </p>
          </div>
        </div>

        {/* Quick Samples Section */}
        {samples.length > 0 && (
          <div className="quick-samples-container">
            <span className="samples-label font-mono">Quick Test Samples:</span>
            <div className="samples-pills-list">
              {samples.map((s) => (
                <button
                  key={s.sign}
                  type="button"
                  className={`sample-pill-btn ${selectedSample === s.sign ? 'sample-active' : ''}`}
                  onClick={() => handleSelectSample(s)}
                  disabled={isAnalyzing}
                  title={`${s.title} — ${s.desc}`}
                >
                  <span className="sample-sign-pill">{s.sign}</span>
                  <span className="sample-category-badge">{s.category}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2. Main Studio Body: Upload Zone OR Result Split View */}
      {!uploadedImage ? (
        /* Empty / Upload Dropzone State */
        <div
          ref={dropZoneRef}
          className={`image-upload-dropzone ${isDragging ? 'dropzone-active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png, image/jpeg, image/jpg, image/webp"
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                processFile(e.target.files[0]);
              }
            }}
          />

          <div className="dropzone-inner-content">
            <div className="dropzone-icon-pulse">
              <Upload size={36} />
            </div>
            <h3 className="dropzone-heading font-display">
              {isDragging ? 'Drop photo here to analyze' : 'Drag & Drop Sign Photo, or Click to Browse'}
            </h3>
            <p className="dropzone-sub">
              Supports PNG, JPG, JPEG, WEBP • Paste directly from clipboard with <kbd>Ctrl</kbd> + <kbd>V</kbd>
            </p>
            <div className="dropzone-chips">
              <span className="chip-item">
                <Cpu size={12} /> Residual Dense MLP
              </span>
              <span className="chip-item">
                <Layers size={12} /> MediaPipe Holistic Skeleton
              </span>
              <span className="chip-item">
                <Sparkles size={12} /> 35 ISL Static Classes
              </span>
            </div>
          </div>
        </div>
      ) : (
        /* Active Image & Recognition Two-Column Workspace */
        <div className="image-workspace-two-column">
          {/* Left Column: Image Viewer with Skeleton Overlay Toggle */}
          <div className="image-viewer-column card-elevated">
            <div className="viewer-toolbar">
              <div className="viewer-tab-group">
                <button
                  type="button"
                  className={`viewer-tab-btn ${activeView === 'annotated' ? 'tab-active' : ''}`}
                  onClick={() => setActiveView('annotated')}
                  disabled={!annotatedImage}
                >
                  <Layers size={14} />
                  <span>MediaPipe Skeleton</span>
                </button>
                <button
                  type="button"
                  className={`viewer-tab-btn ${activeView === 'original' ? 'tab-active' : ''}`}
                  onClick={() => setActiveView('original')}
                >
                  <ImageIcon size={14} />
                  <span>Original Photo</span>
                </button>
              </div>

              <div className="viewer-actions">
                <button
                  type="button"
                  className="viewer-action-btn"
                  onClick={handleReset}
                  title="Upload a new sign photo"
                >
                  <RefreshCw size={13} />
                  <span>New Photo</span>
                </button>
              </div>
            </div>

            {/* Main Image Stage */}
            <div className="image-stage-container">
              {isAnalyzing && (
                <div className="stage-loading-overlay">
                  <div className="loading-spinner-ring" />
                  <span className="loading-text font-mono">Running MediaPipe Holistic & V3 Residual MLP...</span>
                </div>
              )}

              <img
                src={activeView === 'annotated' && annotatedImage ? annotatedImage : uploadedImage}
                alt="ISL Symbol Display"
                className="stage-display-image"
              />

              {/* Resolution / Meta Badge */}
              {detectionResult?.dimensions && (
                <div className="stage-meta-pill font-mono">
                  <span>{detectionResult.dimensions.width} × {detectionResult.dimensions.height} px</span>
                  {detectionResult.latency_ms && <span> • {detectionResult.latency_ms} ms</span>}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: High-Confidence Recognition Results Card */}
          <div className="image-result-column card-elevated">
            <div className="result-header">
              <span className="section-label">STATIC CLASSIFICATION RESULT</span>
              {detectionResult && (
                <div className={`status-badge-chip ${isHighConf ? 'badge-confirmed' : 'badge-warn'}`}>
                  {isHighConf ? (
                    <>
                      <CheckCircle2 size={13} /> High Confidence
                    </>
                  ) : (
                    <>
                      <AlertCircle size={13} /> Low Confidence
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Prominent Recognized Sign Banner */}
            <div className={`image-sign-hero-card ${isHighConf ? 'hero-confident' : ''}`}>
              <div className="hero-top-meta">
                <span className="hero-label">DETECTED ISL SYMBOL</span>
                <span className="hero-arch-badge font-mono">V3 MLP</span>
              </div>

              {isAnalyzing ? (
                <div className="hero-analyzing-state">
                  <span className="analyzing-shimmer">Processing pose...</span>
                </div>
              ) : sign ? (
                <div className="hero-sign-content">
                  <h1 className="hero-sign-title font-display">{sign}</h1>
                  <span className="hero-sign-subtitle">
                    {handsDetected ? 'Static Alphabet / Number Pose' : 'No hands tracked in image'}
                  </span>
                </div>
              ) : (
                <div className="hero-sign-content">
                  <h1 className="hero-sign-title font-display text-muted">Ready</h1>
                </div>
              )}

              {/* Confidence Gauge */}
              <div className="hero-confidence-meter">
                <div className="meter-label-row">
                  <span className="meter-title">Classification Confidence</span>
                  <span className="meter-value font-mono">{(confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="meter-track">
                  <div
                    className={`meter-bar ${isHighConf ? 'meter-high' : 'meter-med'}`}
                    style={{ width: `${Math.min(confidence * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Top 3 Candidate Probabilities */}
            {top3.length > 0 && (
              <div className="top3-breakdown-card">
                <div className="breakdown-header">
                  <span className="breakdown-title font-mono">TOP 3 RANKINGS</span>
                </div>
                <div className="top3-list">
                  {top3.map(([candSign, candProb], idx) => (
                    <div key={candSign} className="top3-item">
                      <div className="cand-rank font-mono">{idx + 1}</div>
                      <div className="cand-info">
                        <div className="cand-label-row">
                          <span className="cand-name font-mono font-bold">{candSign}</span>
                          <span className="cand-pct font-mono">{(candProb * 100).toFixed(1)}%</span>
                        </div>
                        <div className="cand-track">
                          <div
                            className={`cand-fill ${idx === 0 ? 'fill-primary' : 'fill-secondary'}`}
                            style={{ width: `${Math.min(candProb * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Detection Diagnostics Metrics */}
            {detectionResult && (
              <div className="diagnostics-mini-grid">
                <div className="diag-item">
                  <span className="diag-k">Hands Tracked</span>
                  <span className="diag-v font-mono">
                    {detectionResult.left_hand && detectionResult.right_hand
                      ? 'Both Hands'
                      : detectionResult.left_hand
                      ? 'Left Hand'
                      : detectionResult.right_hand
                      ? 'Right Hand'
                      : 'None'}
                  </span>
                </div>
                <div className="diag-item">
                  <span className="diag-k">Inference Time</span>
                  <span className="diag-v font-mono">{detectionResult.latency_ms || 0} ms</span>
                </div>
              </div>
            )}

            {/* Main Action Bar: Add to Sentence Builder & Utilities */}
            <div className="image-actions-bar">
              <button
                type="button"
                className={`btn-add-sentence ${addedFeedback ? 'btn-added' : ''}`}
                onClick={handleAddToSentence}
                disabled={!sign || sign === 'No Hand Detected' || isAnalyzing}
              >
                {addedFeedback ? (
                  <>
                    <Check size={16} /> Added to Sentence!
                  </>
                ) : (
                  <>
                    <Plus size={16} /> Add "{sign || 'Symbol'}" to Sentence Builder
                  </>
                )}
              </button>

              <div className="utility-buttons-row">
                <button
                  type="button"
                  className="btn-util"
                  onClick={handleSpeak}
                  disabled={!sign || sign === 'No Hand Detected'}
                  title="Speak symbol aloud"
                >
                  <Volume2 size={15} />
                  <span>Speak</span>
                </button>
                <button
                  type="button"
                  className="btn-util"
                  onClick={handleCopy}
                  disabled={!sign || sign === 'No Hand Detected'}
                  title="Copy symbol to clipboard"
                >
                  {copied ? <Check size={15} color="#10B981" /> : <Copy size={15} />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="image-detector-error-banner">
          <AlertCircle size={16} />
          <span>{error}</span>
          <button type="button" className="error-dismiss-btn" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
}
