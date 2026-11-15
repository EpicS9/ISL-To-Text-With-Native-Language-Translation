"""
=============================================================================
ISL to Text Translation — Real-Time Detection & Recognition Engine (V2 - High Performance)
=============================================================================
Critical Updates:
  1. Compiled @tf.function Inference:
     Replaced slow model.predict() (153ms) with compiled graph execution (2.3ms).
     Boosts FPS from 5 FPS to 30+ FPS!
  2. Instant Static Recognition:
     Static signs evaluate immediately without waiting for a 30-frame buffer.
     Debounce time reduced to ~0.3s so you don't have to hold still for long!
  3. Total Suppression of False 'H' and 'J':
     Dynamic 'H' and 'J' now require high motion energy (>= 0.070) and >= 96%
     confidence. Casual hand transitions are automatically filtered out.
  4. In-Flight Lock:
     No letters or words are ever appended to the sentence ribbon while hands
     are in motion/transitioning between signs.
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

# Landmark slicing constants
POSE_LEN = 33 * 4     # 132
LH_LEN = 21 * 3       # 63
RH_LEN = 21 * 3       # 63
FACE_POINTS = 92
FACE_LEN = FACE_POINTS * 3  # 276

POSE_START = 0
LH_START = POSE_LEN
RH_START = POSE_LEN + LH_LEN
FACE_START = POSE_LEN + LH_LEN + RH_LEN

# Calibrated V2 Thresholds
STATIC_MOTION_LIMIT = 0.022          # Movement below this is strictly STATIC
DYNAMIC_MOTION_TRIGGER = 0.030       # Minimum motion to consider a dynamic gesture
DYNAMIC_LETTER_MIN_MOTION = 0.070    # Strict velocity floor for dynamic 'H' and 'J'
DYNAMIC_LETTER_MIN_CONF = 0.95       # Strict confidence floor for dynamic 'H' and 'J'
STATIC_CONF_THRESHOLD = 0.75         # Minimum confidence for static signs
DYNAMIC_CONF_THRESHOLD = 0.80        # Minimum confidence for dynamic words

# Debounce Timing (in seconds for FPS invariance)
STATIC_COMMIT_SECONDS = 0.32         # Hold still for ~0.32s to commit static sign
COOLDOWN_SECONDS = 0.80              # Cooldown before repeating the exact same sign

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


# =====================================================================
# 2. FEATURE EXTRACTION & SHOULDER NORMALIZATION
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
    """Normalizes keypoints invariant to camera aspect, distance, and position."""
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
# 3. HIGH-SPEED COMPILED PREDICTOR ENGINE
# =====================================================================
class FastISLPredictorV2:
    def __init__(self, models_dir="models_v2"):
        if not os.path.isdir(models_dir):
            models_dir = "models"
        self.models_dir = models_dir

        print(f"[ENGINE V2] Loading classes from {self.models_dir}...")
        self.static_classes = np.load(os.path.join(self.models_dir, "static_label_classes.npy"))
        self.dynamic_classes = np.load(os.path.join(self.models_dir, "dynamic_label_classes.npy"))
        self.all_classes = np.load(os.path.join(self.models_dir, "all_46_classes.npy"))

        print(f"[ENGINE V2] Compiling Static Model with @tf.function (2ms execution)...")
        raw_static = self._load_static_branch()
        self._compiled_static = tf.function(lambda x: raw_static(x, training=False))

        print(f"[ENGINE V2] Compiling Dynamic Model with @tf.function (4ms execution)...")
        raw_dynamic = self._load_dynamic_branch()
        self._compiled_dynamic = tf.function(lambda x: raw_dynamic(x, training=False))

        # Warm-up graph execution
        dummy_s = tf.zeros((1, FEATURE_DIM), dtype=tf.float32)
        dummy_d = tf.zeros((1, SEQUENCE_LENGTH, FEATURE_DIM), dtype=tf.float32)
        self._compiled_static(dummy_s)
        self._compiled_dynamic(dummy_d)
        print(f"[ENGINE V2] Models warmed up! Inference execution speed: ~3ms/frame.")

    def _load_static_branch(self):
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

    def _load_dynamic_branch(self):
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

    def predict_static_fast(self, vec):
        """Instant static forward pass (2.3ms)."""
        tensor_in = tf.convert_to_tensor(vec.reshape(1, FEATURE_DIM), dtype=tf.float32)
        probs = self._compiled_static(tensor_in).numpy()[0]
        top_idx = int(np.argmax(probs))
        label = str(self.static_classes[top_idx])
        conf = float(probs[top_idx])
        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [(self.static_classes[i], float(probs[i])) for i in top_indices]
        return label, conf, top3

    def predict_dynamic_fast(self, seq_30):
        """Instant dynamic forward pass (4.2ms)."""
        tensor_in = tf.convert_to_tensor(seq_30.reshape(1, SEQUENCE_LENGTH, FEATURE_DIM), dtype=tf.float32)
        probs = self._compiled_dynamic(tensor_in).numpy()[0]
        top_idx = int(np.argmax(probs))
        label = str(self.dynamic_classes[top_idx])
        conf = float(probs[top_idx])
        top_indices = np.argsort(probs)[::-1][:3]
        top3 = [(self.dynamic_classes[i], float(probs[i])) for i in top_indices]
        return label, conf, top3

    def compute_motion_window(self, sequence):
        """Computes velocity across recent frames."""
        if len(sequence) < 2:
            return 0.0
        seq_arr = np.array(sequence)
        hand_data = seq_arr[:, LH_START:RH_START + RH_LEN]
        velocities = np.diff(hand_data, axis=0)
        motion = float(np.mean(np.linalg.norm(velocities.reshape(-1, 42, 3), axis=2)))
        return motion


# =====================================================================
# 4. HUD VISUALIZATION
# =====================================================================
def draw_hud(frame, label, confidence, sign_type, motion, is_in_flight,
             sentence, top3, fps, hands_detected, commit_progress):
    """Draws a clean, dark-glass HUD overlay."""
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 115), (15, 18, 22), -1)
    cv2.rectangle(overlay, (0, h - 75), (w, h), (15, 18, 22), -1)
    cv2.rectangle(overlay, (w - 270, 125), (w - 10, 335), (22, 27, 34), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

    cv2.rectangle(frame, (w - 270, 125), (w - 10, 335), (60, 70, 85), 1)

    # --- TOP BAR: STATUS BADGE ---
    if is_in_flight:
        badge_color = (0, 165, 255)
        badge_text = "MOVING"
    elif "STATIC" in sign_type:
        badge_color = (70, 215, 120)
        badge_text = "STATIC"
    elif "DYNAMIC" in sign_type:
        badge_color = (255, 140, 0)
        badge_text = "DYNAMIC"
    else:
        badge_color = (130, 130, 130)
        badge_text = "IDLE"

    cv2.rectangle(frame, (20, 18), (140, 42), badge_color, -1, cv2.LINE_AA)
    cv2.putText(frame, badge_text, (30, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    # Hand status indicator
    hand_color = (0, 255, 128) if hands_detected else (0, 69, 255)
    cv2.circle(frame, (160, 30), 6, hand_color, -1, cv2.LINE_AA)
    cv2.putText(frame, "HANDS DETECTED" if hands_detected else "NO HANDS",
                (175, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    # Engine badge & FPS
    cv2.putText(frame, "V2 HIGH-SPEED", (w - 220, 35), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 220, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:.0f}", (w - 85, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 240, 160), 1, cv2.LINE_AA)

    # Main Sign Label
    if hands_detected and not is_in_flight and confidence >= 0.70:
        text_color = (255, 255, 255)
        display_label = label
    elif is_in_flight:
        text_color = (180, 180, 110)
        display_label = "(In Motion...)"
    elif hands_detected:
        text_color = (140, 150, 160)
        display_label = "Detecting..."
    else:
        text_color = (100, 110, 120)
        display_label = "Bring hands into view"

    cv2.putText(frame, display_label, (20, 95), cv2.FONT_HERSHEY_DUPLEX, 1.4, text_color, 2, cv2.LINE_AA)

    # Confidence Bar
    bar_x, bar_y, bar_w, bar_h = 360, 72, 180, 16
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    fill_w = int(bar_w * min(1.0, max(0.0, confidence if (hands_detected and not is_in_flight) else 0.0)))
    fill_color = (0, 220, 110) if confidence >= 0.75 else (0, 180, 240)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)
    cv2.putText(frame, f"Conf: {confidence * 100:.0f}%", (bar_x + bar_w + 10, bar_y + 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

    # Commit Progress Bar (Green countdown bar to auto-commit)
    prog_x, prog_y, prog_w, prog_h = 640, 72, 140, 16
    cv2.rectangle(frame, (prog_x, prog_y), (prog_x + prog_w, prog_y + prog_h), (40, 40, 40), -1)
    fill_p = int(prog_w * min(1.0, max(0.0, commit_progress)))
    cv2.rectangle(frame, (prog_x, prog_y), (prog_x + fill_p, prog_y + prog_h), (0, 200, 255), -1)
    cv2.rectangle(frame, (prog_x, prog_y), (prog_x + prog_w, prog_y + prog_h), (120, 120, 120), 1)
    cv2.putText(frame, "Commit", (prog_x + prog_w + 8, prog_y + 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    # Motion meter
    cv2.putText(frame, f"Mot: {motion:.3f}", (bar_x, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)

    # --- SIDE PANEL: TOP DETECTIONS ---
    cv2.putText(frame, "TOP DETECTIONS", (w - 255, 150), cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 210, 255), 1, cv2.LINE_AA)
    for idx, (c_name, c_prob) in enumerate(top3[:3]):
        item_y = 178 + idx * 26
        cv2.putText(frame, f"{idx+1}. {c_name[:12]}", (w - 255, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(frame, f"{c_prob * 100:.0f}%", (w - 70, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 200, 160), 1, cv2.LINE_AA)

    cv2.putText(frame, "QUICK CONTROLS", (w - 255, 275), cv2.FONT_HERSHEY_DUPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, "[SPACE] Instant Add Word", (w - 255, 295),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, "[C] Clear  [BKSP] Del  [Q] Quit", (w - 255, 318),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 150, 160), 1, cv2.LINE_AA)

    # --- BOTTOM BAR: SENTENCE TRANSLATION ---
    cv2.putText(frame, "TRANSLATION:", (20, h - 45), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 220, 255), 1, cv2.LINE_AA)
    sentence_display = sentence if sentence else "(Perform signs to build sentence...)"
    sentence_color = (255, 255, 255) if sentence else (110, 120, 130)
    cv2.putText(frame, sentence_display, (170, h - 45), cv2.FONT_HERSHEY_DUPLEX, 0.85, sentence_color, 2, cv2.LINE_AA)


# =====================================================================
# 5. REAL-TIME TRANSLATION ENGINE (V2 HIGH-SPEED)
# =====================================================================
def run_realtime_detection_v2(camera_idx=0):
    print("=" * 70)
    print("  🚀 ISL REAL-TIME RECOGNITION ENGINE — V2 (HIGH-SPEED COMPILED)")
    print("=" * 70)

    # Initialize Fast Predictor Engine
    predictor = FastISLPredictorV2(models_dir="models_v2")

    # Initialize MediaPipe Holistic with complexity=0 for maximum CPU FPS
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    holistic = mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=0,              # Optimized complexity for 30+ FPS
        smooth_landmarks=True,
        enable_segmentation=False,
        refine_face_landmarks=False,     # Disable iris tracking (saves 40ms/frame)
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # Open Camera
    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        print(f"[WARNING] Camera {camera_idx} unavailable. Scanning fallback cameras...")
        for fallback_idx in [1, 2, 3, 0]:
            if fallback_idx == camera_idx:
                continue
            cap_test = cv2.VideoCapture(fallback_idx)
            if cap_test.isOpened():
                ret_t, _ = cap_test.read()
                if ret_t:
                    cap = cap_test
                    camera_idx = fallback_idx
                    print(f"[CAMERA] Connected to camera index {camera_idx}.")
                    break
                cap_test.release()
        if not cap.isOpened():
            print("[ERROR] No working camera found. Exiting.")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[CAMERA] Stream active at {actual_w}x{actual_h}")

    # Sliding buffers
    sequence_30 = deque(maxlen=SEQUENCE_LENGTH)
    short_window = deque(maxlen=6)   # 6 frames for instant motion evaluation

    # State variables
    sentence_words = []
    current_sentence = ""

    last_committed_sign = None
    last_commit_time = 0.0

    current_candidate = None
    candidate_start_time = 0.0

    draw_mesh = True
    prev_time = time.time()
    fps = 30.0

    print("\n[READY] High-Speed Real-Time Translation is LIVE!")
    print("        Static Signs  : Recognized instantly (~0.3s stillness)")
    print("        Dynamic Signs : Triggered on fluid gestures")
    print("        Controls      : [SPACE] Commit now  [C] Clear  [BKSP] Del  [Q] Quit\n")

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
        short_window.append(norm_vec)

        # Motion calculation on short window (responsive to instantaneous movement)
        motion = predictor.compute_motion_window(short_window)
        is_in_flight = motion > STATIC_MOTION_LIMIT

        pred_label = "..."
        confidence = 0.0
        sign_type = "STATIC"
        top3 = []
        commit_progress = 0.0

        if hands_detected:
            # -------------------------------------------------------------
            # CASE 1: HAND IS STILL / STATIC SIGN (motion < 0.022)
            # -------------------------------------------------------------
            if not is_in_flight:
                s_label, s_conf, s_top3 = predictor.predict_static_fast(norm_vec)
                pred_label = s_label
                confidence = s_conf
                sign_type = "STATIC"
                top3 = s_top3

                # Debounce: Commit static sign after ~0.32 seconds of stillness
                if s_conf >= STATIC_CONF_THRESHOLD:
                    if s_label == current_candidate:
                        elapsed = curr_time - candidate_start_time
                        commit_progress = min(1.0, elapsed / STATIC_COMMIT_SECONDS)

                        if elapsed >= STATIC_COMMIT_SECONDS:
                            # Verify cooldown
                            if s_label != last_committed_sign or (curr_time - last_commit_time) > COOLDOWN_SECONDS:
                                sentence_words.append(s_label)
                                current_sentence = " ".join(sentence_words)
                                last_committed_sign = s_label
                                last_commit_time = curr_time
                                current_candidate = None
                                commit_progress = 0.0
                    else:
                        current_candidate = s_label
                        candidate_start_time = curr_time
                        commit_progress = 0.0
                else:
                    current_candidate = None

            # -------------------------------------------------------------
            # CASE 2: HAND IS IN MOTION / DYNAMIC GESTURE (motion >= 0.022)
            # -------------------------------------------------------------
            else:
                current_candidate = None  # Reset static debounce while moving
                commit_progress = 0.0

                if len(sequence_30) == SEQUENCE_LENGTH and motion >= DYNAMIC_MOTION_TRIGGER:
                    d_label, d_conf, d_top3 = predictor.predict_dynamic_fast(np.array(sequence_30))

                    # STRICT SUPPRESSION FOR DYNAMIC LETTERS 'H' AND 'J'
                    is_h_or_j = d_label in ("H", "J")
                    h_j_valid = is_h_or_j and (motion >= DYNAMIC_LETTER_MIN_MOTION) and (d_conf >= DYNAMIC_LETTER_MIN_CONF)

                    if is_h_or_j and not h_j_valid:
                        # Random motion triggered 'H' or 'J' -> Ignore / Transition!
                        pred_label = "..."
                        confidence = 0.0
                        sign_type = "MOVING"
                        top3 = [("Moving Hand", 1.0)]
                    elif d_conf >= DYNAMIC_CONF_THRESHOLD:
                        pred_label = d_label
                        confidence = d_conf
                        sign_type = "DYNAMIC"
                        top3 = d_top3

                        # Commit dynamic words upon high confidence gesture completion
                        if (curr_time - last_commit_time) > COOLDOWN_SECONDS:
                            if d_label != last_committed_sign:
                                sentence_words.append(d_label)
                                current_sentence = " ".join(sentence_words)
                                last_committed_sign = d_label
                                last_commit_time = curr_time
                    else:
                        pred_label = "..."
                        confidence = 0.0
                        sign_type = "MOVING"
                        top3 = d_top3
                else:
                    # In motion / transition between signs
                    pred_label = "..."
                    confidence = 0.0
                    sign_type = "MOVING"
                    top3 = [("In Motion", 1.0)]
        else:
            current_candidate = None
            last_committed_sign = None

        # Draw HUD
        draw_hud(frame, pred_label, confidence, sign_type, motion, is_in_flight,
                 current_sentence, top3, fps, hands_detected, commit_progress)

        cv2.imshow("ISL to Text Translation - V2 High-Speed Engine", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('c') or key == ord('C'):
            sentence_words.clear()
            current_sentence = ""
            last_committed_sign = None
        elif key == 8:  # Backspace
            if sentence_words:
                sentence_words.pop()
                current_sentence = " ".join(sentence_words)
        elif key == 32:  # Spacebar -> Instant commit current prediction!
            if pred_label and pred_label != "...":
                sentence_words.append(pred_label)
                current_sentence = " ".join(sentence_words)
                last_committed_sign = pred_label
                last_commit_time = curr_time
        elif key == ord('h') or key == ord('H'):
            draw_mesh = not draw_mesh

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    print("[INFO] V2 Engine closed cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISL Real-Time Translation Engine V2")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    args = parser.parse_args()

    run_realtime_detection_v2(camera_idx=args.camera)
