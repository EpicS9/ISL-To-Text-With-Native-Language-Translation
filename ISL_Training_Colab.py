# ============================================================
# ISL to Text Translation — Full Training Notebook for Google Colab
# ============================================================
# HOW TO USE:
#   1. Upload your entire "data_v1/" folder to Google Drive
#      (e.g., MyDrive/ISL_Dataset/data_v1/)
#   2. Open a new Google Colab notebook
#   3. Copy each cell (separated by # %%) into a separate Colab cell
#   4. Set Runtime → Change runtime type → GPU (T4 or better)
#   5. Run all cells top to bottom
# ============================================================

# %% [markdown]
# # ISL to Text Translation — Training Notebook
# **Trains two models:**
# - `static_model` — classifies static hand signs (single frame)
# - `dynamic_model` — classifies dynamic signs (30-frame sequences)
#
# **Training strategy:**
# - Keras Tuner (Bayesian Optimization) for hyperparameter search
# - Data augmentation (noise, masking, time-warp)
# - Learning rate scheduling + Early stopping
# - Cross-signer evaluation (train on 3, test on 1)

# %% -- CELL 1: Install dependencies --
!pip install keras-tuner --quiet
!pip install seaborn --quiet

# %% -- CELL 2: Mount Google Drive --
from google.colab import drive
drive.mount('/content/drive')

# %% -- CELL 3: Configuration — SET THESE TO MATCH YOUR DRIVE PATH --
import os

# Point this to wherever you uploaded data_v1/ on your Drive
DRIVE_DATA_ROOT = "/content/drive/MyDrive/ISL_Dataset/data_v1"

STATIC_ROOT  = os.path.join(DRIVE_DATA_ROOT, "static")
DYNAMIC_ROOT = os.path.join(DRIVE_DATA_ROOT, "dynamic")

# Where trained models will be saved back to Drive
MODEL_SAVE_DIR = "/content/drive/MyDrive/ISL_Dataset/models"
os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

# Dataset constants — must match isl_data_collector_vfinal.py
SEQUENCE_LENGTH = 30          # frames per dynamic sample

STATIC_FEATURE_DIM  = None    # auto-detected
DYNAMIC_FEATURE_DIM = None    # auto-detected

# Training config
SEED        = 42
TEST_RATIO  = 0.20            # 20% held-out test set (stratified)
VAL_RATIO   = 0.15            # 15% validation from training set
BATCH_SIZE  = 32
MAX_EPOCHS  = 150             # max epochs for final training
TUNER_MAX_TRIALS = 30         # Keras Tuner trials (increase for better search)
TUNER_EXECUTIONS  = 1         # executions per trial

SIGNERS = ["Roopesh", "Sambhram", "Vaidehi", "Vaishnavi"]

print("Config loaded.")
print(f"Static root : {STATIC_ROOT}")
print(f"Dynamic root: {DYNAMIC_ROOT}")
print(f"Model dir   : {MODEL_SAVE_DIR}")

# %% -- CELL 4: Imports --
import numpy as np
import json
import random
import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers, callbacks
import keras_tuner as kt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

np.random.seed(SEED)
tf.random.set_seed(SEED)
random.seed(SEED)

print(f"TensorFlow version : {tf.__version__}")
print(f"GPU available      : {tf.config.list_physical_devices('GPU')}")

# %% -- CELL 5: Data loading utilities --

def load_static_dataset(data_root):
    """
    Loads all static .npy files.
    Returns:
        X       : (N, D)  float32 keypoint vectors
        y       : (N,)    string labels
        signers : (N,)    string signer IDs
    """
    X, y, signers = [], [], []
    if not os.path.isdir(data_root):
        raise FileNotFoundError(f"Static root not found: {data_root}")

    for signer in sorted(os.listdir(data_root)):
        signer_path = os.path.join(data_root, signer)
        if not os.path.isdir(signer_path):
            continue
        for label in sorted(os.listdir(signer_path)):
            label_path = os.path.join(signer_path, label)
            if not os.path.isdir(label_path):
                continue
            for fname in os.listdir(label_path):
                if not fname.endswith('.npy') or not fname[:-4].isdigit():
                    continue
                arr = np.load(os.path.join(label_path, fname))
                if arr.ndim == 1:
                    X.append(arr)
                    y.append(label)
                    signers.append(signer)

    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    signers = np.array(signers)
    print(f"[Static]  Loaded {len(X)} samples | {len(set(y))} classes | shape {X.shape}")
    return X, y, signers


