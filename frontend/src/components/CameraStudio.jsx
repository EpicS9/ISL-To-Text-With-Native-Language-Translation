import React from 'react';
import {
  Camera,
  CameraOff,
  FlipHorizontal,
  Eye,
  EyeOff,
  AlertTriangle,
  Cpu
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
  availableCameras = [],
  selectedCameraId = '',
  onSelectCameraId,
  onToggleCamera,
  onToggleMirror,
  onToggleLandmarks,
}) {
  return (
    <div className="camera-studio-container">
      {/* Studio Header Bar */}
      <div className="studio-header">
        <div className="studio-header-title">
          <span className="section-label">LIVE CAMERA STUDIO</span>

          {/* Camera Hardware Device Dropdown (Auto-detects all connected cameras) */}
          {availableCameras && availableCameras.length > 0 && (
            <div className="camera-device-select-wrapper">
              <select
                className="camera-device-select font-mono"
                value={selectedCameraId}
                onChange={(e) => onSelectCameraId && onSelectCameraId(e.target.value)}
                title="Select camera hardware device (e.g. Integrated Camera, USB Webcam, or Iriun)"
              >
                {availableCameras.map((cam, idx) => (
                  <option key={cam.id || idx} value={cam.id}>
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
              MEDIAPIPE VISION FEED
              {fps > 0 ? ` • ${fps} FPS` : ''}
            </span>
          )}
        </div>
      </div>

      {/* Main Viewport */}
      <div className="camera-viewport-frame">
        {/* Video Element for Webcam Feed */}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`camera-video-element ${isMirror ? 'mirrored' : ''}`}
          style={{ display: isCameraActive ? 'block' : 'none', zIndex: 1 }}
        />

        {/* Overlay Canvas for Skeletal Landmarks */}
        <canvas
          ref={canvasRef}
          className={`camera-canvas-overlay ${isMirror ? 'mirrored' : ''}`}
          style={{
            display: (isCameraActive && showLandmarks) ? 'block' : 'none',
            zIndex: 10
          }}
        />

        {/* Positioning Guide Outline */}
        {isCameraActive && (
          <div className="camera-positioning-guide" style={{ zIndex: 12 }}>
            <div className="guide-box">
              <span className="guide-hint">Align upper body & hands within frame</span>
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
                <h4 className="standby-title font-display">Direct MediaPipe Studio Standby</h4>
                <p className="standby-desc">
                  Start your webcam to begin real-time MediaPipe skeletal tracking, hand landmark detection, and ISL translation.
                </p>
                <button onClick={onToggleCamera} className="primary-btn start-camera-btn">
                  <Camera size={16} /> Start MediaPipe Camera
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
        <span><strong style={{ color: '#ab47bc' }}>[H]</strong> Toggle Mesh</span>
      </div>
    </div>
  );
}
