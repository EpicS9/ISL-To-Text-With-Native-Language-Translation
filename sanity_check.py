"""
ISL Dataset Sanity Checker (v3)
=================================
Run this any time — after one signer, after all four, doesn't matter.

Deliberately uses a NEAREST-CENTROID classifier, not a neural net:
  - Zero hyperparameters to tune.
  - Runs in seconds, so you can check after every session.
  - This is a diagnostic on your DATA, not a preview of your final model's
    accuracy. A real neural net can learn nonlinear boundaries a simple
    centroid cannot — so treat a bad number here as "worth investigating,"
    and a good number as "no obvious red flag," never as a final verdict.
    The real test is always your Colab-trained model.

NEW IN v3:
  - "Confused with" reporting: for every letter with errors, shows the
    actual wrong predictions (e.g. "I -> mistaken for Z: 18 times"),
    not just an accuracy percentage. This turns "something is broken"
    into "here's specifically what it's being confused with."
  - Dynamic-sequence checking (data/dynamic): same nearest-centroid
    approach applied to flattened 30-frame sequences. Caveat: this
    assumes rough temporal alignment between sequences (same signer
    speed), which flattening does not correct for — treat this as a
    coarser signal than the static check.

Usage:
    python sanity_check.py
"""

import os
import numpy as np
from collections import Counter

STATIC_ROOT = "data/static"
DYNAMIC_ROOT = "data/dynamic"


def load_all_signers_static(data_root):
    """Returns {signer: {letter: (N, D) array}}"""
    dataset = {}
    if not os.path.isdir(data_root):
        return dataset
    for signer in sorted(os.listdir(data_root)):
        signer_path = os.path.join(data_root, signer)
        if not os.path.isdir(signer_path):
            continue
        letters = {}
        for letter in sorted(os.listdir(signer_path)):
            letter_path = os.path.join(signer_path, letter)
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
                letters[letter] = np.array(vecs)
        if letters:
            dataset[signer] = letters
    return dataset


def load_all_signers_dynamic(data_root):
    """Returns {signer: {label: (N, SEQ_LEN*D) array}} — each sequence is
    flattened into one long vector so the same nearest-centroid machinery
    works unchanged. Sequences of inconsistent length are skipped with a
    warning, since flattening requires a fixed length to compare directly."""
    dataset = {}
    skipped = []
    if not os.path.isdir(data_root):
        return dataset, skipped
    for signer in sorted(os.listdir(data_root)):
        signer_path = os.path.join(data_root, signer)
        if not os.path.isdir(signer_path):
            continue
        labels = {}
        for label in sorted(os.listdir(signer_path)):
            label_path = os.path.join(signer_path, label)
            if not os.path.isdir(label_path):
                continue
            vecs = []
            expected_shape = None
            for fname in os.listdir(label_path):
                if not fname.endswith('.npy'):
                    continue
                arr = np.load(os.path.join(label_path, fname))
                if arr.ndim != 2:
                    continue  # not a sequence, skip
                if expected_shape is None:
                    expected_shape = arr.shape
                if arr.shape != expected_shape:
                    skipped.append((signer, label, fname, arr.shape, expected_shape))
                    continue
                vecs.append(arr.flatten())
            if vecs:
                labels[label] = np.array(vecs)
        if labels:
            dataset[signer] = labels
    return dataset, skipped


def nearest_centroid_fit_predict(train_X, train_y, test_X):
    classes = sorted(set(train_y))
    centroids = {}
    for c in classes:
        mask = [y == c for y in train_y]
        centroids[c] = train_X[mask].mean(axis=0)

    preds = []
    for x in test_X:
        dists = {c: np.linalg.norm(x - centroid) for c, centroid in centroids.items()}
        preds.append(min(dists, key=dists.get))
    return preds


def split_train_test(letters_dict, test_fraction=0.25, seed=42):
    rng = np.random.default_rng(seed)
    train_X, train_y, test_X, test_y = [], [], [], []
    for letter, vecs in letters_dict.items():
        idx = np.arange(len(vecs))
        rng.shuffle(idx)
        split_point = max(1, int(len(idx) * (1 - test_fraction)))
        train_idx, test_idx = idx[:split_point], idx[split_point:]
        train_X.extend(vecs[train_idx])
        train_y.extend([letter] * len(train_idx))
        test_X.extend(vecs[test_idx])
        test_y.extend([letter] * len(test_idx))
    return np.array(train_X), train_y, np.array(test_X), test_y