def load_dynamic_dataset(data_root, seq_len=30):
    """
    Loads all dynamic .npy files (shape: seq_len x D).
    Returns:
        X       : (N, seq_len, D)  float32
        y       : (N,)             string labels
        signers : (N,)             string signer IDs
    """
    X, y, signers = [], [], []
    skipped = 0
    if not os.path.isdir(data_root):
        raise FileNotFoundError(f"Dynamic root not found: {data_root}")

    for signer in sorted(os.listdir(data_root)):
        signer_path = os.path.join(data_root, signer)
        if not os.path.isdir(signer_path):
            continue
        for label in sorted(os.listdir(signer_path)):
            label_path = os.path.join(signer_path, label)
            if not os.path.isdir(label_path):
                continue
            for fname in os.listdir(label_path):
                if not fname.endswith('.npy') or not fname[:-4].isdigit():
                    continue
                arr = np.load(os.path.join(label_path, fname))
                if arr.ndim != 2 or arr.shape[0] != seq_len:
                    skipped += 1
                    continue
                X.append(arr)
                y.append(label)
                signers.append(signer)

    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    signers = np.array(signers)
    print(f"[Dynamic] Loaded {len(X)} samples | {len(set(y))} classes | shape {X.shape} | skipped {skipped}")
    return X, y, signers


# Load both datasets
X_static,  y_static,  sig_static  = load_static_dataset(STATIC_ROOT)
X_dynamic, y_dynamic, sig_dynamic = load_dynamic_dataset(DYNAMIC_ROOT, seq_len=SEQUENCE_LENGTH)

STATIC_FEATURE_DIM  = X_static.shape[1]
DYNAMIC_FEATURE_DIM = X_dynamic.shape[2] if X_dynamic.ndim == 3 else None

print(f"\nStatic  feature dim : {STATIC_FEATURE_DIM}")
print(f"Dynamic feature dim : {DYNAMIC_FEATURE_DIM}")

# %% -- CELL 6: Dataset exploration --

def plot_class_distribution(y, title, top_n=50):
    counts = Counter(y)
    labels_sorted = sorted(counts.keys())
    vals = [counts[l] for l in labels_sorted]
    fig, ax = plt.subplots(figsize=(max(12, len(labels_sorted) * 0.45), 4))
    ax.bar(labels_sorted[:top_n], vals[:top_n], color='steelblue')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Class")
    ax.set_ylabel("Sample count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    print(f"  Min samples: {min(vals)} | Max: {max(vals)} | Mean: {np.mean(vals):.1f}")

plot_class_distribution(y_static,  "Static Dataset — Class Distribution")
plot_class_distribution(y_dynamic, "Dynamic Dataset — Class Distribution")

print("\n-- Static signer breakdown --")
for s in sorted(set(sig_static)):
    mask = sig_static == s
    classes = set(y_static[mask])
    print(f"  {s:15s}: {mask.sum():4d} samples | {len(classes):2d} classes")

print("\n-- Dynamic signer breakdown --")
for s in sorted(set(sig_dynamic)):
    mask = sig_dynamic == s
    classes = set(y_dynamic[mask])
    print(f"  {s:15s}: {mask.sum():4d} samples | {len(classes):2d} classes")

# %% -- CELL 7: Preprocessing & splits --

def encode_labels(y):
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    return y_enc, le


def make_splits(X, y_enc, test_ratio=TEST_RATIO, val_ratio=VAL_RATIO, seed=SEED):
    """Stratified train / val / test split."""
    X_tv, X_test, y_tv, y_test = train_test_split(
        X, y_enc, test_size=test_ratio, stratify=y_enc, random_state=seed)
    val_frac = val_ratio / (1.0 - test_ratio)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tv, y_tv, test_size=val_frac, stratify=y_tv, random_state=seed)
    return X_train, X_val, X_test, y_train, y_val, y_test


