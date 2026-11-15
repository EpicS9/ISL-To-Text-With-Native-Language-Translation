import cv2
import numpy as np
import os
import json
import time
import mediapipe as mp


# =====================================================================
# ISL DATA ENGINE v10 - pose + hands + optional face,
# hand refinement kept, CVAT-friendly frame/keypoint export added.
# =====================================================================

STATIC_TARGET_SAMPLES = 40
DYNAMIC_TARGET_SEQUENCES = 40
SEQUENCE_LENGTH = 30
TARGET_FPS = 30
FRAME_DELAY = 1.0 / TARGET_FPS
MIN_VALID_FRAME_RATIO = 0.9

REQUIRE_FACE_FOR_STATIC = False

SCALE_DRIFT_WARN_PCT = 0.15
ORIGIN_DRIFT_WARN_PCT = 0.20
STILLNESS_CHECK_FRAMES = 5
STILLNESS_MOVEMENT_THRESHOLD = 0.03

MIN_HAND_BBOX_FRACTION = 0.004
STRICT_MIN_HAND_BBOX_FRACTION = 0.0015
SEGMENT_RATIO_WARN = 3.5
HAND_OVERLAP_WARN_IOU = 0.25

CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720
CAPTURE_FPS = 30

ZOOM_CROP_PADDING_FRAC = 0.6
ZOOM_TARGET_SIZE = 448
REVIEW_ZOOM_PADDING_FRAC = 0.5
REVIEW_ZOOM_OUTPUT_SIZE = 420

EXPORT_CVAT_FRAMES = True
EXPORT_CVAT_KEYPOINT_JSON = True

OUTPUT_ROOT = 'data'
CVAT_EXPORT_SUBDIR = 'cvat_export'

mp_holistic = mp.solutions.holistic
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    enable_segmentation=False,
    refine_face_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

hands_zoom_detector = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.5,
)

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
NUM_FACE_POINTS = len(FACE_LANDMARK_INDICES)

POSE_LEN = 33 * 4
LH_LEN = 21 * 3
RH_LEN = 21 * 3
FACE_LEN = NUM_FACE_POINTS * 3
FEATURE_VECTOR_LENGTH = POSE_LEN + LH_LEN + RH_LEN + FACE_LEN

POSE_START = 0
LH_START = POSE_LEN
RH_START = POSE_LEN + LH_LEN
FACE_START = POSE_LEN + LH_LEN + RH_LEN

SIGNING_RELEVANT_POSE_INDICES = [11, 12, 13, 14, 15, 16]

HAND_FINGER_CHAINS = [
    [0, 1, 2, 3, 4],
    [0, 5, 6, 7, 8],
    [0, 9, 10, 11, 12],
    [0, 13, 14, 15, 16],
    [0, 17, 18, 19, 20],
]

print(f"[CONFIG] Feature vector length: {FEATURE_VECTOR_LENGTH} (pose={POSE_LEN}, left_hand={LH_LEN}, right_hand={RH_LEN}, face={FACE_LEN})")
print(f"[CONFIG] REQUIRE_FACE_FOR_STATIC={REQUIRE_FACE_FOR_STATIC}")
print(f"[CONFIG] Zoomed hand re-detection ENABLED (single pass, crop target size={ZOOM_TARGET_SIZE}px)")


def extract_keypoints(results, override_lh=None, override_rh=None):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(POSE_LEN)

    if override_lh is not None and results.left_hand_landmarks:
        original_z = np.array([lm.z for lm in results.left_hand_landmarks.landmark])
        lh = np.column_stack([override_lh[:, 0], override_lh[:, 1], original_z]).flatten()
    else:
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(LH_LEN)

    if override_rh is not None and results.right_hand_landmarks:
        original_z = np.array([lm.z for lm in results.right_hand_landmarks.landmark])
        rh = np.column_stack([override_rh[:, 0], override_rh[:, 1], original_z]).flatten()
    else:
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(RH_LEN)

    if results.face_landmarks:
        all_face_lm = results.face_landmarks.landmark
        face = np.array([[all_face_lm[i].x, all_face_lm[i].y, all_face_lm[i].z] for i in FACE_LANDMARK_INDICES]).flatten()
    else:
        face = np.zeros(FACE_LEN)

    return np.concatenate([pose, lh, rh, face])