def compute_per_letter_stats(preds, true_y):
    """Returns {letter: {'correct': int, 'total': int, 'accuracy': float,
    'confused_with': Counter of wrong predictions}}"""
    stats = {}
    for p, t in zip(preds, true_y):
        stats.setdefault(t, {"correct": 0, "total": 0, "confused_with": Counter()})
        stats[t]["total"] += 1
        if p == t:
            stats[t]["correct"] += 1
        else:
            stats[t]["confused_with"][p] += 1
    for letter, s in stats.items():
        s["accuracy"] = s["correct"] / s["total"]
    return stats


def print_full_breakdown(stats, indent="    ", confusion_limit=3):
    """Prints every letter's accuracy AND its top wrong predictions,
    worst-accuracy-first. This is the actual diagnostic upgrade over v2."""
    ordered = sorted(stats.items(), key=lambda kv: kv[1]["accuracy"])
    for letter, s in ordered:
        flag = "  <-- CHECK THIS" if s["accuracy"] < 0.5 else ""
        line = f"{indent}{letter}: {s['accuracy']:.2f} ({s['correct']}/{s['total']}){flag}"
        print(line)
        if s["confused_with"]:
            top_confusions = s["confused_with"].most_common(confusion_limit)
            confusion_str = ", ".join(f"'{wrong}' x{count}" for wrong, count in top_confusions)
            print(f"{indent}    -> mistaken for: {confusion_str}")


def report_accuracy(preds, true_y, label=""):
    correct = sum(p == t for p, t in zip(preds, true_y))
    acc = correct / len(true_y) if true_y else 0.0
    print(f"{label} accuracy: {acc:.4f} ({correct}/{len(true_y)})")
    stats = compute_per_letter_stats(preds, true_y)
    print(f"  All {len(stats)} classes (worst first, with confusion detail):")
    print_full_breakdown(stats)
    return acc, stats


def run_static_checks():
    print("=" * 70)
    print("STATIC LETTERS — SANITY CHECK")
    print("=" * 70)

    dataset = load_all_signers_static(STATIC_ROOT)
    if not dataset:
        print("No static data found.")
        return

    signers = list(dataset.keys())
    print(f"\nSigners found: {signers}\n")

    print("-" * 70)
    print("PART 1: Per-signer self-consistency")
    print("-" * 70)
    for signer, letters in dataset.items():
        print(f"\n{signer}: {len(letters)} letters collected: {sorted(letters.keys())}")
        if len(letters) < 2:
            print("  Not enough letters yet to check. Skipping.")
            continue
        train_X, train_y, test_X, test_y = split_train_test(letters)
        if len(test_y) == 0:
            print("  Not enough samples per letter for a test split yet. Skipping.")
            continue
        preds = nearest_centroid_fit_predict(train_X, train_y, test_X)
        report_accuracy(preds, test_y, label="  Self")

    print("\n" + "-" * 70)
    print("PART 2: Cross-signer generalization")
    print("-" * 70)

    if len(signers) < 2:
        print("Only 1 signer collected so far — cross-signer check needs at least 2.")
        return

    all_letter_sets = {s: set(dataset[s].keys()) for s in signers}
    common_letters = set.intersection(*all_letter_sets.values())
    all_letters_seen = set.union(*all_letter_sets.values())
    skipped_letters = all_letters_seen - common_letters

    print(f"\nLetters common to ALL {len(signers)} signers: {sorted(common_letters)}")
    if skipped_letters:
        print(f"Letters SKIPPED (not collected by every signer): {sorted(skipped_letters)}")

    if not common_letters:
        print("No letters in common — nothing to compare.")
        return

    results = []
    letter_agg = {letter: {"correct": 0, "total": 0, "confused_with": Counter()} for letter in common_letters}

    for train_signer in signers:
        for test_signer in signers:
            if train_signer == test_signer:
                continue
            train_X, train_y = [], []
            for letter in common_letters:
                vecs = dataset[train_signer][letter]
                train_X.extend(vecs)
                train_y.extend([letter] * len(vecs))

            test_X, test_y = [], []
            for letter in common_letters:
                vecs = dataset[test_signer][letter]
                test_X.extend(vecs)
                test_y.extend([letter] * len(vecs))

            preds = nearest_centroid_fit_predict(np.array(train_X), train_y, np.array(test_X))
            correct = sum(p == t for p, t in zip(preds, test_y))
            acc = correct / len(test_y)
            results.append((train_signer, test_signer, acc))

            stats = compute_per_letter_stats(preds, test_y)
            print(f"\n  Train={train_signer:12s} Test={test_signer:12s} -> accuracy: {acc:.4f}")
            print_full_breakdown(stats, indent="      ")

            for letter, s in stats.items():
                letter_agg[letter]["correct"] += s["correct"]
                letter_agg[letter]["total"] += s["total"]
                letter_agg[letter]["confused_with"].update(s["confused_with"])

    avg_cross_acc = np.mean([r[2] for r in results])
    print(f"\n{'=' * 70}")
    print(f"  Average cross-signer accuracy (all pairs): {avg_cross_acc:.4f}")
    print(f"{'=' * 70}")

    print(f"\n  Per-letter accuracy AGGREGATED across every signer pair, WITH confusion detail:")
    for letter, s in letter_agg.items():
        s["accuracy"] = s["correct"] / max(s["total"], 1)
    print_full_breakdown(letter_agg, indent="    ")

    print("\n  (This is the single most useful section for deciding what to fix next —")
    print("   look at the 'mistaken for' lines to see if errors are systematic")
    print("   (e.g. always confused with the SAME letter) vs. scattered/random.)")