# -- Static --
y_static_enc, le_static = encode_labels(y_static)
NUM_STATIC_CLASSES = len(le_static.classes_)

X_str_tr, X_str_val, X_str_te, y_str_tr, y_str_val, y_str_te = make_splits(X_static, y_static_enc)

print(f"\n[Static]  Train: {len(X_str_tr)} | Val: {len(X_str_val)} | Test: {len(X_str_te)}")
print(f"          Classes ({NUM_STATIC_CLASSES}): {list(le_static.classes_)}")

# -- Dynamic --
y_dynamic_enc, le_dynamic = encode_labels(y_dynamic)
NUM_DYNAMIC_CLASSES = len(le_dynamic.classes_)

X_dyn_tr, X_dyn_val, X_dyn_te, y_dyn_tr, y_dyn_val, y_dyn_te = make_splits(X_dynamic, y_dynamic_enc)

print(f"\n[Dynamic] Train: {len(X_dyn_tr)} | Val: {len(X_dyn_val)} | Test: {len(X_dyn_te)}")
print(f"          Classes ({NUM_DYNAMIC_CLASSES}): {list(le_dynamic.classes_)}")

# Save label encoders to Drive
np.save(os.path.join(MODEL_SAVE_DIR, "static_label_classes.npy"),  le_static.classes_)
np.save(os.path.join(MODEL_SAVE_DIR, "dynamic_label_classes.npy"), le_dynamic.classes_)
print("\nLabel classes saved.")

# %% -- CELL 8: Data augmentation --

def augment_static(X, y, noise_std=0.005, mask_prob=0.05, n_aug=3):
    """
    Generates augmented copies of static samples:
      - Gaussian noise injection
      - Random feature masking (zero-out random dims)
    """
    X_aug, y_aug = [X], [y]
    rng = np.random.RandomState(SEED)
    for i in range(n_aug):
        noise = rng.normal(0, noise_std, X.shape).astype(np.float32)
        X_noisy = X + noise
        mask = rng.binomial(1, 1 - mask_prob, X.shape).astype(np.float32)
        X_noisy = X_noisy * mask
        X_aug.append(X_noisy)
        y_aug.append(y)
    return np.concatenate(X_aug), np.concatenate(y_aug)


def time_warp(sequence, sigma=0.1, seed=None):
    """Simple time-warp via 1D interpolation on a warped time axis."""
    rng = np.random.RandomState(seed)
    seq_len = sequence.shape[0]
    orig_steps = np.arange(seq_len)
    warp_steps = orig_steps + np.cumsum(rng.normal(0, sigma, seq_len))
    warp_steps -= warp_steps.min()
    warp_steps = warp_steps / warp_steps.max() * (seq_len - 1)
    warped = np.array([
        np.interp(warp_steps, orig_steps, sequence[:, i])
        for i in range(sequence.shape[1])
    ], dtype=np.float32).T
    return warped


def augment_dynamic(X, y, noise_std=0.005, mask_prob=0.03, n_aug=3, warp=True):
    """
    Generates augmented copies of dynamic sequences:
      - Gaussian noise per frame per dimension
      - Feature masking
      - Time warp (optional)
    """
    X_aug, y_aug = [X], [y]
    rng = np.random.RandomState(SEED)
    for aug_idx in range(n_aug):
        X_new = []
        for i, seq in enumerate(X):
            s = seq.copy()
            if warp and rng.rand() > 0.5:
                s = time_warp(s, seed=SEED + aug_idx * 10000 + i)
            noise = rng.normal(0, noise_std, s.shape).astype(np.float32)
            s = s + noise
            mask = rng.binomial(1, 1 - mask_prob, s.shape).astype(np.float32)
            s = s * mask
            X_new.append(s)
        X_aug.append(np.array(X_new, dtype=np.float32))
        y_aug.append(y)
    return np.concatenate(X_aug), np.concatenate(y_aug)


def shuffle_together(X, y, seed=SEED):
    idx = np.random.RandomState(seed).permutation(len(X))
    return X[idx], y[idx]


