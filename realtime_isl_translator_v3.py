"""
=============================================================================
ISL to Text Translation — Real-Time Engine (V3 - Decoupled Dual Model with Mode Toggle)
=============================================================================
Architecture:
  • Two Independent, High-Accuracy Models:
    1. Static Model  : 35 Classes (0-9, A-Z, Good) — Residual Dense MLP (98.7% acc)
    2. Dynamic Model : 11 Classes (Hello, ThankYou, Claps, Congrats, H, J, No,
                                  Please, Sorry, Welcome, Yes) — BiLSTM + Attention (99.2% acc)
  • Explicit User-Controlled Mode Toggle:
    - Press [TAB] or [M] to switch between STATIC and DYNAMIC modes instantly.
    - When in STATIC mode, the dynamic model is completely muted — zero false 'H' or 'J'!
    - When in DYNAMIC mode, the static model is muted — focuses purely on movement gestures!
  • High-Speed Compiled Inference:
    - @tf.function graph compilation runs in 2.5ms (30+ FPS smooth).
=============================================================================
"""

import os
import sys
import time
import json
import zipfile
import tempfile
import argparse
from collections import deque

import cv2
import numpy as np
import mediapipe as mp

try:
    if not hasattr(mp, "solutions"):
        import mediapipe.python.solutions as mp_solutions
        mp.solutions = mp_solutions
except Exception:
    pass

# Silence TF / Keras info logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import keras
from keras import layers
import tensorflow as tf

# =====================================================================
# 1. CONSTANTS & FEATURE CONFIGURATION
# =====================================================================
SEQUENCE_LENGTH = 30
FEATURE_DIM = 534

# Slicing constants matching the dataset
POSE_LEN = 33 * 4     # 132
LH_LEN = 21 * 3       # 63
RH_LEN = 21 * 3       # 63
FACE_POINTS = 92
FACE_LEN = FACE_POINTS * 3  # 276

POSE_START = 0
LH_START = POSE_LEN
RH_START = POSE_LEN + LH_LEN
FACE_START = POSE_LEN + LH_LEN + RH_LEN

# MediaPipe face mesh connections
mp_face_mesh = mp.solutions.face_mesh
_FACE_REGIONS_OF_INTEREST = [
    mp_face_mesh.FACEMESH_LIPS,
    mp_face_mesh.FACEMESH_LEFT_EYE,
    mp_face_mesh.FACEMESH_RIGHT_EYE,
    mp_face_mesh.FACEMESH_LEFT_EYEBROW,
    mp_face_mesh.FACEMESH_RIGHT_EYEBROW,
]
FACE_LANDMARK_INDICES = sorted({
    idx for connection_set in _FACE_REGIONS_OF_INTEREST
    for pair in connection_set
    for idx in pair
})

# Thresholds & Debounce
STATIC_CONF_THRESHOLD = 0.80         # 80% confidence required to ensure symbol accuracy
DYNAMIC_CONF_THRESHOLD = 0.80
STATIC_HOLD_SECONDS = 0.80          # Hold static sign steady for 0.80s to confirm deliberate pose
COMMIT_COOLDOWN_SECONDS = 0.80      # Deliberate transition time gap after printing symbol before next symbol
DYNAMIC_COOLDOWN_SECONDS = 1.2      # Prevent repeating dynamic word too quickly


# =====================================================================
# 2. KEYPOINT EXTRACTION & SHOULDER NORMALIZATION
# =====================================================================
def extract_keypoints(results):
    """Extracts raw keypoints from MediaPipe holistic results."""
    if results.pose_landmarks:
        pose = np.array([[res.x, res.y, res.z, res.visibility]
                         for res in results.pose_landmarks.landmark], dtype=np.float32).flatten()
    else:
        pose = np.zeros(POSE_LEN, dtype=np.float32)

    if results.left_hand_landmarks:
        lh = np.array([[res.x, res.y, res.z]
                       for res in results.left_hand_landmarks.landmark], dtype=np.float32).flatten()
    else:
        lh = np.zeros(LH_LEN, dtype=np.float32)

    if results.right_hand_landmarks:
        rh = np.array([[res.x, res.y, res.z]
                       for res in results.right_hand_landmarks.landmark], dtype=np.float32).flatten()
    else:
        rh = np.zeros(RH_LEN, dtype=np.float32)

    if results.face_landmarks:
        all_face_lm = results.face_landmarks.landmark
        face = np.array([[all_face_lm[i].x, all_face_lm[i].y, all_face_lm[i].z]
                         for i in FACE_LANDMARK_INDICES], dtype=np.float32).flatten()
    else:
        face = np.zeros(FACE_LEN, dtype=np.float32)

    return np.concatenate([pose, lh, rh, face])


