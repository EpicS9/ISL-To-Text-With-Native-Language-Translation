"""
=============================================================================
ISL to Text Translation — Real-Time Detection & Recognition Engine
=============================================================================
Unified 46-Class Real-Time Inference:
  • 35 Static Signs  (0-9, A-Z)
  • 11 Dynamic Signs (Claps, Congrats, H, Hello, J, No, Please, Sorry,
                      ThankYou, Welcome, Yes)

Key Features:
  1. Shoulder-relative scale & aspect normalization (exact match with dataset)
  2. 30-frame sliding temporal window buffer
  3. Dynamic Motion Energy Gate (automatically routes to static or dynamic branch)
  4. Prediction debouncing & Sentence Accumulator (builds full sentences)
  5. Interactive HUD with motion meter, confidence bar, and sentence ribbon
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

import keras
from keras import layers
import tensorflow as tf

# =====================================================================
# 1. CONSTANTS & FEATURE CONFIGURATION (MUST MATCH DATASET EXACTLY)
# =====================================================================
SEQUENCE_LENGTH = 30
FEATURE_DIM = 534

# Landmark slicing constants
POSE_LEN = 33 * 4     # 132
LH_LEN = 21 * 3       # 63
RH_LEN = 21 * 3       # 63
FACE_POINTS = 92
FACE_LEN = FACE_POINTS * 3  # 276
# Total = 132 + 63 + 63 + 276 = 534

POSE_START = 0
LH_START = POSE_LEN
RH_START = POSE_LEN + LH_LEN
FACE_START = POSE_LEN + LH_LEN + RH_LEN

# MediaPipe face mesh connections used during data collection
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

# Motion energy gate cutoff (empirically calibrated during training)
DEFAULT_MOTION_CUTOFF = 0.0050
DEFAULT_CONFIDENCE_THRESHOLD = 0.70
DEBOUNCE_FRAMES = 12   # frames a sign must persist before appending to sentence
COOLDOWN_FRAMES = 25   # cooldown frames before appending the same sign again


# =====================================================================
# 2. KEYPOINT EXTRACTION & SHOULDER NORMALIZATION PIPELINE
# =====================================================================
def extract_keypoints(results):
    """Extracts raw keypoints from MediaPipe holistic results."""
    # Pose: 33 landmarks * 4 (x, y, z, visibility)
    if results.pose_landmarks:
        pose = np.array([[res.x, res.y, res.z, res.visibility]
                         for res in results.pose_landmarks.landmark], dtype=np.float32).flatten()
    else:
        pose = np.zeros(POSE_LEN, dtype=np.float32)

    # Left hand: 21 landmarks * 3 (x, y, z)
    if results.left_hand_landmarks:
        lh = np.array([[res.x, res.y, res.z]
                       for res in results.left_hand_landmarks.landmark], dtype=np.float32).flatten()
    else:
        lh = np.zeros(LH_LEN, dtype=np.float32)

    # Right hand: 21 landmarks * 3 (x, y, z)
    if results.right_hand_landmarks:
        rh = np.array([[res.x, res.y, res.z]
                       for res in results.right_hand_landmarks.landmark], dtype=np.float32).flatten()
    else:
        rh = np.zeros(RH_LEN, dtype=np.float32)

    # Face subset: 92 landmarks * 3 (x, y, z)
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
    """
    Applies the exact dataset normalization:
    1. Aspect ratio rescaling on x-coordinates
    2. Translation centering to mid-shoulder origin
    3. Scale normalization by shoulder span
    """
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
# 3. UNIFIED MODEL LOADER & RUNTIME PREDICTOR
# =====================================================================
class UnifiedISLPredictor:
    """
    Unified 46-Class Predictor:
    Loads both the tuned Static and Dynamic branches and gates them dynamically
    using temporal motion energy.
    """
    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.static_classes = np.load(os.path.join(models_dir, "static_label_classes.npy"))
        self.dynamic_classes = np.load(os.path.join(models_dir, "dynamic_label_classes.npy"))
        self.all_classes = np.load(os.path.join(models_dir, "all_46_classes.npy"))

        print(f"[PREDICTOR] Loading Static Model (35 classes)...")
        self.static_model = self._load_static_branch()

        print(f"[PREDICTOR] Loading Dynamic Model (11 classes)...")
        self.dynamic_model = self._load_dynamic_branch()

        # Warm-up inference
        dummy_static = np.zeros((1, FEATURE_DIM), dtype=np.float32)
        dummy_dynamic = np.zeros((1, SEQUENCE_LENGTH, FEATURE_DIM), dtype=np.float32)
        self.static_model.predict(dummy_static, verbose=0)
        self.dynamic_model.predict(dummy_dynamic, verbose=0)
        print(f"[PREDICTOR] Both branches warmed up and ready for 46-class real-time detection.")

    def _load_static_branch(self):
        keras_path = os.path.join(self.models_dir, "isl_static_model_final.keras")
        with zipfile.ZipFile(keras_path) as z:
            cfg = json.loads(z.read("config.json"))
            w_bytes = z.read("model.weights.h5")

        def clean_dict(d):
            if isinstance(d, dict):
                d.pop("quantization_config", None)
                d.pop("optional", None)
                if "batch_shape" in d:
                    d["batch_input_shape"] = d.pop("batch_shape")
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

    def compute_motion_energy(self, sequence):
        """
        Computes the velocity of hands and wrists over the 30-frame window.
        Uses Left Hand (63 dims) and Right Hand (63 dims) coordinates.
        """
        # Slice both hands: indices LH_START to (RH_START + RH_LEN)
        hand_data = sequence[:, LH_START:RH_START + RH_LEN]
        velocities = np.diff(hand_data, axis=0)
        # Average Euclidean displacement per frame
        motion_energy = float(np.mean(np.linalg.norm(velocities.reshape(-1, 42, 3), axis=2)))
        return motion_energy

    def predict(self, sequence_window, motion_cutoff=DEFAULT_MOTION_CUTOFF):
        """
        Takes a (30, 534) numpy buffer and produces the unified 46-class prediction.
        Returns:
          label          : predicted string sign
          confidence     : confidence score [0.0 - 1.0]
          sign_type      : 'DYNAMIC' or 'STATIC'
          motion_energy  : computed motion energy
          top3           : list of (class_name, prob)
        """
        motion = self.compute_motion_energy(sequence_window)
        is_dynamic = motion > motion_cutoff

        if is_dynamic:
            # Route to Dynamic branch
            inp_seq = sequence_window.reshape(1, SEQUENCE_LENGTH, FEATURE_DIM)
            probs = self.dynamic_model.predict(inp_seq, verbose=0)[0]
            top_idx = int(np.argmax(probs))
            label = str(self.dynamic_classes[top_idx])
            conf = float(probs[top_idx])
            sign_type = "DYNAMIC"

            # Top 3 candidates
            top_indices = np.argsort(probs)[::-1][:3]
            top3 = [(self.dynamic_classes[i], float(probs[i])) for i in top_indices]
        else:
            # Route to Static branch on the central stable keyframe
            keyframe = sequence_window[SEQUENCE_LENGTH // 2].reshape(1, FEATURE_DIM)
            probs = self.static_model.predict(keyframe, verbose=0)[0]
            top_idx = int(np.argmax(probs))
            label = str(self.static_classes[top_idx])
            conf = float(probs[top_idx])
            sign_type = "STATIC"

            # Top 3 candidates
            top_indices = np.argsort(probs)[::-1][:3]
            top3 = [(self.static_classes[i], float(probs[i])) for i in top_indices]

        return label, conf, sign_type, motion, top3


# =====================================================================
# 4. HUD & VISUALIZATION UTILITIES
# =====================================================================
def draw_hud(frame, label, confidence, sign_type, motion, motion_cutoff,
             conf_threshold, sentence, top3, fps, hands_detected):
    """Draws a modern, polished dark-glass HUD overlay on the camera frame."""
    h, w = frame.shape[:2]

    # Semi-transparent top bar (Header & Prediction)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 115), (15, 18, 22), -1)

    # Semi-transparent bottom bar (Sentence Ribbon)
    cv2.rectangle(overlay, (0, h - 75), (w, h), (15, 18, 22), -1)

    # Semi-transparent side bar (Status & Top candidates)
    cv2.rectangle(overlay, (w - 260, 125), (w - 10, 310), (22, 27, 34), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Borders for panels
    cv2.rectangle(frame, (w - 260, 125), (w - 10, 310), (60, 70, 85), 1)

    # --- TOP BAR: PREDICTED SIGN ---
    # Type Badge (STATIC vs DYNAMIC)
    badge_color = (0, 165, 255) if sign_type == "DYNAMIC" else (70, 210, 120)
    cv2.rectangle(frame, (20, 18), (120, 42), badge_color, -1, cv2.LINE_AA)
    cv2.putText(frame, sign_type, (30, 35), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    # Hand status indicator
    hand_color = (0, 255, 128) if hands_detected else (0, 69, 255)
    cv2.circle(frame, (140, 30), 6, hand_color, -1, cv2.LINE_AA)
    cv2.putText(frame, "HANDS TRACKED" if hands_detected else "NO HANDS",
                (155, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    # FPS
    cv2.putText(frame, f"FPS: {fps:.0f}", (w - 100, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)

    # Main Sign Label
    if hands_detected and confidence >= conf_threshold:
        text_color = (255, 255, 255)
        display_label = label
    else:
        text_color = (130, 140, 150)
        display_label = "Waiting for sign..." if hands_detected else "Bring hands into view"

    cv2.putText(frame, display_label, (20, 95), cv2.FONT_HERSHEY_DUPLEX, 1.4, text_color, 2, cv2.LINE_AA)

    # Confidence Bar
    bar_x, bar_y, bar_w, bar_h = 360, 72, 220, 16
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
    fill_w = int(bar_w * min(1.0, max(0.0, confidence if hands_detected else 0.0)))
    fill_color = (0, 220, 110) if confidence >= conf_threshold else (0, 180, 240)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)
    cv2.putText(frame, f"Conf: {confidence * 100:.1f}%", (bar_x + bar_w + 12, bar_y + 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220, 220, 220), 1, cv2.LINE_AA)

    # Motion Energy Gauge
    motion_ratio = min(1.0, motion / (motion_cutoff * 3.0))
    mot_x, mot_y, mot_w, mot_h = 670, 72, 140, 16
    cv2.rectangle(frame, (mot_x, mot_y), (mot_x + mot_w, mot_y + mot_h), (50, 50, 50), -1)
    fill_m = int(mot_w * motion_ratio)
    m_color = (0, 165, 255) if motion > motion_cutoff else (100, 180, 100)
    cv2.rectangle(frame, (mot_x, mot_y), (mot_x + fill_m, mot_y + mot_h), m_color, -1)
    cv2.rectangle(frame, (mot_x, mot_y), (mot_x + mot_w, mot_y + mot_h), (120, 120, 120), 1)
    cv2.putText(frame, f"Motion: {motion:.4f}", (mot_x + mot_w + 10, mot_y + 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    # --- SIDE PANEL: TOP CANDIDATES & SHORTCUTS ---
    cv2.putText(frame, "TOP CANDIDATES", (w - 245, 150), cv2.FONT_HERSHEY_DUPLEX, 0.45, (0, 200, 255), 1, cv2.LINE_AA)
    for idx, (c_name, c_prob) in enumerate(top3):
        item_y = 178 + idx * 26
        cv2.putText(frame, f"{idx+1}. {c_name[:10]}", (w - 245, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1, cv2.LINE_AA)
        cv2.putText(frame, f"{c_prob * 100:.1f}%", (w - 75, item_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 200, 160), 1, cv2.LINE_AA)

    cv2.putText(frame, "CONTROLS", (w - 245, 275), cv2.FONT_HERSHEY_DUPLEX, 0.40, (180, 180, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, "[C] Clear  [BKSP] Del  [Q] Quit", (w - 250, 298),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 150, 160), 1, cv2.LINE_AA)

    # --- BOTTOM BAR: SENTENCE RIBBON ---
    cv2.putText(frame, "TRANSLATION:", (20, h - 45), cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 220, 255), 1, cv2.LINE_AA)
    sentence_display = sentence if sentence else "(Perform signs to build a sentence...)"
    sentence_color = (255, 255, 255) if sentence else (110, 120, 130)
    cv2.putText(frame, sentence_display, (170, h - 45), cv2.FONT_HERSHEY_DUPLEX, 0.85, sentence_color, 2, cv2.LINE_AA)


# =====================================================================
# 5. MAIN REAL-TIME LOOP
# =====================================================================
def run_realtime_detection(camera_idx=0, motion_cutoff=DEFAULT_MOTION_CUTOFF,
                           conf_threshold=DEFAULT_CONFIDENCE_THRESHOLD):
    print("=" * 65)
    print("  🚀 INITIALIZING ISL TO TEXT TRANSLATION RUNTIME")
    print("=" * 65)

    # 1. Initialize Predictor
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    predictor = UnifiedISLPredictor(models_dir=models_dir)

    # 2. Initialize MediaPipe Holistic
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    holistic = mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        refine_face_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    # 3. Initialize Camera
    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        print(f"[WARNING] Could not open camera at index {camera_idx}. Searching available cameras...")
        found = False
        for fallback_idx in [1, 2, 3, 0]:
            if fallback_idx == camera_idx:
                continue
            cap_test = cv2.VideoCapture(fallback_idx)
            if cap_test.isOpened():
                ret_t, _ = cap_test.read()
                if ret_t:
                    cap = cap_test
                    camera_idx = fallback_idx
                    found = True
                    print(f"[CAMERA] Successfully connected to fallback camera index {camera_idx}.")
                    break
                cap_test.release()
        if not found:
            print("[ERROR] No working camera found. Please check your webcam connection.")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[CAMERA] Opened camera {camera_idx} at {actual_w}x{actual_h}")

    # 4. State variables
    sequence_buffer = deque(maxlen=SEQUENCE_LENGTH)
    sentence_words = []
    current_sentence = ""

    last_appended_sign = None
    debounce_counter = 0
    cooldown_counter = 0
    candidate_sign = None

    draw_mesh = True
    prev_time = time.time()
    fps = 30.0

    print("\n[READY] Real-time detection is LIVE! Look at the camera window.")
    print("        Controls: [C] Clear  [Backspace] Remove last word  [H] Toggle Landmarks  [Q] Quit\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Frame capture dropped.")
            break

        # Mirror horizontally for natural webcam interaction
        frame = cv2.flip(frame, 1)
        frame_h, frame_w = frame.shape[:2]

        # Calculate FPS
        curr_time = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(1e-4, curr_time - prev_time))
        prev_time = curr_time

        # MediaPipe inference
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb_frame)

        # Check hand presence
        hands_detected = bool(results.left_hand_landmarks or results.right_hand_landmarks)

        # Draw landmarks if enabled
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

        # Feature extraction & normalization
        raw_vec = extract_keypoints(results)
        norm_vec, _, _ = normalize_vector(raw_vec, frame_w, frame_h)
        sequence_buffer.append(norm_vec)

        # Prediction state defaults
        pred_label = "..."
        confidence = 0.0
        sign_type = "STATIC"
        motion = 0.0
        top3 = []

        # Predict when buffer is full
        if len(sequence_buffer) == SEQUENCE_LENGTH and hands_detected:
            window_arr = np.array(sequence_buffer, dtype=np.float32)
            pred_label, confidence, sign_type, motion, top3 = predictor.predict(
                window_arr, motion_cutoff=motion_cutoff
            )

            # Debouncing logic to build stable sentences
            if confidence >= conf_threshold:
                if pred_label == candidate_sign:
                    debounce_counter += 1
                else:
                    candidate_sign = pred_label
                    debounce_counter = 1

                # If sign is held steadily past debounce threshold
                if debounce_counter >= DEBOUNCE_FRAMES and cooldown_counter == 0:
                    if candidate_sign != last_appended_sign:
                        sentence_words.append(candidate_sign)
                        current_sentence = " ".join(sentence_words)
                        last_appended_sign = candidate_sign
                        cooldown_counter = COOLDOWN_FRAMES
            else:
                debounce_counter = max(0, debounce_counter - 1)
        else:
            debounce_counter = 0

        if cooldown_counter > 0:
            cooldown_counter -= 1
        elif not hands_detected:
            last_appended_sign = None

        # Draw UI Overlay
        draw_hud(frame, pred_label, confidence, sign_type, motion, motion_cutoff,
                 conf_threshold, current_sentence, top3, fps, hands_detected)

        cv2.imshow("ISL to Text Translation - Real-time Detection", frame)

        # Keyboard interaction
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("\nExiting detection...")
            break
        elif key == ord('c') or key == ord('C'):  # Clear sentence
            sentence_words.clear()
            current_sentence = ""
            last_appended_sign = None
        elif key == 8:  # Backspace
            if sentence_words:
                sentence_words.pop()
                current_sentence = " ".join(sentence_words)
        elif key == ord('h') or key == ord('H'):  # Toggle landmarks
            draw_mesh = not draw_mesh
        elif key in (ord('+'), ord('=')):  # Increase confidence threshold
            conf_threshold = min(0.95, conf_threshold + 0.05)
            print(f"[CONFIG] Confidence threshold: {conf_threshold:.2f}")
        elif key in (ord('-'), ord('_')):  # Decrease confidence threshold
            conf_threshold = max(0.40, conf_threshold - 0.05)
            print(f"[CONFIG] Confidence threshold: {conf_threshold:.2f}")

    cap.release()
    cv2.destroyAllWindows()
    holistic.close()
    print("[INFO] Cleanup complete. Thank you!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISL Real-Time Translation Engine")
    parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    parser.add_argument("--motion-cutoff", type=float, default=DEFAULT_MOTION_CUTOFF,
                        help="Dynamic motion gate cutoff threshold (default: 0.005)")
    parser.add_argument("--conf-threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD,
                        help="Minimum confidence threshold for classification (default: 0.70)")
    args = parser.parse_args()

    run_realtime_detection(
        camera_idx=args.camera,
        motion_cutoff=args.motion_cutoff,
        conf_threshold=args.conf_threshold
    )