def get_class_weights(y_enc):
    classes = np.unique(y_enc)
    weights = compute_class_weight('balanced', classes=classes, y=y_enc)
    return dict(zip(classes, weights))


print("Augmenting static training data (3x)...")
X_str_tr_aug, y_str_tr_aug = augment_static(X_str_tr, y_str_tr, n_aug=3)
X_str_tr_aug, y_str_tr_aug = shuffle_together(X_str_tr_aug, y_str_tr_aug)
print(f"  Before: {len(X_str_tr)} | After: {len(X_str_tr_aug)}")

print("Augmenting dynamic training data (3x)...")
X_dyn_tr_aug, y_dyn_tr_aug = augment_dynamic(X_dyn_tr, y_dyn_tr, n_aug=3)
X_dyn_tr_aug, y_dyn_tr_aug = shuffle_together(X_dyn_tr_aug, y_dyn_tr_aug)
print(f"  Before: {len(X_dyn_tr)} | After: {len(X_dyn_tr_aug)}")

static_class_weights  = get_class_weights(y_str_tr_aug)
dynamic_class_weights = get_class_weights(y_dyn_tr_aug)

print("\nAugmentation complete.")

# %% -- CELL 9: Static model builder (Residual Dense MLP) --

def build_static_model(hp):
    """
    Residual Dense network for static keypoint classification.

    Hyperparameters tuned:
      - n_blocks      : number of residual blocks (2-5)
      - stem_units    : size of input projection layer (256-1024)
      - block_i_units : units per residual block (128-768)
      - dropout rates : per-block (0.1-0.5)
      - l2            : L2 weight regularization (1e-5 to 1e-2)
      - lr            : AdamW learning rate (1e-4 to 1e-2)
      - use_batchnorm : whether to use BatchNorm after each layer
    """
    inp = keras.Input(shape=(STATIC_FEATURE_DIM,), name="keypoints")

    n_blocks  = hp.Int("n_blocks", 2, 5, default=3)
    l2_rate   = hp.Float("l2", 1e-5, 1e-2, sampling="log", default=1e-4)
    lr        = hp.Float("lr", 1e-4, 1e-2, sampling="log", default=1e-3)
    use_bn    = hp.Boolean("use_batchnorm", default=True)

    # Stem projection
    x = layers.Dense(
        hp.Int("stem_units", 256, 1024, step=64, default=512),
        kernel_regularizer=regularizers.l2(l2_rate),
        name="stem"
    )(inp)
    if use_bn:
        x = layers.BatchNormalization()(x)
    x = layers.Activation("gelu")(x)
    x = layers.Dropout(hp.Float("stem_dropout", 0.1, 0.4, step=0.05, default=0.2))(x)

    # Residual blocks
    for i in range(n_blocks):
        units   = hp.Int(f"block_{i}_units",   128, 768, step=64, default=256)
        dropout = hp.Float(f"block_{i}_dropout", 0.1, 0.5, step=0.05, default=0.3)

        shortcut = x
        h = layers.Dense(units, kernel_regularizer=regularizers.l2(l2_rate))(x)
        if use_bn:
            h = layers.BatchNormalization()(h)
        h = layers.Activation("gelu")(h)
        h = layers.Dropout(dropout)(h)
        h = layers.Dense(units, kernel_regularizer=regularizers.l2(l2_rate))(h)
        if use_bn:
            h = layers.BatchNormalization()(h)

        # Project shortcut if dimensions differ
        if shortcut.shape[-1] != units:
            shortcut = layers.Dense(units, use_bias=False)(shortcut)

        x = layers.Add()([h, shortcut])
        x = layers.Activation("gelu")(x)

    # Classification head
    x = layers.Dense(128, activation="gelu")(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(NUM_STATIC_CLASSES, activation="softmax", name="predictions")(x)

    model = keras.Model(inp, out)
    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=lr, weight_decay=l2_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


print(f"Static model builder ready.")
print(f"Input: ({STATIC_FEATURE_DIM},) | Output classes: {NUM_STATIC_CLASSES}")

# %% -- CELL 10: Run static hyperparameter search --

static_tuner = kt.BayesianOptimization(
    build_static_model,
    objective=kt.Objective("val_accuracy", direction="max"),
    max_trials=TUNER_MAX_TRIALS,
    executions_per_trial=TUNER_EXECUTIONS,
    overwrite=True,
    directory="/content/drive/MyDrive/ISL_Dataset/tuner",
    project_name="static_model",
    seed=SEED,
)

static_tuner.search_space_summary()

static_tuner.search(
    X_str_tr_aug, y_str_tr_aug,
    validation_data=(X_str_val, y_str_val),
    epochs=80,
    batch_size=BATCH_SIZE,
    class_weight=static_class_weights,
    callbacks=[
        callbacks.EarlyStopping(monitor="val_accuracy", patience=12,
                                restore_best_weights=True, verbose=0),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                    patience=6, min_lr=1e-6, verbose=0),
    ],
    verbose=1,
)