def _rough_hand_bbox_px(hand_landmarks, frame_w, frame_h):
    xs = [lm.x * frame_w for lm in hand_landmarks.landmark]
    ys = [lm.y * frame_h for lm in hand_landmarks.landmark]
    return min(xs), min(ys), max(xs), max(ys)


def _safe_square_crop(frame, x1, y1, x2, y2, padding_frac, out_size):
    frame_h, frame_w = frame.shape[:2]
    bw, bh = x2 - x1, y2 - y1
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
    side = max(bw, bh) * (1.0 + padding_frac)
    half = side / 2.0

    ix1, iy1 = cx - half, cy - half
    ix2, iy2 = cx + half, cy + half

    ax1, ay1 = max(0, ix1), max(0, iy1)
    ax2, ay2 = min(frame_w, ix2), min(frame_h, iy2)

    if ax2 <= ax1 or ay2 <= ay1:
        return None

    side_int = int(round(side))
    if side_int < 2:
        return None

    canvas = np.zeros((side_int, side_int, 3), dtype=frame.dtype)
    paste_x1 = int(round(ax1 - ix1))
    paste_y1 = int(round(ay1 - iy1))
    valid_w = int(round(ax2 - ax1))
    valid_h = int(round(ay2 - ay1))
    paste_x2 = min(side_int, paste_x1 + valid_w)
    paste_y2 = min(side_int, paste_y1 + valid_h)

    src = frame[int(ay1):int(ay1) + (paste_y2 - paste_y1), int(ax1):int(ax1) + (paste_x2 - paste_x1)]
    if src.size == 0:
        return None

    canvas[paste_y1:paste_y2, paste_x1:paste_x2] = src
    resized = cv2.resize(canvas, (out_size, out_size), interpolation=cv2.INTER_CUBIC)
    return resized, ix1, iy1, side


def zoomed_hand_redetect(frame, rough_hand_landmarks, frame_w, frame_h):
    if rough_hand_landmarks is None:
        return None
    x1, y1, x2, y2 = _rough_hand_bbox_px(rough_hand_landmarks, frame_w, frame_h)
    crop_result = _safe_square_crop(frame, x1, y1, x2, y2, ZOOM_CROP_PADDING_FRAC, ZOOM_TARGET_SIZE)
    if crop_result is None:
        return None
    crop_resized, ix1, iy1, side = crop_result

    crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
    zoom_result = hands_zoom_detector.process(crop_rgb)
    if not zoom_result.multi_hand_landmarks:
        return None
    zoom_landmarks = zoom_result.multi_hand_landmarks[0]

    mapped = np.zeros((21, 2), dtype=np.float32)
    for i, lm in enumerate(zoom_landmarks.landmark):
        px_in_square = lm.x * ZOOM_TARGET_SIZE
        py_in_square = lm.y * ZOOM_TARGET_SIZE
        px_in_original_square = px_in_square * (side / ZOOM_TARGET_SIZE)
        py_in_original_square = py_in_square * (side / ZOOM_TARGET_SIZE)
        px_in_frame = ix1 + px_in_original_square
        py_in_frame = iy1 + py_in_original_square
        mapped[i, 0] = px_in_frame / frame_w
        mapped[i, 1] = py_in_frame / frame_h
    return mapped


def refine_hand_landmarks(frame, results, frame_w, frame_h):
    refined_lh = zoomed_hand_redetect(frame, results.left_hand_landmarks, frame_w, frame_h) if results.left_hand_landmarks else None
    refined_rh = zoomed_hand_redetect(frame, results.right_hand_landmarks, frame_w, frame_h) if results.right_hand_landmarks else None
    return refined_lh, refined_rh


def build_review_zoom_panel(annotated_frame, results, frame_w, frame_h):
    crops = []
    for hand_landmarks in [results.left_hand_landmarks, results.right_hand_landmarks]:
        if hand_landmarks is None:
            continue
        x1, y1, x2, y2 = _rough_hand_bbox_px(hand_landmarks, frame_w, frame_h)
        crop_result = _safe_square_crop(annotated_frame, x1, y1, x2, y2, REVIEW_ZOOM_PADDING_FRAC, REVIEW_ZOOM_OUTPUT_SIZE)
        if crop_result is None:
            continue
        crop_resized, _, _, _ = crop_result
        crops.append(crop_resized)
    if not crops:
        return None
    if len(crops) == 1:
        return crops[0]
    return np.hstack(crops)