def run_dynamic_checks():
    print("\n\n" + "=" * 70)
    print("DYNAMIC SIGNS — SANITY CHECK")
    print("=" * 70)
    print("NOTE: sequences are flattened (30 frames x D dims -> one long vector).")
    print("This assumes rough temporal alignment between signers' sequences —")
    print("it does NOT correct for one signer signing faster/slower than another.")
    print("Treat this as a coarser signal than the static check above.\n")

    dataset, skipped = load_all_signers_dynamic(DYNAMIC_ROOT)

    if skipped:
        print(f"[WARNING] {len(skipped)} sequence(s) skipped due to inconsistent shape:")
        for signer, label, fname, shape, expected in skipped[:10]:
            print(f"    {signer}/{label}/{fname}: shape {shape}, expected {expected}")
        if len(skipped) > 10:
            print(f"    ... and {len(skipped) - 10} more")
        print()

    if not dataset:
        print("No dynamic data found (or nothing with consistent shape). Skipping.")
        return

    signers = list(dataset.keys())
    print(f"Signers found: {signers}\n")

    print("-" * 70)
    print("PART 1: Per-signer self-consistency (dynamic)")
    print("-" * 70)
    for signer, labels in dataset.items():
        print(f"\n{signer}: {len(labels)} dynamic labels collected: {sorted(labels.keys())}")
        if len(labels) < 2:
            print("  Not enough labels yet to check. Skipping.")
            continue
        train_X, train_y, test_X, test_y = split_train_test(labels)
        if len(test_y) == 0:
            print("  Not enough samples per label for a test split yet. Skipping.")
            continue
        preds = nearest_centroid_fit_predict(train_X, train_y, test_X)
        report_accuracy(preds, test_y, label="  Self")

    print("\n" + "-" * 70)
    print("PART 2: Cross-signer generalization (dynamic)")
    print("-" * 70)

    if len(signers) < 2:
        print("Only 1 signer collected so far — cross-signer check needs at least 2.")
        return

    all_label_sets = {s: set(dataset[s].keys()) for s in signers}
    common_labels = set.intersection(*all_label_sets.values())
    if not common_labels:
        print("No dynamic labels in common across signers yet — nothing to compare.")
        return

    print(f"\nLabels common to ALL {len(signers)} signers: {sorted(common_labels)}")

    results = []
    for train_signer in signers:
        for test_signer in signers:
            if train_signer == test_signer:
                continue
            train_X, train_y = [], []
            for label in common_labels:
                vecs = dataset[train_signer][label]
                train_X.extend(vecs)
                train_y.extend([label] * len(vecs))

            test_X, test_y = [], []
            for label in common_labels:
                vecs = dataset[test_signer][label]
                test_X.extend(vecs)
                test_y.extend([label] * len(vecs))

            preds = nearest_centroid_fit_predict(np.array(train_X), train_y, np.array(test_X))
            correct = sum(p == t for p, t in zip(preds, test_y))
            acc = correct / len(test_y)
            results.append((train_signer, test_signer, acc))
            stats = compute_per_letter_stats(preds, test_y)
            print(f"\n  Train={train_signer:12s} Test={test_signer:12s} -> accuracy: {acc:.4f}")
            print_full_breakdown(stats, indent="      ")

    avg_cross_acc = np.mean([r[2] for r in results])
    print(f"\n  Average cross-signer accuracy (dynamic, all pairs): {avg_cross_acc:.4f}")


def main():
    run_static_checks()
    run_dynamic_checks()
    print("\n" + "=" * 70)
    print("DONE. Reminder: these are proxy numbers from a zero-hyperparameter")
    print("classifier — a real signal about your DATA, not a preview of your")
    print("final Colab-trained model's accuracy.")
    print("=" * 70)


if __name__ == "__main__":
    main()