print("\n-- Top 5 static model configurations --")
static_tuner.results_summary(num_trials=5)

# %% -- CELL 11: Train best static model to full convergence --

best_static_hp = static_tuner.get_best_hyperparameters(1)[0]
print("Best static hyperparameters:")
for k, v in best_static_hp.values.items():
    print(f"  {k}: {v}")

static_model = build_static_model(best_static_hp)
static_model.summary()

static_history = static_model.fit(
    X_str_tr_aug, y_str_tr_aug,
    validation_data=(X_str_val, y_str_val),
    epochs=MAX_EPOCHS,
    batch_size=BATCH_SIZE,
    class_weight=static_class_weights,
    callbacks=[
        callbacks.EarlyStopping(monitor="val_accuracy", patience=20,
                                restore_best_weights=True, verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.4,
                                    patience=8, min_lr=1e-7, verbose=1),
        callbacks.ModelCheckpoint(
            filepath=os.path.join(MODEL_SAVE_DIR, "static_model_best.keras"),
            monitor="val_accuracy", save_best_only=True, verbose=1),
    ],
    verbose=1,
)

# %% -- CELL 12: Evaluate static model --

def plot_history(history, title):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.plot(history.history['accuracy'],     label='Train', linewidth=2)
    ax1.plot(history.history['val_accuracy'], label='Val',   linewidth=2)
    ax1.set_title(f"{title} — Accuracy"); ax1.legend(); ax1.set_xlabel("Epoch")
    ax2.plot(history.history['loss'],     label='Train', linewidth=2)
    ax2.plot(history.history['val_loss'], label='Val',   linewidth=2)
    ax2.set_title(f"{title} — Loss"); ax2.legend(); ax2.set_xlabel("Epoch")
    plt.tight_layout(); plt.show()


def plot_confusion(y_true, y_pred, classes, title, figsize=(16, 14)):
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
                xticklabels=classes, yticklabels=classes, ax=ax,
                linewidths=0.3, annot_kws={"size": 7})
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout(); plt.show()


plot_history(static_history, "Static Model")

y_str_pred = np.argmax(static_model.predict(X_str_te, verbose=0), axis=1)
test_acc_static = np.mean(y_str_pred == y_str_te)

print(f"\n[Static] Test Accuracy: {test_acc_static:.4f} ({test_acc_static*100:.2f}%)")
print(classification_report(y_str_te, y_str_pred, target_names=le_static.classes_))
plot_confusion(y_str_te, y_str_pred, le_static.classes_, "Static Model — Test Confusion Matrix")

# %% -- CELL 13: Dynamic model builder (BiLSTM + Temporal Attention) --

