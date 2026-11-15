"""
Capture Metadata Audit
========================
Scans every _meta.json sidecar file across your dataset and reports,
per signer, what camera/resolution/aspect-ratio was actually used during
capture. This directly tests whether cross-signer accuracy collapse is
caused by inconsistent capture conditions rather than guessing.

Only samples captured with v9/v10 have _meta.json sidecars. Any sample
WITHOUT one is flagged explicitly — that itself is diagnostic, since it
means that sample was captured with an older script version.

Usage:
    python audit_capture_metadata.py
"""

import os
import json
from collections import defaultdict

DATA_ROOT = "data/static"


def audit():
    if not os.path.isdir(DATA_ROOT):
        print(f"[ERROR] {DATA_ROOT} not found. Run this from your project root.")
        return

    signers = sorted(os.listdir(DATA_ROOT))

    print("=" * 70)
    print("CAPTURE METADATA AUDIT")
    print("=" * 70)

    for signer in signers:
        signer_path = os.path.join(DATA_ROOT, signer)
        if not os.path.isdir(signer_path):
            continue

        print(f"\n{'-' * 70}")
        print(f"SIGNER: {signer}")
        print(f"{'-' * 70}")

        cameras = defaultdict(int)
        resolutions = defaultdict(int)
        aspect_ratios = defaultdict(int)
        letters_missing_meta = defaultdict(int)
        total_samples = 0
        samples_with_meta = 0

        for letter in sorted(os.listdir(signer_path)):
            letter_path = os.path.join(signer_path, letter)
            if not os.path.isdir(letter_path):
                continue

            npy_files = [f for f in os.listdir(letter_path) if f.endswith('.npy')]
            for npy_file in npy_files:
                total_samples += 1
                sample_num = os.path.splitext(npy_file)[0]
                meta_path = os.path.join(letter_path, f"{sample_num}_meta.json")

                if not os.path.exists(meta_path):
                    letters_missing_meta[letter] += 1
                    continue

                samples_with_meta += 1
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                    cameras[meta.get('camera_name', 'UNKNOWN')] += 1
                    res = f"{meta.get('frame_width', '?')}x{meta.get('frame_height', '?')}"
                    resolutions[res] += 1
                    aspect_ratios[meta.get('aspect_ratio', '?')] += 1
                except Exception as e:
                    print(f"  [WARNING] Failed to read {meta_path}: {e}")

        print(f"Total samples: {total_samples}")
        print(f"Samples WITH metadata (v9/v10 capture): {samples_with_meta}")
        print(f"Samples WITHOUT metadata (older script version): {total_samples - samples_with_meta}")

        if letters_missing_meta:
            print(f"\n  Letters with samples missing metadata (captured on an older script):")
            for letter, count in sorted(letters_missing_meta.items()):
                print(f"    {letter}: {count} sample(s) missing metadata")

        if cameras:
            print(f"\n  Cameras used:")
            for cam, count in sorted(cameras.items(), key=lambda x: -x[1]):
                print(f"    '{cam}': {count} samples")

        if resolutions:
            print(f"\n  Resolutions used:")
            for res, count in sorted(resolutions.items(), key=lambda x: -x[1]):
                print(f"    {res}: {count} samples")

        if aspect_ratios:
            print(f"\n  Aspect ratios recorded:")
            for ar, count in sorted(aspect_ratios.items(), key=lambda x: -x[1]):
                print(f"    {ar}: {count} samples")

        # Flag inconsistency within this single signer, not just across signers
        if len(cameras) > 1:
            print(f"\n  [FLAG] This signer used MORE THAN ONE camera across their samples.")
        if len(resolutions) > 1:
            print(f"  [FLAG] This signer's samples were captured at MORE THAN ONE resolution.")

    print(f"\n{'=' * 70}")
    print("CROSS-SIGNER COMPARISON")
    print(f"{'=' * 70}")
    print("Compare the camera/resolution/aspect-ratio lists above across signers.")
    print("If they differ between signers, or if some signers have samples")
    print("'missing metadata' while others don't, that is strong evidence of")
    print("inconsistent capture conditions — and a likely explanation for")
    print("cross-signer accuracy collapse, separate from any signing-style issue.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    audit()