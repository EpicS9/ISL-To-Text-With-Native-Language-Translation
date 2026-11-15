import os
import shutil
import random
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_ROOT = Path("data_v1/static")
OUTPUT_ROOT = Path("image_splits")

SIGNERS = [
    "Roopesh",
    "Sambhram",
    "Vaidehi",
    "Vaishnavi"
]

TEST_RATIO = 0.20
SEED = 42

random.seed(SEED)

# ============================================================
# CLEAN OLD SPLIT
# ============================================================

if OUTPUT_ROOT.exists():
    print("Removing previous image_splits folder...")
    shutil.rmtree(OUTPUT_ROOT)

# ============================================================
# COUNTERS
# ============================================================

total_images = 0
total_train = 0
total_test = 0

# ============================================================
# PROCESS EACH SIGNER
# ============================================================

for signer in SIGNERS:

    signer_path = SOURCE_ROOT / signer

    if not signer_path.exists():
        print(f"[WARNING] Signer folder not found: {signer_path}")
        continue

    print(f"\nProcessing: {signer}")

    # Find every JPG/JPEG recursively
    image_files = []

    for ext in ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG"):
        image_files.extend(signer_path.rglob(ext))

    # --------------------------------------------------------
    # Group images by letter
    # --------------------------------------------------------

    letters = {}

    for image_path in image_files:

        # The immediate parent folder should be the letter
        letter = image_path.parent.name.upper()

        # Only accept single-letter folders A-Z
        if len(letter) != 1 or not letter.isalpha():
            continue

        letters.setdefault(letter, []).append(image_path)

    # --------------------------------------------------------
    # Split each letter independently
    # --------------------------------------------------------

    for letter, files in sorted(letters.items()):

        random.shuffle(files)

        total = len(files)

        if total < 2:
            train_files = files
            test_files = []
        else:
            test_count = max(1, round(total * TEST_RATIO))

            test_files = files[:test_count]
            train_files = files[test_count:]

        # Output directories
        train_dir = OUTPUT_ROOT / "train" / signer / letter
        test_dir = OUTPUT_ROOT / "test" / signer / letter

        train_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)

        # ----------------------------------------------------
        # Copy training images
        # ----------------------------------------------------

        for src in train_files:
            dst = train_dir / src.name
            shutil.copy2(src, dst)

        # ----------------------------------------------------
        # Copy test images
        # ----------------------------------------------------

        for src in test_files:
            dst = test_dir / src.name
            shutil.copy2(src, dst)

        total_images += total
        total_train += len(train_files)
        total_test += len(test_files)

        print(
            f"  {letter}: "
            f"{total} total | "
            f"{len(train_files)} train | "
            f"{len(test_files)} test"
        )

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("IMAGE SPLIT COMPLETE")
print("=" * 60)

print(f"Total images : {total_images}")
print(f"Training     : {total_train}")
print(f"Testing      : {total_test}")

if total_images > 0:
    print(f"Train ratio  : {total_train / total_images:.2%}")
    print(f"Test ratio   : {total_test / total_images:.2%}")

print(f"\nOutput folder: {OUTPUT_ROOT.resolve()}")