def build_dynamic_model(hp):
    """
    Bidirectional LSTM stack with Bahdanau temporal attention.

    Hyperparameters tuned:
      - n_lstm_layers  : number of BiLSTM layers (1-3)
      - lstm_i_units   : LSTM units per layer (64-512)
      - dropout rates  : per-layer (0.0-0.4)
      - recurrent dropout
      - use_cnn_frontend: optional Conv1D pre-processing
      - head_units     : dense classification head (64-512)
      - l2, lr, batchnorm
    """
    inp = keras.Input(shape=(SEQUENCE_LENGTH, DYNAMIC_FEATURE_DIM), name="sequence")

    n_lstm  = hp.Int("n_lstm_layers", 1, 3, default=2)
    l2_rate = hp.Float("l2", 1e-5, 1e-2, sampling="log", default=1e-4)
    lr      = hp.Float("lr", 1e-4, 5e-3, sampling="log", default=5e-4)
    use_bn  = hp.Boolean("use_batchnorm", default=True)

    x = inp

    # Optional Conv1D frontend for local temporal patterns
    if hp.Boolean("use_cnn_frontend", default=False):
        x = layers.Conv1D(
            hp.Int("cnn_filters", 32, 128, step=32, default=64),
            kernel_size=3, padding="same", activation="relu",
            name="cnn_frontend"
        )(x)

    # Stacked Bidirectional LSTMs (all return sequences for attention)
    for i in range(n_lstm):
        units       = hp.Int(f"lstm_{i}_units",       64, 512, step=64, default=256)
        dropout     = hp.Float(f"lstm_{i}_dropout",    0.0, 0.4, step=0.05, default=0.2)
        rec_dropout = hp.Float(f"lstm_{i}_rec_dropout", 0.0, 0.4, step=0.05, default=0.1)

        x = layers.Bidirectional(
            layers.LSTM(units,
                        return_sequences=True,
                        dropout=dropout,
                        recurrent_dropout=rec_dropout,
                        kernel_regularizer=regularizers.l2(l2_rate)),
            name=f"bilstm_{i}"
        )(x)
        if use_bn:
            x = layers.BatchNormalization()(x)

    # Temporal attention pooling
    score   = layers.Dense(1, activation="tanh", name="attn_score")(x)    # (B, T, 1)
    weights = layers.Softmax(axis=1, name="attn_weights")(score)           # (B, T, 1)
    x       = layers.Multiply()([x, weights])                              # (B, T, units)
    x       = layers.Lambda(lambda t: tf.reduce_sum(t, axis=1),
                            name="attn_context")(x)                        # (B, units)

    # Classification head
    head_units = hp.Int("head_units", 64, 512, step=64, default=256)
    head_drop  = hp.Float("head_dropout", 0.1, 0.5, step=0.05, default=0.3)
    x = layers.Dense(head_units, kernel_regularizer=regularizers.l2(l2_rate))(x)
    if use_bn:
        x = layers.BatchNormalization()(x)
    x = layers.Activation("gelu")(x)
    x = layers.Dropout(head_drop)(x)

    out = layers.Dense(NUM_DYNAMIC_CLASSES, activation="softmax", name="predictions")(x)

    model = keras.Model(inp, out)
    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=lr, weight_decay=l2_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


print(f"Dynamic model builder ready.")
print(f"Input: ({SEQUENCE_LENGTH}, {DYNAMIC_FEATURE_DIM}) | Output classes: {NUM_DYNAMIC_CLASSES}")

# %% -- CELL 14: Run dynamic hyperparameter search --

dynamic_tuner = kt.BayesianOptimization(
    build_dynamic_model,
    objective=kt.Objective("val_accuracy", direction="max"),
    max_trials=TUNER_MAX_TRIALS,
    executions_per_trial=TUNER_EXECUTIONS,
    overwrite=True,
    directory="/content/drive/MyDrive/ISL_Dataset/tuner",
    project_name="dynamic_model",
    seed=SEED,
)

dynamic_tuner.search_space_summary()

dynamic_tuner.search(
    X_dyn_tr_aug, y_dyn_tr_aug,
    validation_data=(X_dyn_val, y_dyn_val),
    epochs=80,
    batch_size=BATCH_SIZE,
    class_weight=dynamic_class_weights,
    callbacks=[
        callbacks.EarlyStopping(monitor="val_accuracy", patience=12,
                                restore_best_weights=True, verbose=0),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                    patience=6, min_lr=1e-6, verbose=0),
    ],
    verbose=1,
)

print("\n-- Top 5 dynamic model configurations --")
dynamic_tuner.results_summary(num_trials=5)

# %% -- CELL 15: Train best dynamic model to full convergence --