def get_shoulder_origin_and_scale(vec):
    left_shoulder = vec[11 * 4: 11 * 4 + 3]
    right_shoulder = vec[12 * 4: 12 * 4 + 3]
    origin = (left_shoulder + right_shoulder) / 2.0
    scale = np.linalg.norm(right_shoulder - left_shoulder)
    scale = scale if scale > 1e-6 else 1e-6
    return origin, scale


def normalize_vector(vec, frame_width, frame_height):
    vec = vec.copy()
    aspect = frame_width / frame_height

    def rescale_x(start, count, stride):
        for i in range(count):
            base = start + i * stride
            vec[base] *= aspect

    rescale_x(POSE_START, 33, 4)
    rescale_x(LH_START, 21, 3)
    rescale_x(RH_START, 21, 3)
    rescale_x(FACE_START, NUM_FACE_POINTS, 3)

    origin, scale = get_shoulder_origin_and_scale(vec)

    def normalize_block(start, count, stride):
        for i in range(count):
            base = start + i * stride
            vec[base:base + 3] = (vec[base:base + 3] - origin) / scale

    normalize_block(POSE_START, 33, 4)
    normalize_block(LH_START, 21, 3)
    normalize_block(RH_START, 21, 3)
    normalize_block(FACE_START, NUM_FACE_POINTS, 3)

    return vec, origin, scale


def _hand_landmarks_to_xy(hand_landmarks, aspect=1.0):
    return np.array([[lm.x * aspect, lm.y] for lm in hand_landmarks.landmark])


def _bbox_from_points(points):
    return points[:, 0].min(), points[:, 1].min(), points[:, 0].max(), points[:, 1].max()


def _iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_w, inter_h = max(0.0, inter_x2 - inter_x1), max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 1e-9 else 0.0


def check_hand_mesh_quality(results, aspect=1.0):
    warnings = []
    for hand_name, hand_landmarks in [("Left hand", results.left_hand_landmarks), ("Right hand", results.right_hand_landmarks)]:
        if hand_landmarks is None:
            continue
        points = _hand_landmarks_to_xy(hand_landmarks, aspect)
        bbox_w = points[:, 0].max() - points[:, 0].min()
        bbox_h = points[:, 1].max() - points[:, 1].min()
        bbox_area = bbox_w * bbox_h
        if bbox_area < STRICT_MIN_HAND_BBOX_FRACTION:
            warnings.append(f"{hand_name} is very small in frame (~{bbox_area:.3%} of image area).")
        elif bbox_area < MIN_HAND_BBOX_FRACTION:
            warnings.append(f"{hand_name} is small in frame (~{bbox_area:.3%} of image area).")

        segment_lengths = []
        for chain in HAND_FINGER_CHAINS:
            for i in range(len(chain) - 1):
                p1, p2 = points[chain[i]], points[chain[i + 1]]
                segment_lengths.append(np.linalg.norm(p1 - p2))
        segment_lengths = np.array(segment_lengths)
        median_len = np.median(segment_lengths)
        if median_len > 1e-6:
            ratios = segment_lengths / median_len
            if np.any(ratios > SEGMENT_RATIO_WARN) or np.any(ratios < 1.0 / SEGMENT_RATIO_WARN):
                warnings.append(f"{hand_name} mesh looks unreliable — some finger joints are disproportionate.")
    return warnings


def check_self_occlusion(results, aspect=1.0):
    warnings = []
    if results.left_hand_landmarks and results.right_hand_landmarks:
        lp = _hand_landmarks_to_xy(results.left_hand_landmarks, aspect)
        rp = _hand_landmarks_to_xy(results.right_hand_landmarks, aspect)
        iou = _iou(_bbox_from_points(lp), _bbox_from_points(rp))
        if iou > HAND_OVERLAP_WARN_IOU:
            warnings.append(f"POSSIBLE SELF-OCCLUSION: hand boxes overlap significantly (IoU={iou:.2f}).")
    return warnings


def has_valid_hands(results):
    return results.left_hand_landmarks is not None or results.right_hand_landmarks is not None


def has_valid_face(results):
    return results.face_landmarks is not None


def check_pose_visibility(results, threshold=0.5):
    if not results.pose_landmarks:
        return ["NO POSE: pose landmarks missing entirely."]
    lm = results.pose_landmarks.landmark
    vis = [lm[i].visibility for i in SIGNING_RELEVANT_POSE_INDICES]
    avg_vis = sum(vis) / len(vis)
    if avg_vis < threshold:
        return [f"LOW VISIBILITY: avg shoulder/arm visibility {avg_vis:.2f}."]
    return []


