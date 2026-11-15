import React, { useRef, useEffect } from 'react';
import { 
  Camera, 
  CameraOff, 
  FlipHorizontal, 
  Eye, 
  EyeOff, 
  Info, 
  AlertTriangle,
  Cpu,
  Globe,
  Sparkles
} from 'lucide-react';

export default function CameraStudio({
  videoRef,
  canvasRef,
  isCameraActive,
  isMirror,
  showLandmarks,
  showHudOverlay = true,
  cameraError,
  fps,
  cameraSource = 'native', // 'native' | 'browser'
  onChangeCameraSource,
  nativeStreamUrl,
  availableCameras = [],
  selectedCameraIndex = 0,
  onSelectCameraIndex,
  onToggleCamera,
  onToggleMirror,
  onToggleLandmarks,
  onToggleHudOverlay,
}) {
  const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

  return (
    <div className="camera-studio-container">
      {/* Studio Header Bar */}
      <div className="studio-header">
        <div className="studio-header-title">
          <span className="section-label">LIVE CAMERA STUDIO</span>
          
          {/* Camera Source Switcher Pill */}
          <div className="camera-source-segmented">
            <button
              type="button"
              className={`source-segment-btn ${cameraSource === 'native' ? 'active' : ''}`}
              onClick={() => onChangeCameraSource && onChangeCameraSource('native')}
              title="Direct hardware camera via local Python server (Best for localhost)"
            >
              <Cpu size={12} className="source-btn-icon" />
              <span>Direct MediaPipe</span>
              <span className="source-tag-recommended">{isLocal ? 'LOCAL' : 'OFFLINE'}</span>
            </button>
            <button
              type="button"
              className={`source-segment-btn ${cameraSource === 'browser' ? 'active' : ''}`}
              onClick={() => onChangeCameraSource && onChangeCameraSource('browser')}
              title="Browser WebRTC camera (Required for cloud website access)"
            >
              <Globe size={12} className="source-btn-icon" />
              <span>Browser WebRTC</span>
              <span className="source-tag-recommended">CLOUD</span>
            </button>
          </div>

          {/* Camera Hardware Device Dropdown (Iriun Webcam, USB Webcams) */}
          {cameraSource === 'native' && availableCameras && availableCameras.length > 0 && (
            <div className="camera-device-select-wrapper">
              <select
                className="camera-device-select font-mono"
                value={selectedCameraIndex}
                onChange={(e) => onSelectCameraIndex && onSelectCameraIndex(Number(e.target.value))}
                title="Select camera hardware device (e.g. Iriun Webcam or USB webcam)"
              >
                {availableCameras.map((cam) => (
                  <option key={cam.index} value={cam.index}>
                    {cam.is_iriun ? '📱 ' : '📷 '}
                    {cam.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="studio-header-stats">
          {isCameraActive && (
            <span className="live-stat-pill">
              <span className="live-pulse"></span>
              {cameraSource === 'native' ? 'DIRECT MEDIAPIPE' : 'WEBRTC FEED'}
              {fps > 0 ? ` • ${fps} FPS` : ''}
            </span>
          )}
        </div>
      </div>

      {!isLocal && cameraSource === 'native' && (
        <div style={{ background: 'rgba(234, 179, 8, 0.15)', border: '1px solid #eab308', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#fef08a', margin: '0 16px 12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
          <span>⚠️ <strong>Cloud Server Notice:</strong> Direct MediaPipe accesses the host computer's USB camera (when running locally). On the cloud website, please click <strong>Browser WebRTC</strong> to use your laptop or phone camera!</span>
          <button 
            type="button" 
            onClick={() => onChangeCameraSource && onChangeCameraSource('browser')}
            style={{ background: '#eab308', color: '#000', border: 'none', borderRadius: '6px', padding: '6px 12px', fontWeight: 'bold', cursor: 'pointer', whiteSpace: 'nowrap' }}
          >
            Switch to Browser WebRTC
          </button>
        </div>
      )}

      {/* Main Viewport */}
      <div className="camera-viewport-frame">
        {/* 1. Direct Native MediaPipe Stream (Recommended: High-Precision OpenCV + MediaPipe) */}
        {cameraSource === 'native' && isCameraActive && nativeStreamUrl && (
          <img
            key={nativeStreamUrl}
            src={nativeStreamUrl}
            alt="Google MediaPipe Holistic Live Feed"
            className={`camera-video-element ${isMirror ? 'mirrored' : ''}`}
            crossOrigin="anonymous"
          />
        )}

        {/* 2. Browser WebRTC Video Source (Fallback) */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`camera-video-element ${isMirror ? 'mirrored' : ''}`}
          style={{ display: (cameraSource === 'browser' && isCameraActive) ? 'block' : 'none' }}
        />

        {/* Overlay Canvas for Skeletal Landmarks in Browser Mode */}
        <canvas
          ref={canvasRef}
          className={`camera-canvas-overlay ${isMirror ? 'mirrored' : ''}`}
          style={{ display: (cameraSource === 'browser' && isCameraActive && showLandmarks) ? 'block' : 'none' }}
        />

        {/* Positioning Guide Outline */}
        {isCameraActive && (
          <div className="camera-positioning-guide">
            <div className="guide-box">
              <span className="guide-hint">
                {cameraSource === 'native' 
                  ? '✨ Native MediaPipe Holistic V3 Stream • DirectShow 720p HD' 
                  : 'Align upper body & hands within frame'}
              </span>
            </div>
          </div>
        )}

        {/* Inactive / Error Overlay */}
        {!isCameraActive && (
          <div className="camera-placeholder">
            {cameraError ? (
              <div className="camera-error-content">
                <AlertTriangle size={36} className="error-icon" />
                <h4 className="error-title">Camera Access Notice</h4>
                <p className="error-desc">{cameraError}</p>
                <button onClick={onToggleCamera} className="primary-btn retry-btn">
                  <Camera size={16} /> Try Camera Again
                </button>
              </div>
            ) : (
              <div className="camera-standby-content">
                <div className="standby-icon-circle">
                  <Camera size={32} />
                </div>
                <h4 className="standby-title font-display">
                  {cameraSource === 'native' ? 'Direct MediaPipe Studio Standby' : 'Browser Camera Inactive'}
                </h4>
                <p className="standby-desc">
                  {cameraSource === 'native'
                    ? 'Captures directly from your webcam with Google MediaPipe Holistic in Python (1280x720 @ 30 FPS) with compiled V3 models.'
                    : 'Start the browser camera to begin real-time Indian Sign Language detection and translation.'}
                </p>
                <button onClick={onToggleCamera} className="primary-btn start-camera-btn">
                  <Camera size={16} /> {cameraSource === 'native' ? 'Start Direct MediaPipe Feed' : 'Start Browser Webcam'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Control Bar beneath Camera */}
      <div className="camera-controls-bar">
        <div className="controls-left">
          <button
            onClick={onToggleCamera}
            className={`control-pill-btn ${isCameraActive ? 'btn-active-red' : 'btn-active-green'}`}
          >
            {isCameraActive ? (
              <>
                <CameraOff size={15} /> Stop Camera
              </>
            ) : (
              <>
                <Camera size={15} /> Start Camera
              </>
            )}
          </button>
        </div>

        <div className="controls-right">
          <button
            onClick={onToggleMirror}
            className={`control-icon-btn ${isMirror ? 'active' : ''}`}
            title="Mirror preview for natural self-view"
            disabled={!isCameraActive}
          >
            <FlipHorizontal size={15} />
            <span className="btn-label-text">Mirror</span>
          </button>

          <button
            onClick={onToggleLandmarks}
            className={`control-icon-btn ${showLandmarks ? 'active' : ''}`}
            title="Toggle MediaPipe skeletal landmark overlay [H]"
            disabled={!isCameraActive}
          >
            {showLandmarks ? <Eye size={15} /> : <EyeOff size={15} />}
            <span className="btn-label-text">Skeletons</span>
          </button>

          {cameraSource === 'native' && (
            <button
              onClick={onToggleHudOverlay}
              className={`control-icon-btn ${showHudOverlay ? 'active' : ''}`}
              title="Toggle authentic V3 Engine HUD overlay (Top banner, hold commit bar, candidates, translation ribbon)"
              disabled={!isCameraActive}
            >
              <Sparkles size={15} />
              <span className="btn-label-text">V3 HUD</span>
            </button>
          )}
        </div>
      </div>

      {/* Shortcuts Quick Strip */}
      <div className="camera-shortcuts-strip font-mono" style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '6px',
        padding: '7px 14px',
        background: 'rgba(15, 23, 42, 0.45)',
        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
        fontSize: '11px',
        color: '#94a3b8'
      }}>
        <span><strong style={{ color: '#00e5ff' }}>[TAB/M]</strong> Toggle Mode</span>
        <span><strong style={{ color: '#69f0ae' }}>[1]</strong> Static</span>
        <span><strong style={{ color: '#ffb74d' }}>[2]</strong> Dynamic</span>
        <span><strong style={{ color: '#ffd54f' }}>[SPACE]</strong> Add Sign</span>
        <span><strong style={{ color: '#ef5350' }}>[C]</strong> Clear</span>
        <span><strong style={{ color: '#ab47bc' }}>[BKSP]</strong> Delete</span>
        <span><strong style={{ color: '#4fc3f7' }}>[H]</strong> Skeletons</span>
      </div>
    </div>
  );
}