best_dynamic_hp = dynamic_tuner.get_best_hyperparameters(1)[0]
print("Best dynamic hyperparameters:")
for k, v in best_dynamic_hp.values.items():
    print(f"  {k}: {v}")

dynamic_model = build_dynamic_model(best_dynamic_hp)
dynamic_model.summary()

dynamic_history = dynamic_model.fit(
    X_dyn_tr_aug, y_dyn_tr_aug,
    validation_data=(X_dyn_val, y_dyn_val),
    epochs=MAX_EPOCHS,
    batch_size=BATCH_SIZE,
    class_weight=dynamic_class_weights,
    callbacks=[
        callbacks.EarlyStopping(monitor="val_accuracy", patience=20,
                                restore_best_weights=True, verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.4,
                                    patience=8, min_lr=1e-7, verbose=1),
        callbacks.ModelCheckpoint(
            filepath=os.path.join(MODEL_SAVE_DIR, "dynamic_model_best.keras"),
            monitor="val_accuracy", save_best_only=True, verbose=1),
    ],
    verbose=1,
)

# %% -- CELL 16: Evaluate dynamic model --

plot_history(dynamic_history, "Dynamic Model")

y_dyn_pred = np.argmax(dynamic_model.predict(X_dyn_te, verbose=0), axis=1)
test_acc_dynamic = np.mean(y_dyn_pred == y_dyn_te)

print(f"\n[Dynamic] Test Accuracy: {test_acc_dynamic:.4f} ({test_acc_dynamic*100:.2f}%)")
print(classification_report(y_dyn_te, y_dyn_pred, target_names=le_dynamic.classes_))
plot_confusion(y_dyn_te, y_dyn_pred, le_dynamic.classes_, "Dynamic Model — Test Confusion Matrix")

# %% -- CELL 17: Cross-signer leave-one-out evaluation --
# The hardest test: train on 3 signers, evaluate on the 4th.
# This shows true generalization to unseen signers.

print("=" * 70)
print("CROSS-SIGNER EVALUATION (Leave-One-Signer-Out)")
print("=" * 70)