def get_shoulder_origin_and_scale(vec):
    """Calculates mid-shoulder origin and shoulder-span scale."""
    left_shoulder = vec[11 * 4: 11 * 4 + 3]
    right_shoulder = vec[12 * 4: 12 * 4 + 3]
    origin = (left_shoulder + right_shoulder) / 2.0
    scale = float(np.linalg.norm(right_shoulder - left_shoulder))
    scale = scale if scale > 1e-6 else 1.0
    return origin, scale


def normalize_vector(vec, frame_width, frame_height):
    """Exact dataset-aligned scale and aspect ratio normalization."""
    vec = vec.copy()
    aspect = float(frame_width) / float(frame_height)

    def rescale_x(start, count, stride):
        for i in range(count):
            base = start + i * stride
            vec[base] *= aspect

    rescale_x(POSE_START, 33, 4)
    rescale_x(LH_START, 21, 3)
    rescale_x(RH_START, 21, 3)
    rescale_x(FACE_START, FACE_POINTS, 3)

    origin, scale = get_shoulder_origin_and_scale(vec)

    def normalize_block(start, count, stride):
        for i in range(count):
            base = start + i * stride
            vec[base:base + 3] = (vec[base:base + 3] - origin) / scale

    normalize_block(POSE_START, 33, 4)
    normalize_block(LH_START, 21, 3)
    normalize_block(RH_START, 21, 3)
    normalize_block(FACE_START, FACE_POINTS, 3)

    return vec, origin, scale