def check_blur(frame, hand_bbox_px=None, threshold=80.0):
    if hand_bbox_px is not None:
        x1, y1, x2, y2 = hand_bbox_px
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            return []
        region = frame[y1:y2, x1:x2]
    else:
        region = frame
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var < threshold:
        return [f"BLUR WARNING: sharpness score {lap_var:.1f} is low."]
    return []


def draw_styled_landmarks(image, results):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    if results.face_landmarks:
        mp_drawing.draw_landmarks(
            image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(80, 200, 255), thickness=1, circle_radius=1)
        )


def build_sequence_montage(frames, cols=6, thumb_w=160, thumb_h=120):
    if not frames:
        return None
    n = len(frames)
    rows = (n + cols - 1) // cols
    canvas = np.zeros((rows * thumb_h, cols * thumb_w, 3), dtype=np.uint8)
    for i, f in enumerate(frames):
        r, c = divmod(i, cols)
        thumb = cv2.resize(f, (thumb_w, thumb_h))
        canvas[r * thumb_h:(r + 1) * thumb_h, c * thumb_w:(c + 1) * thumb_w] = thumb
        cv2.putText(canvas, str(i + 1), (c * thumb_w + 4, r * thumb_h + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
    return canvas


def load_session_stats(signer_dir):
    stats_path = os.path.join(signer_dir, '_session_stats.json')
    if os.path.exists(stats_path):
        with open(stats_path, 'r') as f:
            stats = json.load(f)
        last_ts = stats.get('last_updated')
        if last_ts and (time.time() - last_ts) > 6 * 3600:
            print('[NOTICE] Session stats are from a previous session (>6h old).')
        return stats
    return {'count': 0, 'avg_scale': None, 'avg_origin': None, 'last_updated': None}


def save_session_stats(signer_dir, stats):
    stats['last_updated'] = time.time()
    stats_path = os.path.join(signer_dir, '_session_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)


def update_session_stats(stats, origin, scale):
    n = stats['count']
    if n == 0:
        stats['avg_scale'] = float(scale)
        stats['avg_origin'] = origin.tolist()
    else:
        stats['avg_scale'] = (stats['avg_scale'] * n + float(scale)) / (n + 1)
        stats['avg_origin'] = [(stats['avg_origin'][i] * n + float(origin[i])) / (n + 1) for i in range(3)]
    stats['count'] = n + 1
    return stats


def check_drift(stats, origin, scale):
    warnings = []
    if stats['count'] < 3:
        return warnings
    avg_scale = stats['avg_scale']
    scale_diff_pct = abs(scale - avg_scale) / max(avg_scale, 1e-6)
    if scale_diff_pct > SCALE_DRIFT_WARN_PCT:
        direction = 'closer to' if scale > avg_scale else 'farther from'
        warnings.append(f"SCALE DRIFT: appear {direction} camera vs earlier this session ({scale_diff_pct:.0%}).")
    avg_origin = np.array(stats['avg_origin'])
    origin_diff = np.linalg.norm(origin - avg_origin)
    origin_diff_pct = origin_diff / max(avg_scale, 1e-6)
    if origin_diff_pct > ORIGIN_DRIFT_WARN_PCT:
        warnings.append(f"POSITION DRIFT: shoulder position shifted ({origin_diff_pct:.0%} of body scale).")
    return warnings


def load_signer_dataset(mode_root):
    letter_vectors = {}
    if not os.path.isdir(mode_root):
        return letter_vectors
    for letter in os.listdir(mode_root):
        letter_path = os.path.join(mode_root, letter)
        if not os.path.isdir(letter_path):
            continue
        vecs = []
        for fname in os.listdir(letter_path):
            if not fname.endswith('.npy'):
                continue
            arr = np.load(os.path.join(letter_path, fname))
            if arr.ndim == 1:
                vecs.append(arr)
        if vecs:
            letter_vectors[letter] = np.array(vecs)
    return letter_vectors


def check_letter_consistency(mode_root, just_finished_label):
    warnings = []
    all_letters = load_signer_dataset(mode_root)
    if just_finished_label not in all_letters or len(all_letters) < 2:
        return warnings
    this_vecs = all_letters[just_finished_label]
    this_centroid = this_vecs.mean(axis=0)
    internal_spread = np.mean(np.linalg.norm(this_vecs - this_centroid, axis=1))
    other_distances = {}
    for other_label, other_vecs in all_letters.items():
        if other_label == just_finished_label:
            continue
        other_centroid = other_vecs.mean(axis=0)
        other_distances[other_label] = np.linalg.norm(this_centroid - other_centroid)
    if other_distances:
        nearest_label = min(other_distances, key=other_distances.get)
        nearest_dist = other_distances[nearest_label]
        if nearest_dist < internal_spread * 1.3:
            warnings.append(f"POSSIBLE CONFUSION: '{just_finished_label}' close to '{nearest_label}'.")
    all_spreads = []
    for label, vecs in all_letters.items():
        c = vecs.mean(axis=0)
        all_spreads.append(np.mean(np.linalg.norm(vecs - c, axis=1)))
    median_spread = np.median(all_spreads)
    if internal_spread > median_spread * 1.8:
        warnings.append(f"HIGH INTERNAL VARIANCE: '{just_finished_label}' samples inconsistent.")
    return warnings


def check_stillness(cap, aspect_getter, expected_static=True):
    positions = []
    for _ in range(STILLNESS_CHECK_FRAMES):
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)
        if has_valid_hands(results) and results.pose_landmarks:
            raw_vec = extract_keypoints(results)
            fw, fh = aspect_getter()
            norm_vec, _, _ = normalize_vector(raw_vec, fw, fh)
            positions.append(norm_vec[LH_START:RH_START + RH_LEN])
        time.sleep(0.03)
    if len(positions) < 2:
        return []
    movements = [np.linalg.norm(positions[i] - positions[i - 1]) for i in range(1, len(positions))]
    max_movement = max(movements)
    warnings = []
    if expected_static and max_movement > STILLNESS_MOVEMENT_THRESHOLD:
        warnings.append(f"MOTION DETECTED: movement={max_movement:.3f} (scale-normalized).")
    return warnings


def list_camera_names():
    try:
        from pygrabber.dshow_graph import FilterGraph
        graph = FilterGraph()
        return graph.get_input_devices()
    except Exception:
        return None


def select_camera():
    names = list_camera_names()
    if names:
        print('\nAvailable cameras:')
        for i, name in enumerate(names):
            print(f'  [{i}] {name}')
        while True:
            choice = input('Select a camera by number: ').strip()
            if choice.isdigit() and int(choice) < len(names):
                idx = int(choice)
                return idx, names[idx]
            print('Invalid choice, try again.')
    else:
        print('\n[INFO] Falling back to visual preview for camera selection.\n')
        idx = 0
        while True:
            cap_test = cv2.VideoCapture(idx)
            if not cap_test.isOpened():
                cap_test.release()
                if idx == 0:
                    print('[CRITICAL ERROR] No camera found at all. Exiting.')
                    exit()
                print('No more cameras detected.')
                idx = 0
                continue
            ret, frame = cap_test.read()
            if ret:
                label = f'Camera index {idx}'
                cv2.putText(frame, f'{label}  |  [Y] use this  [N] next  [Q] quit', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow('Camera Preview - identify your camera', frame)
                key = cv2.waitKey(0) & 0xFF
                cap_test.release()
                cv2.destroyWindow('Camera Preview - identify your camera')
                if key in (ord('y'), ord('Y')):
                    return idx, label
                elif key in (ord('q'), ord('Q')):
                    exit()
                else:
                    idx += 1
            else:
                cap_test.release()
                idx += 1


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def save_sample_with_metadata(base_dir, sample_num, data, camera_name, frame_width, frame_height, origin, scale, hand_refined):
    file_path = os.path.join(base_dir, f'{sample_num}.npy')
    np.save(file_path, data)
    meta_path = os.path.join(base_dir, f'{sample_num}_meta.json')
    with open(meta_path, 'w') as f:
        json.dump({
            'camera_name': camera_name,
            'frame_width': frame_width,
            'frame_height': frame_height,
            'aspect_ratio': round(frame_width / frame_height, 4),
            'origin': origin.tolist(),
            'scale': float(scale),
            'hand_landmarks_refined_via_zoom': hand_refined,
            'timestamp': time.time(),
        }, f, indent=2)
    return file_path


def save_cvat_export_frame(export_dir, label, sample_num, frame_bgr, keypoints=None):
    label_dir = ensure_dir(os.path.join(export_dir, label))
    img_path = os.path.join(label_dir, f'{sample_num:06d}.jpg')
    cv2.imwrite(img_path, frame_bgr)
    if EXPORT_CVAT_KEYPOINT_JSON and keypoints is not None:
        ann_path = os.path.join(label_dir, f'{sample_num:06d}.json')
        payload = {'label': label, 'sample': sample_num, 'keypoints': keypoints.tolist() if hasattr(keypoints, 'tolist') else keypoints}
        with open(ann_path, 'w') as f:
            json.dump(payload, f)
    return img_path


def main():
    print('--- ISL DATA ENGINE v10 (pose + hands + optional face, CVAT-ready) ---')
    mode = input("Select collection mode ('static' or 'dynamic'): ").strip().lower()
    if mode not in ['static', 'dynamic']:
        print('[CRITICAL ERROR] Invalid mode selection. Exiting.')
        return

    labels_input = input('Enter labels separated by commas (e.g., A,B,C or Hello,Thanks): ').strip()
    labels_to_process = [l.strip() for l in labels_input.split(',') if l.strip()]
    signer_id = input('Enter signer ID (e.g., signer_1): ').strip() or 'signer_unknown'

    camera_index, camera_name = select_camera()
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f'[CRITICAL ERROR] Failed to access camera: {camera_name}')
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAPTURE_FPS)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'[CONFIG] Requested {CAPTURE_WIDTH}x{CAPTURE_HEIGHT}@{CAPTURE_FPS}fps, got {actual_w}x{actual_h}@{actual_fps:.1f}fps')
    print(f"\nUsing camera: {camera_name}. Press 'q' inside the window to exit completely.\n")
    time.sleep(1)

    session_log = []

    def cleanup():
        cap.release()
        cv2.destroyAllWindows()

    try:
        for current_label in labels_to_process:
            print(f"\n=========================================\n[ACTIVE BATCH] '{current_label}' (signer: {signer_id})\n=========================================")

            base_dir = ensure_dir(os.path.join(OUTPUT_ROOT, mode, signer_id, current_label))
            signer_dir = ensure_dir(os.path.join(OUTPUT_ROOT, mode, signer_id))
            session_stats = load_session_stats(signer_dir)
            export_dir = ensure_dir(os.path.join(OUTPUT_ROOT, mode, signer_id, CVAT_EXPORT_SUBDIR))

            total_loops = STATIC_TARGET_SAMPLES if mode == 'static' else DYNAMIC_TARGET_SEQUENCES
            existing_indices = [int(os.path.splitext(f)[0]) for f in os.listdir(base_dir) if f.endswith('.npy') and os.path.splitext(f)[0].isdigit()]
            start_idx = (max(existing_indices) + 1) if existing_indices else 0
            target_end_idx = start_idx + total_loops
            sample_num = start_idx

            while sample_num < target_end_idx:
                print(f"\n[SAMPLE PROGRESS] Sample {sample_num + 1} (target {sample_num - start_idx + 1}/{total_loops}) for '{current_label}'")

                lead_in_start = time.time()
                lead_in_duration = 2.0
                while time.time() - lead_in_start < lead_in_duration:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame = cv2.flip(frame, 1)
                    time_remaining = max(0.0, lead_in_duration - (time.time() - lead_in_start))
                    cv2.putText(frame, f'LABEL: {current_label} | SAMPLE: {sample_num} | CAM: {camera_name}', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, f'GET READY: {time_remaining:.1f}s', (15, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2, cv2.LINE_AA)
                    cv2.imshow('ISL Data Engine v10', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print('Execution killed by user request.')
                        cleanup()
                        return

                capture_success = False
                temp_data_store = None
                preview_frame = None
                zoom_panel = None
                sample_warnings = []
                frame_w = actual_w
                frame_h = actual_h
                hand_was_refined = False
                frame_for_export = None

                if mode == 'static':
                    sample_warnings.extend(check_stillness(cap, aspect_getter=lambda: (frame_w, frame_h), expected_static=True))

                    ret, frame = cap.read()
                    if ret:
                        frame = cv2.flip(frame, 1)
                        frame_h, frame_w = frame.shape[0], frame.shape[1]
                        aspect = frame_w / frame_h
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = holistic.process(image)

                        hands_ok = has_valid_hands(results)
                        face_ok = has_valid_face(results) if REQUIRE_FACE_FOR_STATIC else True

                        if hands_ok and face_ok:
                            refined_lh, refined_rh = refine_hand_landmarks(frame, results, frame_w, frame_h)
                            hand_was_refined = (refined_lh is not None) or (refined_rh is not None)

                            raw_vec = extract_keypoints(results, override_lh=refined_lh, override_rh=refined_rh)
                            norm_vec, origin, scale = normalize_vector(raw_vec, frame_w, frame_h)

                            sample_warnings.extend(check_drift(session_stats, origin, scale))
                            sample_warnings.extend(check_hand_mesh_quality(results, aspect))
                            sample_warnings.extend(check_pose_visibility(results))
                            sample_warnings.extend(check_self_occlusion(results, aspect))
                            if not has_valid_face(results):
                                sample_warnings.append('No face detected — face landmarks zero-filled (face is optional).')
                            if hand_was_refined:
                                sample_warnings.append('Hand landmark x,y refined via zoomed re-detection (z kept from original).')

                            hand_lm = results.right_hand_landmarks or results.left_hand_landmarks
                            if hand_lm:
                                pts_px = np.array([[lm.x * frame_w, lm.y * frame_h] for lm in hand_lm.landmark])
                                x1, y1 = int(pts_px[:, 0].min()) - 20, int(pts_px[:, 1].min()) - 20
                                x2, y2 = int(pts_px[:, 0].max()) + 20, int(pts_px[:, 1].max()) + 20
                                sample_warnings.extend(check_blur(frame, hand_bbox_px=(x1, y1, x2, y2)))

                            temp_data_store = norm_vec
                            frame_for_export = frame.copy()
                            draw_styled_landmarks(frame, results)
                            preview_frame = frame.copy()
                            zoom_panel = build_review_zoom_panel(preview_frame, results, frame_w, frame_h)
                            capture_success = True
                        else:
                            reason = []
                            if not hands_ok:
                                reason.append('no hands detected')
                            print(f"[VALIDATION WARNING] {' and '.join(reason)}. Retrying sample...")
                            cv2.putText(frame, 'DETECTION FAILED - RETRYING', (15, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                            cv2.imshow('ISL Data Engine v10', frame)
                            cv2.waitKey(1000)
                            continue

                else:
                    sequence_buffer = []
                    preview_frames = []
                    valid_frame_count = 0
                    sequence_start_time = time.time()
                    seq_origins, seq_scales = [], []
                    export_frames = []

                    print(f"[LOG] >>> RECORDING NOW for '{current_label}' <<<")
                    for frame_idx in range(SEQUENCE_LENGTH):
                        start_frame_time = time.time()
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frame = cv2.flip(frame, 1)
                        frame_h, frame_w = frame.shape[0], frame.shape[1]
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = holistic.process(image)
                        draw_styled_landmarks(frame, results)
                        raw_vec = extract_keypoints(results)
                        norm_vec, origin, scale = normalize_vector(raw_vec, frame_w, frame_h)

                        sequence_buffer.append(norm_vec)
                        preview_frames.append(frame.copy())
                        seq_origins.append(origin)
                        seq_scales.append(scale)
                        export_frames.append(frame.copy())

                        if has_valid_hands(results):
                            valid_frame_count += 1

                        cv2.putText(frame, f'RECORDING | FRAME {frame_idx + 1}/{SEQUENCE_LENGTH}', (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
                        cv2.imshow('ISL Data Engine v10', frame)
                        cv2.waitKey(1)

                        elapsed = time.time() - start_frame_time
                        if elapsed < FRAME_DELAY:
                            time.sleep(FRAME_DELAY - elapsed)

                    actual_duration = time.time() - sequence_start_time
                    expected_duration = SEQUENCE_LENGTH * FRAME_DELAY
                    if actual_duration > expected_duration * 1.25:
                        sample_warnings.append(f'TIMING WARNING: sequence ran {actual_duration:.2f}s.')

                    temp_data_store = np.array(sequence_buffer)
                    origin = np.median(np.stack(seq_origins), axis=0) if seq_origins else np.zeros(3)
                    scale = float(np.median(seq_scales)) if seq_scales else 1.0
                    valid_ratio = valid_frame_count / SEQUENCE_LENGTH if SEQUENCE_LENGTH else 0
                    if len(sequence_buffer) == SEQUENCE_LENGTH and valid_ratio >= MIN_VALID_FRAME_RATIO:
                        preview_frame = build_sequence_montage(preview_frames)
                        capture_success = True
                    else:
                        print(f"[VALIDATION WARNING] Sequence rejected — hands detected in only {valid_frame_count}/{SEQUENCE_LENGTH} frames. Resetting...")
                        continue

                if capture_success:
                    decision_made = False
                    while not decision_made:
                        display_frame = preview_frame.copy()
                        bar_h = 50 + (20 * len(sample_warnings))
                        bar_y = display_frame.shape[0] - bar_h
                        cv2.rectangle(display_frame, (10, bar_y), (display_frame.shape[1] - 10, display_frame.shape[0] - 10), (0, 0, 0), -1)

                        for i, w in enumerate(sample_warnings):
                            cv2.putText(display_frame, f'[!] {w[:90]}', (20, bar_y + 20 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1, cv2.LINE_AA)

                        cv2.putText(display_frame, '[SPACE] Accept & Save  |  [R] Reject & Retake', (20, display_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                        cv2.imshow('ISL Data Engine v10', display_frame)

                        if zoom_panel is not None:
                            cv2.imshow('Zoomed Hand View - check alignment here', zoom_panel)

                        if sample_warnings:
                            print('[QUALITY WARNINGS - for your judgment, not auto-rejected]')
                            for w in sample_warnings:
                                print(f'  [!] {w}')

                        key = cv2.waitKey(0) & 0xFF
                        if key == ord(' '):
                            file_path = save_sample_with_metadata(base_dir, sample_num, temp_data_store, camera_name, frame_w, frame_h, origin, scale, hand_was_refined)
                            print(f'[FILE SYSTEM] Saved sample {sample_num} to {file_path}')

                            if mode == 'static':
                                session_stats = update_session_stats(session_stats, origin, scale)
                                save_session_stats(signer_dir, session_stats)

                            if EXPORT_CVAT_FRAMES:
                                if mode == 'static' and frame_for_export is not None:
                                    save_cvat_export_frame(export_dir, current_label, sample_num, frame_for_export, keypoints=temp_data_store)
                                elif mode == 'dynamic':
                                    seq_dir = ensure_dir(os.path.join(export_dir, current_label, f'{sample_num:06d}'))
                                    for i, fr in enumerate(export_frames):
                                        cv2.imwrite(os.path.join(seq_dir, f'{i:03d}.jpg'), fr)
                                    with open(os.path.join(seq_dir, 'sequence_meta.json'), 'w') as f:
                                        json.dump({'label': current_label, 'sample': sample_num, 'frames': len(export_frames)}, f, indent=2)

                            session_log.append({'label': current_label, 'sample': sample_num, 'warnings': sample_warnings})
                            sample_num += 1
                            decision_made = True
                        elif key in (ord('r'), ord('R')):
                            print('[MANUAL REJECTION] Sample dropped. Retaking...')
                            decision_made = True
                        elif key == ord('q'):
                            print('Execution killed inside confirmation loop.')
                            cleanup()
                            return

                    if zoom_panel is not None:
                        cv2.destroyWindow('Zoomed Hand View - check alignment here')

            print(f"[SUCCESS] Finished quota for '{current_label}'")

            if mode == 'static':
                consistency_warnings = check_letter_consistency(os.path.join(OUTPUT_ROOT, mode, signer_id), current_label)
                if consistency_warnings:
                    print(f"\n[POST-BATCH SANITY CHECK] '{current_label}':")
                    for w in consistency_warnings:
                        print(f'  [!] {w}')
                else:
                    print(f"[POST-BATCH SANITY CHECK] '{current_label}': no issues flagged.")

        print('\n=========================================\n[SESSION COMPLETE]\n=========================================')
        flagged = [entry for entry in session_log if entry['warnings']]
        print(f'Total samples saved this session: {len(session_log)}')
        print(f'Saved samples that carry warnings (accepted manually despite them): {len(flagged)}')
        if flagged:
            print('\nFlagged samples (worth a manual second look before training):')
            for entry in flagged:
                print(f"  {entry['label']} / sample {entry['sample']}:")
                for w in entry['warnings']:
                    print(f'    - {w}')

        log_path = os.path.join(OUTPUT_ROOT, mode, signer_id, f"_session_log_{int(time.time())}.json")
        with open(log_path, 'w') as f:
            json.dump(session_log, f, indent=2)
        print(f"\nSession log saved to: {log_path}")

    finally:
        cleanup()


if __name__ == '__main__':
    main()