def cross_signer_eval(X, y_enc, signers_arr, model_builder, hp, le, label=""):
    results = {}
    for test_sig in sorted(set(signers_arr)):
        train_mask = signers_arr != test_sig
        test_mask  = signers_arr == test_sig
        if test_mask.sum() == 0:
            continue
        Xtr, ytr = X[train_mask], y_enc[train_mask]
        Xte, yte = X[test_mask],  y_enc[test_mask]
        cw = get_class_weights(ytr)
        m = model_builder(hp)
        Xtr2, Xval2, ytr2, yval2 = train_test_split(
            Xtr, ytr, test_size=0.15, stratify=ytr, random_state=SEED)
        m.fit(Xtr2, ytr2, validation_data=(Xval2, yval2),
              epochs=80, batch_size=BATCH_SIZE, class_weight=cw,
              callbacks=[
                  callbacks.EarlyStopping(monitor="val_loss", patience=15,
                                          restore_best_weights=True, verbose=0),
                  callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                                              patience=6, verbose=0),
              ], verbose=0)
        preds = np.argmax(m.predict(Xte, verbose=0), axis=1)
        acc   = np.mean(preds == yte)
        results[test_sig] = acc
        print(f"  Hold-out signer: {test_sig:15s} | Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    mean_acc = np.mean(list(results.values()))
    print(f"\n  Mean cross-signer accuracy ({label}): {mean_acc:.4f} ({mean_acc*100:.2f}%)")
    return results


print("\n-- Static model — cross-signer --")
cs_static = cross_signer_eval(
    X_static, y_static_enc, sig_static,
    build_static_model, best_static_hp, le_static, label="Static")

print("\n-- Dynamic model — cross-signer --")
cs_dynamic = cross_signer_eval(
    X_dynamic, y_dynamic_enc, sig_dynamic,
    build_dynamic_model, best_dynamic_hp, le_dynamic, label="Dynamic")

# %% -- CELL 18: Per-class accuracy charts --

def plot_per_class_accuracy(y_true, y_pred, classes, title):
    per_class = {}
    for cls_idx, cls_name in enumerate(classes):
        mask = y_true == cls_idx
        if mask.sum() == 0:
            continue
        per_class[cls_name] = np.mean(y_pred[mask] == cls_idx)
    sorted_cls = sorted(per_class.items(), key=lambda x: x[1])
    names  = [c[0] for c in sorted_cls]
    accs   = [c[1] for c in sorted_cls]
    colors = ["#e74c3c" if a < 0.5 else "#f39c12" if a < 0.8 else "#2ecc71" for a in accs]
    fig, ax = plt.subplots(figsize=(max(10, len(names) * 0.45), 5))
    ax.barh(names, accs, color=colors)
    ax.axvline(0.8, color='gray', linestyle='--', label='80% threshold')
    ax.set_xlim(0, 1.05); ax.set_xlabel("Accuracy")
    ax.set_title(title, fontsize=13, fontweight='bold'); ax.legend()
    plt.tight_layout(); plt.show()
    low = [(n, a) for n, a in sorted_cls if a < 0.8]
    if low:
        print("Classes below 80% accuracy:")
        for n, a in low:
            print(f"    {n}: {a*100:.1f}%")

plot_per_class_accuracy(y_str_te, y_str_pred,  le_static.classes_,  "Static  — Per-class Accuracy")
plot_per_class_accuracy(y_dyn_te, y_dyn_pred,  le_dynamic.classes_, "Dynamic — Per-class Accuracy")

# %% -- CELL 19: Save final models + metadata --

# Save Keras format
static_model.save(os.path.join(MODEL_SAVE_DIR, "isl_static_model_final.keras"))
dynamic_model.save(os.path.join(MODEL_SAVE_DIR, "isl_dynamic_model_final.keras"))


# TFLite export (for mobile/edge deployment)
def export_tflite(model, path):
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    with open(path, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite saved: {path} ({len(tflite_model)/1024:.1f} KB)")

export_tflite(static_model,  os.path.join(MODEL_SAVE_DIR, "isl_static_model.tflite"))
export_tflite(dynamic_model, os.path.join(MODEL_SAVE_DIR, "isl_dynamic_model.tflite"))

# Save training metadata
meta = {
    "static": {
        "feature_dim":   int(STATIC_FEATURE_DIM),
        "num_classes":   int(NUM_STATIC_CLASSES),
        "classes":       list(le_static.classes_),
        "test_accuracy": float(test_acc_static),
        "cross_signer":  {k: float(v) for k, v in cs_static.items()},
        "best_hp":       best_static_hp.values,
    },
    "dynamic": {
        "feature_dim":    int(DYNAMIC_FEATURE_DIM),
        "sequence_length": int(SEQUENCE_LENGTH),
        "num_classes":    int(NUM_DYNAMIC_CLASSES),
        "classes":        list(le_dynamic.classes_),
        "test_accuracy":  float(test_acc_dynamic),
        "cross_signer":   {k: float(v) for k, v in cs_dynamic.items()},
        "best_hp":        best_dynamic_hp.values,
    },
}
with open(os.path.join(MODEL_SAVE_DIR, "training_metadata.json"), "w") as f:
    json.dump(meta, f, indent=2)

print("\n" + "=" * 60)
print("TRAINING COMPLETE — FINAL SUMMARY")
print("=" * 60)
print(f"Static  model test accuracy  : {test_acc_static*100:.2f}%")
print(f"Dynamic model test accuracy  : {test_acc_dynamic*100:.2f}%")
print(f"Static  cross-signer mean    : {np.mean(list(cs_static.values()))*100:.2f}%")
print(f"Dynamic cross-signer mean    : {np.mean(list(cs_dynamic.values()))*100:.2f}%")
print(f"\nFiles saved to: {MODEL_SAVE_DIR}")
print("  - isl_static_model_final.keras")
print("  - isl_dynamic_model_final.keras")
print("  - isl_static_model.tflite")
print("  - isl_dynamic_model.tflite")
print("  - static_label_classes.npy")
print("  - dynamic_label_classes.npy")
print("  - training_metadata.json")
print("=" * 60)