# =====================================================================
# 3. HIGH-SPEED DECOUPLED DUAL MODEL ENGINE
# =====================================================================
class DecoupledISLEngineV3:
    def __init__(self, models_dir="models_v3"):
        if not os.path.isdir(models_dir):
            models_dir = "models"
        self.models_dir = models_dir

        print(f"[ENGINE V3] Initializing dual models from {self.models_dir}...")
        self.static_classes = np.load(os.path.join(self.models_dir, "static_label_classes.npy"))
        self.dynamic_classes = np.load(os.path.join(self.models_dir, "dynamic_label_classes.npy"))

        print(f"  • Static Classes  ({len(self.static_classes)}): {self.static_classes[:10]}...{self.static_classes[-5:]}")
        print(f"  • Dynamic Classes ({len(self.dynamic_classes)}): {self.dynamic_classes}")

        # 1. Load and compile Static Branch (Residual Dense MLP)
        raw_static = self._load_static_model()
        self._compiled_static = tf.function(lambda x: raw_static(x, training=False))

        # 2. Load and compile Dynamic Branch (BiLSTM + Bahdanau Attention)
        raw_dynamic = self._load_dynamic_model()
        self._compiled_dynamic = tf.function(lambda x: raw_dynamic(x, training=False))

        # Graph warm-up
        self._compiled_static(tf.zeros((1, FEATURE_DIM), dtype=tf.float32))
        self._compiled_dynamic(tf.zeros((1, SEQUENCE_LENGTH, FEATURE_DIM), dtype=tf.float32))
        print(f"[ENGINE V3] Both models compiled and warmed up! Ready for inference.")

    def _load_static_model(self):
        keras_path = os.path.join(self.models_dir, "isl_static_model_final.keras")
        with zipfile.ZipFile(keras_path) as z:
            cfg = json.loads(z.read("config.json"))
            w_bytes = z.read("model.weights.h5")

        def clean_dict(d):
            if isinstance(d, dict):
                d.pop("quantization_config", None)
                for v in d.values():
                    clean_dict(v)
            elif isinstance(d, list):
                for item in d:
                    clean_dict(item)

        clean_dict(cfg)
        model = keras.models.model_from_json(json.dumps(cfg))

        with tempfile.NamedTemporaryFile(suffix=".weights.h5", delete=False) as tmp:
            tmp.write(w_bytes)
            tmp_path = tmp.name
        try:
            model.load_weights(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return model

    def _load_dynamic_model(self):
        keras_path = os.path.join(self.models_dir, "isl_dynamic_model_final.keras")
        inp = keras.Input(shape=(SEQUENCE_LENGTH, FEATURE_DIM), name="sequence")
        x = layers.Conv1D(64, kernel_size=3, padding="same", activation="relu", name="cnn_frontend")(inp)
        x = layers.Bidirectional(layers.LSTM(192, return_sequences=True, name="lstm_0"), name="bilstm_0")(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, name="lstm_1"), name="bilstm_1")(x)
        score = layers.Dense(1, activation="tanh", name="attn_score")(x)
        weights = layers.Softmax(axis=1, name="attn_weights")(score)
        x = layers.Multiply()([x, weights])
        x = layers.Lambda(lambda t: tf.reduce_sum(t, axis=1), name="attn_context")(x)
        x = layers.Dense(64, name="dense_1")(x)
        x = layers.Activation("gelu", name="activation_1")(x)
        x = layers.Dropout(0.5, name="dropout_1")(x)
        out = layers.Dense(len(self.dynamic_classes), activation="softmax", name="predictions")(x)
        model = keras.Model(inp, out, name="Dynamic_BiLSTM_Attention")

        with zipfile.ZipFile(keras_path) as z:
            w_bytes = z.read("model.weights.h5")
        with tempfile.NamedTemporaryFile(suffix=".weights.h5", delete=False) as tmp:
            tmp.write(w_bytes)
            tmp_path = tmp.name
        try:
            model.load_weights(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return model

    def predict_static(self, vec):
        """Pure Static Prediction (2.2ms forward pass)."""
        tensor_in = tf.convert_to_tensor(vec.reshape(1, FEATURE_DIM), dtype=tf.float32)
        probs = self._compiled_static(tensor_in).numpy()[0]
        top_idx = int(np.argmax(probs))
        label = str(self.static_classes[top_idx])
        conf = float(probs[top_idx])
        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [(self.static_classes[i], float(probs[i])) for i in top_indices]
        return label, conf, top3

    def predict_dynamic(self, seq_30):
        """Pure Dynamic Prediction (4.2ms forward pass)."""
        tensor_in = tf.convert_to_tensor(seq_30.reshape(1, SEQUENCE_LENGTH, FEATURE_DIM), dtype=tf.float32)
        probs = self._compiled_dynamic(tensor_in).numpy()[0]
        top_idx = int(np.argmax(probs))
        label = str(self.dynamic_classes[top_idx])
        conf = float(probs[top_idx])
        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [(self.dynamic_classes[i], float(probs[i])) for i in top_indices]
        return label, conf, top3


# =====================================================================
# 4. HUD VISUALIZATION
# =====================================================================
def draw_hud(frame, current_mode, label, confidence, sentence, top3, fps,
             hands_detected, commit_progress):
    """Draws a clean, modern HUD overlay with prominent mode switcher."""
    h, w = frame.shape[:2]

    overlay = frame.copy()
    top_bar_h = 90 if w < 900 else 120
    bottom_bar_h = 55 if w < 900 else 75
    panel_w = 210 if w < 900 else 280

    # Top bar
    cv2.rectangle(overlay, (0, 0), (w, top_bar_h), (15, 18, 22), -1)
    # Bottom sentence bar
    cv2.rectangle(overlay, (0, h - bottom_bar_h), (w, h), (15, 18, 22), -1)
    # Side candidates bar
    cv2.rectangle(overlay, (w - panel_w, top_bar_h + 10), (w - 10, min(h - bottom_bar_h - 10, top_bar_h + 220)), (22, 27, 34), -1)
    cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

    cv2.rectangle(frame, (w - panel_w, top_bar_h + 10), (w - 10, min(h - bottom_bar_h - 10, top_bar_h + 220)), (60, 70, 85), 1)

    # --- TOP BAR: MODE BANNER ---
    if current_mode == "STATIC":
        mode_color = (60, 215, 120)  # Bright emerald green
        mode_title = "STATIC (A-Z, 0-9)" if w < 900 else "MODE: STATIC SIGNS (A-Z, 0-9)"
    else:
        mode_color = (0, 160, 255)   # Vibrant orange
        mode_title = "DYNAMIC (Words)" if w < 900 else "MODE: DYNAMIC GESTURES (Words)"

    badge_w = 200 if w < 900 else 340
    # Mode Badge
    cv2.rectangle(frame, (15, 12), (15 + badge_w, 36), mode_color, -1, cv2.LINE_AA)
    cv2.putText(frame, mode_title, (22, 29), cv2.FONT_HERSHEY_DUPLEX, 0.44 if w < 900 else 0.48, (0, 0, 0), 1, cv2.LINE_AA)

    # Switch Hint
    if w >= 900:
        cv2.putText(frame, "[Press TAB / M to Switch Mode]", (375, 29),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 230, 255), 1, cv2.LINE_AA)

    # Hands tracked & FPS
    hand_color = (0, 255, 128) if hands_detected else (0, 69, 255)
    stat_x = w - 170 if w < 900 else w - 195
    cv2.circle(frame, (stat_x, 24), 5, hand_color, -1, cv2.LINE_AA)
    cv2.putText(frame, "TRACKED" if (hands_detected and w < 900) else ("HANDS DETECTED" if hands_detected else "NO HANDS"),
                (stat_x + 12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:.0f}", (w - 55, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (160, 240, 160), 1, cv2.LINE_AA)

    # --- PREDICTED SIGN DISPLAY ---
    if hands_detected and confidence >= 0.65:
        text_color = (255, 255, 255)
        display_label = label
    elif hands_detected:
        text_color = (130, 140, 150)
        display_label = "Detecting..."
    else:
        text_color = (100, 110, 120)
        display_label = "Bring hands into view"

    label_font_scale = 1.0 if w < 900 else 1.45
    label_y = 74 if w < 900 else 100
    cv2.putText(frame, display_label, (15, label_y), cv2.FONT_HERSHEY_DUPLEX, label_font_scale, text_color, 2, cv2.LINE_AA)

    # Confidence Bar
    bar_x = int(w * 0.32) if w < 900 else 360
    bar_y = 56 if w < 900 else 78
    bar_w = int(w * 0.22) if w < 900 else 180
    bar_h = 14 if w < 900 else 16
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    fill_w = int(bar_w * min(1.0, max(0.0, confidence if hands_detected else 0.0)))
    fill_color = (0, 220, 110) if confidence >= 0.75 else (0, 180, 240)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)
    cv2.putText(frame, f"{confidence * 100:.0f}%", (bar_x + bar_w + 6, bar_y + 11),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)

    # Auto-commit progress bar (in static mode)
    if current_mode == "STATIC":
        prog_x = int(w * 0.65) if w < 900 else 640
        prog_y = bar_y
        prog_w = int(w * 0.18) if w < 900 else 130
        prog_h = bar_h
        cv2.rectangle(frame, (prog_x, prog_y), (prog_x + prog_w, prog_y + prog_h), (40, 40, 40), -1)
        fill_p = int(prog_w * min(1.0, max(0.0, commit_progress)))
        cv2.rectangle(frame, (prog_x, prog_y), (prog_x + fill_p, prog_y + prog_h), (0, 200, 255), -1)
        cv2.rectangle(frame, (prog_x, prog_y), (prog_x + prog_w, prog_y + prog_h), (120, 120, 120), 1)
        cv2.putText(frame, "Hold", (prog_x + prog_w + 6, prog_y + 11),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (190, 190, 190), 1, cv2.LINE_AA)

    # --- SIDE PANEL: TOP CANDIDATES & CONTROLS ---
    panel_left = w - panel_w + 12
    candidates_title = f"{current_mode} DETECTIONS"
    cv2.putText(frame, candidates_title, (panel_left, top_bar_h + 30), cv2.FONT_HERSHEY_DUPLEX, 0.38, (0, 210, 255), 1, cv2.LINE_AA)
    for idx, (c_name, c_prob) in enumerate(top3[:3]):
        item_y = top_bar_h + 56 + idx * 24
        cv2.putText(frame, f"{idx+1}. {c_name[:10]}", (panel_left, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(frame, f"{c_prob * 100:.0f}%", (w - 48, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (160, 200, 160), 1, cv2.LINE_AA)

    shortcut_y = top_bar_h + 140
    cv2.putText(frame, "[TAB] Mode  [SPACE] Add", (panel_left, shortcut_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 230, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "[C] Clear  [BKSP] Del", (panel_left, shortcut_y + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (170, 170, 170), 1, cv2.LINE_AA)

    # --- BOTTOM BAR: SENTENCE TRANSLATION RIBBON ---
    bottom_y = h - 22 if w < 900 else h - 45
    cv2.putText(frame, "TRANSLATION:", (15, bottom_y), cv2.FONT_HERSHEY_DUPLEX, 0.45 if w < 900 else 0.55, (0, 220, 255), 1, cv2.LINE_AA)
    sentence_display = sentence if sentence else "(Perform signs to build sentence...)"
    sentence_color = (255, 255, 255) if sentence else (110, 120, 130)
    sent_x = 135 if w < 900 else 170
    cv2.putText(frame, sentence_display, (sent_x, bottom_y), cv2.FONT_HERSHEY_DUPLEX, 0.60 if w < 900 else 0.85, sentence_color, 1 if w < 900 else 2, cv2.LINE_AA)


# =====================================================================
# 5. MAIN REAL-TIME V3 TRANSLATOR LOOP
# =====================================================================
def run_realtime_v3(camera_idx=0, initial_mode="STATIC"):
    print("=" * 72)
    print("  🚀 ISL REAL-TIME TRANSLATION ENGINE V3 (DECOUPLED DUAL MODEL)")
    print("  • Mode Toggle       : [TAB] or [M] keys (STATIC <-> DYNAMIC)")
    print("  • Initial Mode      : " + initial_mode)
    print("  • Static Model      : Residual Dense MLP (35 classes)")
    print("  • Dynamic Model     : BiLSTM + Attention (11 classes)")
    print("=" * 72)

    # Initialize Engine
    engine = DecoupledISLEngineV3(models_dir="models_v3")

    # Initialize MediaPipe Holistic (Complexity 0 for 30+ FPS)
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    holistic = mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=0,              # Optimized for real-time 30+ FPS
        smooth_landmarks=True,
        enable_segmentation=False,
        refine_face_landmarks=False,     # Skip iris tracking for massive speedup
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Open Camera with fallback (DirectShow on Windows for instant Iriun / USB webcam connection)
    cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_idx)

    if not cap.isOpened():
        print(f"[WARNING] Camera index {camera_idx} failed. Scanning cameras...")
        for fallback_idx in [0, 1, 2, 3]:
            if fallback_idx == camera_idx:
                continue
            cap_test = cv2.VideoCapture(fallback_idx, cv2.CAP_DSHOW)
            if not cap_test.isOpened():
                cap_test = cv2.VideoCapture(fallback_idx)
            if cap_test.isOpened():
                ret_t, _ = cap_test.read()
                if ret_t:
                    cap = cap_test
                    camera_idx = fallback_idx
                    print(f"[CAMERA] Connected to camera {camera_idx}.")
                    break
                cap_test.release()
        if not cap.isOpened():
            print("[ERROR] No camera could be opened. Exiting.")
            return


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[CAMERA] Live stream initialized at {actual_w}x{actual_h}")

    # State variables
    current_mode = initial_mode  # "STATIC" or "DYNAMIC"
    sequence_30 = deque(maxlen=SEQUENCE_LENGTH)

    sentence_words = []
    current_sentence = ""

    last_committed_sign = None
    last_commit_time = 0.0

    current_candidate = None
    candidate_start_time = 0.0
    last_hand_seen_time = 0.0
    prev_hand_centroid = None
    hand_is_still = False

    draw_mesh = True
    prev_time = time.time()
    fps = 30.0

    print("\n[READY] V3 Engine is running! Look at the camera window.")
    print("        [TAB] Switch Mode | [SPACE] Add Sign | [C] Clear | [Q] Quit\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_h, frame_w = frame.shape[:2]

        curr_time = time.time()
        fps = 0.85 * fps + 0.15 * (1.0 / max(1e-4, curr_time - prev_time))
        prev_time = curr_time

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb_frame)

        hands_detected = bool(results.left_hand_landmarks or results.right_hand_landmarks)

        if draw_mesh:
            if results.left_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            if results.right_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                    mp_drawing_styles.get_default_pose_landmarks_style()
                )

        raw_vec = extract_keypoints(results)
        norm_vec, _, _ = normalize_vector(raw_vec, frame_w, frame_h)
        sequence_30.append(norm_vec)

        pred_label = "..."
        confidence = 0.0
        top3 = []
        commit_progress = 0.0

        curr_time = time.time()
        # Track hand stillness & motion
        if hands_detected:
            last_hand_seen_time = curr_time
            hand_pts = []
            if results.left_hand_landmarks:
                hand_pts.extend([[lm.x, lm.y] for lm in results.left_hand_landmarks.landmark])
            if results.right_hand_landmarks:
                hand_pts.extend([[lm.x, lm.y] for lm in results.right_hand_landmarks.landmark])

            if hand_pts:
                curr_centroid = np.mean(hand_pts, axis=0)
                if prev_hand_centroid is not None:
                    disp = float(np.linalg.norm(curr_centroid - prev_hand_centroid))
                    hand_is_still = (disp < 0.016)
                else:
                    hand_is_still = True
                prev_hand_centroid = curr_centroid
            else:
                hand_is_still = False
                prev_hand_centroid = None
        else:
            prev_hand_centroid = None
            hand_is_still = False
            if (curr_time - last_hand_seen_time) > 0.5:
                last_committed_sign = None

        # Post-commit transition time gap check
        is_in_cooldown = (curr_time - last_commit_time) < COMMIT_COOLDOWN_SECONDS

        if hands_detected and not is_in_cooldown:
            # =========================================================
            # MODE 1: STATIC (A-Z, 0-9) — Pure Static Model
            # =========================================================
            if current_mode == "STATIC":
                pred_label, confidence, top3 = engine.predict_static(norm_vec)
                top_margin = (top3[0][1] - top3[1][1]) if len(top3) >= 2 else 1.0

                # Must be held STILL, high confidence (>=0.80), and distinct margin (>=0.20)
                is_valid_pose = hand_is_still and (confidence >= STATIC_CONF_THRESHOLD) and (top_margin >= 0.20)

                if is_valid_pose:
                    if pred_label == current_candidate:
                        elapsed = curr_time - candidate_start_time
                        commit_progress = min(1.0, elapsed / STATIC_HOLD_SECONDS)

                        if elapsed >= STATIC_HOLD_SECONDS:
                            if pred_label != last_committed_sign:
                                sentence_words.append(pred_label)
                                current_sentence = " ".join(sentence_words)
                                last_committed_sign = pred_label
                                last_commit_time = curr_time
                            current_candidate = None
                            commit_progress = 0.0
                    else:
                        current_candidate = pred_label
                        candidate_start_time = curr_time
                        commit_progress = 0.0
                else:
                    current_candidate = None
                    commit_progress = 0.0

            # =========================================================
            # MODE 2: DYNAMIC (Gestures / Words) — Pure Dynamic Model
            # =========================================================
            else:
                commit_progress = 0.0
                if len(sequence_30) == SEQUENCE_LENGTH:
                    pred_label, confidence, top3 = engine.predict_dynamic(np.array(sequence_30))

                    # Auto-commit completed dynamic gesture upon high confidence
                    if confidence >= DYNAMIC_CONF_THRESHOLD:
                        if (curr_time - last_commit_time) > DYNAMIC_COOLDOWN_SECONDS:
                            if pred_label != last_committed_sign:
                                sentence_words.append(pred_label)
                                current_sentence = " ".join(sentence_words)
                                last_committed_sign = pred_label
                                last_commit_time = curr_time
        else:
            current_candidate = None
            commit_progress = 0.0

        # Draw HUD Overlay
        draw_hud(frame, current_mode, pred_label, confidence, current_sentence,
                 top3, fps, hands_detected, commit_progress)

        cv2.imshow("ISL Translation Engine V3 - Mode Toggle", frame)

        # Handle Keyboard Inputs
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key in (9, ord('m'), ord('M')):  # TAB or 'M' -> Toggle Mode!
            current_mode = "DYNAMIC" if current_mode == "STATIC" else "STATIC"
            current_candidate = None
            last_committed_sign = None
            print(f"[SWITCH] Mode toggled to: {current_mode}")
        elif key == ord('1'):  # Direct switch to Static
            current_mode = "STATIC"
            current_candidate = None
            print(f"[SWITCH] Mode set to: STATIC")
        elif key == ord('2'):  # Direct switch to Dynamic
            current_mode = "DYNAMIC"
            current_candidate = None
            print(f"[SWITCH] Mode set to: DYNAMIC")
        elif key == 32:  # Spacebar -> Instant Add Current Word
            if pred_label and pred_label != "...":
                sentence_words.append(pred_label)
                current_sentence = " ".join(sentence_words)
                last_committed_sign = pred_label
                last_commit_time = curr_time
        elif key == ord('c') or key == ord('C'):  # Clear sentence
            sentence_words.clear()
            current_sentence = ""
            last_committed_sign = None
        elif key == 8:  # Backspace
            if sentence_words:
                sentence_words.pop()
                current_sentence = " ".join(sentence_words)
        elif key == ord('h') or key == ord('H'):
            draw_mesh = not draw_mesh

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    print("[INFO] V3 Engine closed cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISL Real-Time Translation Engine V3")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    parser.add_argument("--mode", type=str, default="STATIC", choices=["STATIC", "DYNAMIC"],
                        help="Initial mode (STATIC or DYNAMIC)")
    args = parser.parse_args()

    run_realtime_v3(camera_idx=args.camera, initial_mode=args.mode)
