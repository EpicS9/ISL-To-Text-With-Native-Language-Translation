import React, { useState, useEffect, useRef, useCallback } from 'react';
import Header from './components/Header';
import CameraStudio from './components/CameraStudio';
import RecognitionPanel from './components/RecognitionPanel';
import ControlToolbar from './components/ControlToolbar';
import SentenceBuilder from './components/SentenceBuilder';
import NLPSynthesizer from './components/NLPSynthesizer';
import MultilingualTranslation from './components/MultilingualTranslation';
import SettingsModal from './components/SettingsModal';
import GlossaryModal from './components/GlossaryModal';
import ImageDetector from './components/ImageDetector';
import { Camera, FileImage } from 'lucide-react';
import './App.css';

export default function App() {
  // Theme state
  const [theme, setTheme] = useState(() => localStorage.getItem('isl_theme') || 'light');

  // Backend & WebSocket state
  const [backendStatus, setBackendStatus] = useState('checking');
  const [modelsInfo, setModelsInfo] = useState(null);
  const [googleApiKey, setGoogleApiKey] = useState(() => localStorage.getItem('google_translate_api_key') || '');

  // Studio & Model States
  const [studioTab, setStudioTab] = useState('camera'); // 'camera' | 'photo'
  const [cameraSource, setCameraSource] = useState(() => localStorage.getItem('isl_camera_source') || 'native');
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCameraIndex, setSelectedCameraIndex] = useState(() => {
    const saved = localStorage.getItem('isl_camera_index');
    return saved !== null ? Number(saved) : 0;
  });
  const [streamKey, setStreamKey] = useState(Date.now());
  const [activeMode, setActiveMode] = useState('STATIC'); // 'STATIC' | 'DYNAMIC'
  const [threshold, setThreshold] = useState(0.80); // 80% confidence required to guarantee symbol accuracy
  const [debounceHold, setDebounceHold] = useState(0.80); // 0.80s deliberate hold time gap before committing
  const [commitProgress, setCommitProgress] = useState(0.0);
  const [showHudOverlay, setShowHudOverlay] = useState(true);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isMirror, setIsMirror] = useState(true);
  const [showLandmarks, setShowLandmarks] = useState(true);
  const [cameraError, setCameraError] = useState(null);

  // Live Inference Data
  const [prediction, setPrediction] = useState(null);
  const [latencyMs, setLatencyMs] = useState(0);
  const [fps, setFps] = useState(0);
  const [lastCommittedSign, setLastCommittedSign] = useState(null);

  // Sentence & Translation States
  const [glosses, setGlosses] = useState([]);
  const [synthesizedEnglish, setSynthesizedEnglish] = useState('');
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [targetLang, setTargetLang] = useState('hi'); // Default Hindi
  const [translatedResult, setTranslatedResult] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);

  // Modals
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isGlossaryOpen, setIsGlossaryOpen] = useState(false);

  // Refs
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const frameLoopRef = useRef(null);
  const lastUiUpdateRef = useRef(0);
  const autoStartedRef = useRef(false);

  // Mode change handler that sets optimal model thresholds matching V3 engine
  const handleSwitchMode = (newMode) => {
    setActiveMode(newMode);
    if (newMode === 'STATIC') {
      setThreshold(0.80); // 80% threshold for static alphabet & number poses
      setDebounceHold(0.80); // 0.80s hold time gap for deliberate confirmation
    } else {
      setThreshold(0.80); // 80% threshold for dynamic gestures
      setDebounceHold(0.60);
    }
  };

  // Update theme document attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('isl_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const [customBackendUrl, setCustomBackendUrl] = useState(() => {
    // If running directly on localhost or 127.0.0.1, default to local server directly
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      const saved = localStorage.getItem('isl_backend_url');
      if (saved && saved.startsWith('http') && !saved.includes('127.0.0.1') && !saved.includes('localhost')) {
        return saved;
      }
      return '';
    }
    return localStorage.getItem('isl_backend_url') || import.meta.env.VITE_BACKEND_URL || '';
  });

  // Helper for API endpoint URLs
  const getApiUrl = (endpoint) => {
    if (customBackendUrl) {
      const base = customBackendUrl.replace(/\/+$/, '');
      return `${base}${endpoint}`;
    }
    return endpoint;
  };

  // 1. Check Backend Health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(getApiUrl('/api/health'));
        if (res.ok) {
          const data = await res.json();
          setBackendStatus(data.status);
        } else {
          setBackendStatus('disconnected');
        }
      } catch (err) {
        setBackendStatus('disconnected');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, [customBackendUrl]);

  // 2. Fetch Models Info
  useEffect(() => {
    fetch(getApiUrl('/api/models/info'))
      .then(res => res.json())
      .then(data => setModelsInfo(data))
      .catch(err => console.error('Could not fetch models info:', err));
  }, [customBackendUrl]);

  // 3. Fetch Available Cameras (e.g. USB Webcams, Iriun Webcam)
  useEffect(() => {
    fetch(getApiUrl('/api/camera/devices'))
      .then(res => res.json())
      .then(data => {
        if (data.cameras && data.cameras.length > 0) {
          setAvailableCameras(data.cameras);
          const saved = localStorage.getItem('isl_camera_index');
          if (saved !== null) {
            const numSaved = Number(saved);
            const exists = data.cameras.some(c => c.index === numSaved);
            if (exists) {
              setSelectedCameraIndex(numSaved);
              return;
            }
          }
          // Prioritize physical hardware webcam over virtual/Iriun webcams
          const physicalCam = data.cameras.find(c => !c.is_iriun);
          const defaultIdx = physicalCam ? physicalCam.index : data.cameras[0].index;
          setSelectedCameraIndex(defaultIdx);
          localStorage.setItem('isl_camera_index', String(defaultIdx));
        }
      })
      .catch(err => console.error('Could not fetch camera devices:', err));
  }, [customBackendUrl]);

  // 4. Global Keyboard Shortcuts matching realtime_isl_translator_v3.py BAT file exactly:
  // [TAB] or [M]: Toggle Mode (STATIC <-> DYNAMIC)
  // [1]: Switch directly to STATIC Mode
  // [2]: Switch directly to DYNAMIC Mode
  // [SPACE]: Instant Add Word to sentence
  // [C]: Clear sentence
  // [BKSP]: Backspace / remove last word
  // [H]: Toggle skeletal mesh overlay
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.key === 'Tab' || e.key.toLowerCase() === 'm') {
        e.preventDefault();
        const nextMode = activeMode === 'STATIC' ? 'DYNAMIC' : 'STATIC';
        handleSwitchMode(nextMode);
      } else if (e.key === '1') {
        e.preventDefault();
        handleSwitchMode('STATIC');
      } else if (e.key === '2') {
        e.preventDefault();
        handleSwitchMode('DYNAMIC');
      } else if (e.code === 'Space') {
        e.preventDefault();
        if (prediction?.sign && prediction.sign !== '...' && prediction.sign !== 'Buffering...') {
          handleCommitSign(prediction.sign);
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'space', word: prediction.sign }));
          }
        }
      } else if (e.key.toLowerCase() === 'c') {
        e.preventDefault();
        handleClearAll();
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'clear' }));
        }
      } else if (e.key === 'Backspace') {
        e.preventDefault();
        handleUndoLast();
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'backspace' }));
        }
      } else if (e.key.toLowerCase() === 'h') {
        e.preventDefault();
        toggleLandmarks();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeMode, prediction]);

  // 5. WebSocket Setup
  useEffect(() => {
    let wsUrl = '';
    if (customBackendUrl) {
      const cleanUrl = customBackendUrl.replace(/\/+$/, '');
      const wsProto = cleanUrl.startsWith('https:') ? 'wss:' : 'ws:';
      const host = cleanUrl.replace(/^https?:\/\//, '');
      wsUrl = `${wsProto}//${host}/ws/inference`;
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${protocol}//${window.location.host}/ws/inference`;
    }

    const connectWebSocket = () => {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        // Send initial configuration
        ws.send(jsonConfig(activeMode, threshold, debounceHold, showHudOverlay));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'pong') return;

          // Handle automatic debounce commit from backend immediately
          if (data.committed_sign) {
            handleCommitSign(data.committed_sign);
          }

          if (data.commit_progress !== undefined) {
            setCommitProgress(data.commit_progress);
          }

          if (data.type === 'sentence_updated' && data.sentence_words) {
            setGlosses(data.sentence_words);
          }

          // Smooth real-time 30+ FPS UI update
          const now = performance.now();
          if (now - lastUiUpdateRef.current >= 30) {
            lastUiUpdateRef.current = now;
            setPrediction(data);
            if (data.latency_ms !== undefined) setLatencyMs(data.latency_ms);
            if (data.fps !== undefined) setFps(data.fps);
          }

          // Draw skeletal landmark overlay on overlay canvas (browser fallback mode)
          if (showLandmarks && data.landmarks && canvasRef.current && videoRef.current) {
            drawLandmarks(data.landmarks, canvasRef.current);
          }
        } catch (e) {
          console.error('Error parsing WS message:', e);
        }
      };

      ws.onclose = () => {
        setTimeout(connectWebSocket, 2000);
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  // Sync mode & config to WebSocket and Native Camera whenever changed
  useEffect(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(jsonConfig(activeMode, threshold, debounceHold, showHudOverlay));
    }
    if (cameraSource === 'native') {
      fetch(getApiUrl('/api/camera/config'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: activeMode,
          threshold: threshold,
          debounce_hold: debounceHold,
          draw_hud_overlay: showHudOverlay
        })
      }).catch(() => {});
    }
  }, [activeMode, threshold, debounceHold, showHudOverlay, cameraSource]);

  const jsonConfig = (m, th, dh, hud) => JSON.stringify({
    type: 'config',
    mode: m,
    threshold: th,
    debounce_hold: dh,
    draw_hud_overlay: hud
  });

  // 5. Authentic Google MediaPipe Landmark Styling on Canvas (Browser Fallback Mode)
  const drawLandmarks = (landmarks, canvas) => {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const drawHand = (points) => {
      if (!points || points.length < 21) return;

      const FINGER_COLORS = {
        thumb: '#FFA726',    // Warm Amber
        index: '#26C6DA',    // Cyan / Teal
        middle: '#42A5F5',   // Blue
        ring: '#AB47BC',     // Purple
        pinky: '#EC407A',    // Vibrant Pink
        palm: '#ECEFF1'      // Silver White
      };

      const segments = [
        { indices: [[0,1],[1,2],[2,3],[3,4]], color: FINGER_COLORS.thumb },
        { indices: [[0,5],[5,6],[6,7],[7,8]], color: FINGER_COLORS.index },
        { indices: [[5,9],[9,10],[10,11],[11,12]], color: FINGER_COLORS.middle },
        { indices: [[9,13],[13,14],[14,15],[15,16]], color: FINGER_COLORS.ring },
        { indices: [[13,17],[17,18],[18,19],[19,20]], color: FINGER_COLORS.pinky },
        { indices: [[0,17]], color: FINGER_COLORS.palm }
      ];

      // Draw bone connections
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      segments.forEach(({ indices, color }) => {
        ctx.strokeStyle = color;
        indices.forEach(([i, j]) => {
          if (points[i] && points[j]) {
            ctx.beginPath();
            ctx.moveTo(points[i][0] * canvas.width, points[i][1] * canvas.height);
            ctx.lineTo(points[j][0] * canvas.width, points[j][1] * canvas.height);
            ctx.stroke();
          }
        });
      });

      // Draw official MediaPipe joint knuckles (concentric circles with white center)
      points.forEach(([x, y]) => {
        const px = x * canvas.width;
        const py = y * canvas.height;
        ctx.fillStyle = '#FF3D00';
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(px, py, 2, 0, 2 * Math.PI);
        ctx.fill();
      });
    };

    const drawPose = (points) => {
      if (!points || points.length === 0) return;
      const POSE_LINES = [
        [11, 12], [11, 13], [13, 15], [12, 14], [14, 16]
      ];
      ctx.strokeStyle = '#00E676';
      ctx.lineWidth = 3.5;
      ctx.lineCap = 'round';
      POSE_LINES.forEach(([i, j]) => {
        if (points[i] && points[j]) {
          ctx.beginPath();
          ctx.moveTo(points[i][0] * canvas.width, points[i][1] * canvas.height);
          ctx.lineTo(points[j][0] * canvas.width, points[j][1] * canvas.height);
          ctx.stroke();
        }
      });
      [11, 12, 13, 14, 15, 16].forEach(idx => {
        if (points[idx]) {
          const px = points[idx][0] * canvas.width;
          const py = points[idx][1] * canvas.height;
          ctx.fillStyle = '#FFEA00';
          ctx.beginPath();
          ctx.arc(px, py, 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = '#FFFFFF';
          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, 2 * Math.PI);
          ctx.fill();
        }
      });
    };

    drawHand(landmarks.left_hand);
    drawHand(landmarks.right_hand);
    drawPose(landmarks.pose);
  };

  // 6. Camera Lifecycle & Source Management
  const handleCameraSourceChange = async (newSource) => {
    if (newSource === cameraSource) return;
    if (isCameraActive) {
      await stopActiveCamera();
    }
    setCameraSource(newSource);
    localStorage.setItem('isl_camera_source', newSource);
  };

  const handleSelectCameraIndex = async (index) => {
    setSelectedCameraIndex(index);
    localStorage.setItem('isl_camera_index', String(index));
    if (cameraSource === 'native' && isCameraActive) {
      try {
        await fetch(getApiUrl('/api/camera/config'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ camera_index: index })
        });
        setStreamKey(Date.now());
      } catch (e) {
        console.error('Error switching camera index:', e);
      }
    }
  };

  const toggleMirror = () => {
    setIsMirror(prev => {
      const next = !prev;
      if (cameraSource === 'native') {
        fetch(getApiUrl('/api/camera/config'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mirror: next })
        }).catch(() => {});
      }
      return next;
    });
  };

  const toggleLandmarks = () => {
    setShowLandmarks(prev => {
      const next = !prev;
      if (cameraSource === 'native') {
        fetch(getApiUrl('/api/camera/config'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ draw_landmarks: next })
        }).catch(() => {});
      }
      return next;
    });
  };

  const toggleHudOverlay = () => {
    setShowHudOverlay(prev => {
      const next = !prev;
      if (cameraSource === 'native') {
        fetch(getApiUrl('/api/camera/config'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ draw_hud_overlay: next })
        }).catch(() => {});
      }
      return next;
    });
  };

  const stopActiveCamera = async () => {
    if (frameLoopRef.current) cancelAnimationFrame(frameLoopRef.current);
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
    if (cameraSource === 'native') {
      try {
        await fetch(getApiUrl('/api/camera/stop'), { method: 'POST' });
      } catch (e) {
        console.error('Error stopping native camera:', e);
      }
    }
    setIsCameraActive(false);
    setPrediction(null);
  };

  const toggleCamera = async () => {
    if (isCameraActive) {
      await stopActiveCamera();
    } else {
      setCameraError(null);
      if (cameraSource === 'native') {
        // Direct Native Camera Engine (OpenCV + MediaPipe Holistic in Python)
        try {
          const res = await fetch(getApiUrl('/api/camera/start'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              camera_index: selectedCameraIndex,
              mirror: isMirror,
              draw_landmarks: showLandmarks,
              draw_hud_overlay: showHudOverlay,
              mode: activeMode,
              threshold: threshold,
              debounce_hold: debounceHold
            })
          });
          const data = await res.json();
          if (data.status === 'started' || data.is_running) {
            setIsCameraActive(true);
            setStreamKey(Date.now());
          } else {
            setCameraError('Unable to open native webcam. Please verify your camera device is plugged in and not in use by another program.');
            setIsCameraActive(false);
          }
        } catch (err) {
          console.error('Failed to start native camera:', err);
          setCameraError('Could not reach backend camera API: ' + err.message);
          setIsCameraActive(false);
        }
      } else {
        // Browser WebRTC camera
        try {
          const stream = await navigator.mediaDevices.getUserMedia({
            video: {
              width: { ideal: 1280 },
              height: { ideal: 720 },
              facingMode: 'user'
            },
            audio: false
          });

          mediaStreamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            await videoRef.current.play();
          }
          setIsCameraActive(true);

          if (canvasRef.current && videoRef.current) {
            canvasRef.current.width = videoRef.current.videoWidth || 1280;
            canvasRef.current.height = videoRef.current.videoHeight || 720;
          }

          startFrameCaptureLoop();
        } catch (err) {
          console.error('Webcam access error:', err);
          setCameraError(err.message || 'Unable to access webcam. Check browser permissions.');
          setIsCameraActive(false);
        }
      }
    }
  };

  // Frame capture loop sending frames to WebSocket (Browser Mode Fallback)
  const startFrameCaptureLoop = () => {
    const captureCanvas = document.createElement('canvas');
    captureCanvas.width = 640; // 640x480 for ultra-fast 30 FPS canvas rendering & MediaPipe alignment
    captureCanvas.height = 480;
    const captureCtx = captureCanvas.getContext('2d', { willReadFrequently: true });

    let lastSent = 0;
    const sendInterval = 33; // ~30 FPS

    const loop = (timestamp) => {
      if (!mediaStreamRef.current || !videoRef.current) return;

      if (timestamp - lastSent > sendInterval) {
        lastSent = timestamp;
        if (videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
          captureCtx.drawImage(videoRef.current, 0, 0, captureCanvas.width, captureCanvas.height);
          const base64Data = captureCanvas.toDataURL('image/jpeg', 0.72);

          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
              type: 'frame',
              image: base64Data,
              mode: activeMode,
              threshold: threshold,
              debounce_hold: debounceHold
            }));
          }
        }
      }
      frameLoopRef.current = requestAnimationFrame(loop);
    };

    frameLoopRef.current = requestAnimationFrame(loop);
  };

  // 7. Sentence Builder Actions
  const handleCommitSign = (sign) => {
    setLastCommittedSign(sign);
    setGlosses(prev => [...prev, sign]);
  };

  const handleAddManualGloss = (token) => {
    setGlosses(prev => [...prev, token]);
  };

  const handleRemoveGloss = (index) => {
    setGlosses(prev => prev.filter((_, i) => i !== index));
  };

  const handleUndoLast = () => {
    setGlosses(prev => prev.slice(0, -1));
  };

  const handleClearAll = () => {
    setGlosses([]);
    setSynthesizedEnglish('');
    setTranslatedResult(null);
  };

  const handleInsertSpace = () => {
    setGlosses(prev => [...prev, ' ']);
  };

  // 8. NLP Synthesis
  const triggerNLPSynthesis = useCallback(async () => {
    if (glosses.length === 0) return;
    setIsSynthesizing(true);
    try {
      const res = await fetch(getApiUrl('/api/nlp/synthesize'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ glosses })
      });
      if (res.ok) {
        const data = await res.json();
        setSynthesizedEnglish(data.synthesized_english);
      }
    } catch (err) {
      console.error('NLP Synthesis Error:', err);
    } finally {
      setIsSynthesizing(false);
    }
  }, [glosses, customBackendUrl]);

  // Auto-synthesize English when glosses change (with debounce)
  useEffect(() => {
    if (glosses.length > 0) {
      const timer = setTimeout(triggerNLPSynthesis, 600);
      return () => clearTimeout(timer);
    } else {
      setSynthesizedEnglish('');
    }
  }, [glosses, triggerNLPSynthesis]);

  // 9. Multilingual Translation
  const triggerTranslation = useCallback(async () => {
    if (!synthesizedEnglish.trim()) {
      setTranslatedResult(null);
      return;
    }
    setIsTranslating(true);
    try {
      const res = await fetch(getApiUrl('/api/translate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: synthesizedEnglish,
          target_lang: targetLang,
          api_key: googleApiKey || undefined
        })
      });
      if (res.ok) {
        const data = await res.json();
        setTranslatedResult(data);
      }
    } catch (err) {
      console.error('Translation Error:', err);
    } finally {
      setIsTranslating(false);
    }
  }, [synthesizedEnglish, targetLang, googleApiKey, customBackendUrl]);

  // Auto-translate when synthesized English or target language changes
  useEffect(() => {
    if (synthesizedEnglish.trim()) {
      const timer = setTimeout(triggerTranslation, 400);
      return () => clearTimeout(timer);
    } else {
      setTranslatedResult(null);
    }
  }, [synthesizedEnglish, targetLang, triggerTranslation]);

  // Save API Key
  const handleSaveApiKey = (key) => {
    setGoogleApiKey(key);
    if (key) {
      localStorage.setItem('google_translate_api_key', key);
    } else {
      localStorage.removeItem('google_translate_api_key');
    }
  };

  // Save Custom Backend URL (for Vercel deployment)
  const handleSaveBackendUrl = (url) => {
    setCustomBackendUrl(url);
    if (url) {
      localStorage.setItem('isl_backend_url', url);
    } else {
      localStorage.removeItem('isl_backend_url');
    }
  };

  return (
    <div className="studio-app">
      {/* 1. Header & Navigation */}
      <Header
        backendStatus={backendStatus}
        activeMode={activeMode}
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenGlossary={() => setIsGlossaryOpen(true)}
      />

      <main className="studio-main-content">
        <div className="studio-page-header">
          <div>
            <h1 className="page-heading font-display">Accessible Real-Time Studio</h1>
            <p className="page-subheading">
              Translating Indian Sign Language into natural English and regional native languages.
            </p>
          </div>
        </div>

        {/* Studio View Selector: Live Camera Studio vs Static Photo Symbol Detector */}
        <div className="studio-mode-switcher">
          <button
            type="button"
            className={`studio-tab-btn ${studioTab === 'camera' ? 'active' : ''}`}
            onClick={() => setStudioTab('camera')}
          >
            <Camera size={18} />
            <span>Live Camera Studio</span>
            <span className="tab-pill">Real-Time</span>
          </button>
          <button
            type="button"
            className={`studio-tab-btn ${studioTab === 'photo' ? 'active' : ''}`}
            onClick={() => setStudioTab('photo')}
          >
            <FileImage size={18} />
            <span>Static Photo Detector</span>
            <span className="tab-pill new">Instant</span>
          </button>
        </div>

        {studioTab === 'camera' ? (
          <>
            {/* 2. Main Workspace: Live Studio (Two Columns) */}
            <div className="workspace-two-column-layout">
              {/* Left Column: Camera Studio */}
              <CameraStudio
                videoRef={videoRef}
                canvasRef={canvasRef}
                isCameraActive={isCameraActive}
                isMirror={isMirror}
                showLandmarks={showLandmarks}
                showHudOverlay={showHudOverlay}
                cameraError={cameraError}
                fps={fps}
                cameraSource={cameraSource}
                onChangeCameraSource={handleCameraSourceChange}
                nativeStreamUrl={getApiUrl(`/api/camera/stream?t=${streamKey}`)}
                availableCameras={availableCameras}
                selectedCameraIndex={selectedCameraIndex}
                onSelectCameraIndex={handleSelectCameraIndex}
                onToggleCamera={toggleCamera}
                onToggleMirror={toggleMirror}
                onToggleLandmarks={toggleLandmarks}
                onToggleHudOverlay={toggleHudOverlay}
              />

              {/* Right Column: Recognition Panel */}
              <RecognitionPanel
                activeMode={activeMode}
                prediction={prediction}
                latencyMs={latencyMs}
                fps={fps}
                threshold={threshold}
                commitProgress={commitProgress}
                isCameraActive={isCameraActive}
                committedSign={lastCommittedSign}
              />
            </div>

            {/* 3. Mode and Recognition Controls Toolbar */}
            <ControlToolbar
              activeMode={activeMode}
              threshold={threshold}
              debounceHold={debounceHold}
              onChangeMode={handleSwitchMode}
              onChangeThreshold={(th) => setThreshold(th)}
              onChangeDebounceHold={(dh) => setDebounceHold(dh)}
            />
          </>
        ) : (
          /* Static Photo Symbol Detector Section */
          <ImageDetector
            onAddSign={handleCommitSign}
            getApiUrl={getApiUrl}
            threshold={threshold}
          />
        )}

        {/* 4. Sentence Builder (Gloss Timeline) */}
        <SentenceBuilder
          glosses={glosses}
          onAddGloss={handleAddManualGloss}
          onRemoveGloss={handleRemoveGloss}
          onUndoLast={handleUndoLast}
          onClearAll={handleClearAll}
          onInsertSpace={handleInsertSpace}
        />

        {/* 5. English NLP Synthesizer */}
        <NLPSynthesizer
          glosses={glosses}
          synthesizedEnglish={synthesizedEnglish}
          isSynthesizing={isSynthesizing}
          onTriggerSynthesize={triggerNLPSynthesis}
          onUpdateEnglish={(txt) => setSynthesizedEnglish(txt)}
        />

        {/* 6. Regional Multilingual Translation & Speech Output */}
        <MultilingualTranslation
          synthesizedEnglish={synthesizedEnglish}
          targetLang={targetLang}
          translatedResult={translatedResult}
          isTranslating={isTranslating}
          hasGoogleKey={Boolean(googleApiKey)}
          onSelectLanguage={(code) => setTargetLang(code)}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />
      </main>

      {/* Settings & Diagnostics Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        googleApiKey={googleApiKey}
        onSaveApiKey={handleSaveApiKey}
        customBackendUrl={customBackendUrl}
        onSaveBackendUrl={handleSaveBackendUrl}
        modelsInfo={modelsInfo}
        backendStatus={backendStatus}
        threshold={threshold}
        onChangeThreshold={(val) => setThreshold(val)}
        debounceHold={debounceHold}
        onChangeDebounceHold={(val) => setDebounceHold(val)}
      />

      {/* Sign Glossary Modal */}
      <GlossaryModal
        isOpen={isGlossaryOpen}
        onClose={() => setIsGlossaryOpen(false)}
        activeMode={activeMode}
        onSelectSign={(sign) => {
          handleCommitSign(sign);
          setIsGlossaryOpen(false);
        }}
      />
    </div>
  );
}
