"""
Builds a completely self-contained portable distribution of ISL Translation Studio.
Creates a zip archive that any friend can extract and double-click to run immediately
on Windows without installing Python or any libraries.
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STAGING_DIR = os.path.join(BASE_DIR, "ISL_Translation_Studio")
ZIP_NAME = "ISL_Translation_Studio.zip"
ZIP_PATH = os.path.join(BASE_DIR, ZIP_NAME)
PYTHON_EMBED_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
DOWNLOAD_ZIP = os.path.join(BASE_DIR, "python-3.10.11-embed-amd64.zip")

# Packages in isl_env not needed at all for server.py or realtime_isl_translator_v3.py
EXCLUDE_DIRS = {
    "__pycache__",
    "fitz",
    "pymupdf",
    "pymupdf-1.28.2.dist-info",
    "pypdf",
    "pypdf-6.20.0.dist-info",
    "docx",
    "python_docx-1.2.0.dist-info",
    "reportlab",
    "reportlab-5.0.1.dist-info",
    "pip",
    "pip-22.3.1.dist-info",
    "setuptools",
    "setuptools-65.5.0.dist-info",
    "wheel",
    "wheel-0.48.0.dist-info",
    "tensorboard",
    "tensorboard-2.13.0.dist-info",
    "tensorboard_data_server",
    "tensorboard_data_server-0.7.2.dist-info",
    "Werkzeug",
    "werkzeug-3.1.9.dist-info",
}

def log(msg):
    print(f"[BUILD] {msg}", flush=True)

def step1_prepare_dirs():
    log(f"Preparing staging directory: {STAGING_DIR}")
    os.makedirs(STAGING_DIR, exist_ok=True)

def step2_setup_embed_python():
    runtime_dir = os.path.join(STAGING_DIR, "runtime")
    os.makedirs(runtime_dir, exist_ok=True)
    
    if not os.path.exists(DOWNLOAD_ZIP):
        log(f"Downloading Python 3.10.11 embeddable from {PYTHON_EMBED_URL}...")
        urllib.request.urlretrieve(PYTHON_EMBED_URL, DOWNLOAD_ZIP)
    else:
        log("Using cached python-3.10.11-embed-amd64.zip")

    if not os.path.exists(os.path.join(runtime_dir, "python.exe")):
        log("Extracting embedded Python to runtime/...")
        with zipfile.ZipFile(DOWNLOAD_ZIP, 'r') as z:
            z.extractall(runtime_dir)

    pth_file = os.path.join(runtime_dir, "python310._pth")
    pth_content = (
        "python310.zip\n"
        ".\n"
        "..\n"
        "Lib\\site-packages\n"
        "import site\n"
    )
    with open(pth_file, "w", encoding="utf-8") as f:
        f.write(pth_content)
    log("Configured python310._pth for site-packages and app root.")

def step3_copy_site_packages():
    src_site_packages = os.path.join(BASE_DIR, "isl_env", "Lib", "site-packages")
    dest_site_packages = os.path.join(STAGING_DIR, "runtime", "Lib", "site-packages")
    log(f"Copying site-packages from {src_site_packages} to {dest_site_packages}...")
    os.makedirs(dest_site_packages, exist_ok=True)

    copied_dirs = 0
    copied_files = 0

    for item in os.listdir(src_site_packages):
        if item.startswith("~") or item.startswith("-"):
            continue
        if item in EXCLUDE_DIRS:
            continue
        
        src_item = os.path.join(src_site_packages, item)
        dest_item = os.path.join(dest_site_packages, item)

        if os.path.exists(dest_item):
            continue

        if os.path.isdir(src_item):
            shutil.copytree(
                src_item,
                dest_item,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
            copied_dirs += 1
        elif os.path.isfile(src_item) and not item.endswith(".pyc"):
            shutil.copy2(src_item, dest_item)
            copied_files += 1

    log(f"Copied {copied_dirs} packages and {copied_files} top-level modules.")

def step4_copy_app_files():
    log("Copying application code, models, and frontend bundle...")
    # App scripts
    shutil.copy2(os.path.join(BASE_DIR, "server.py"), os.path.join(STAGING_DIR, "server.py"))
    shutil.copy2(os.path.join(BASE_DIR, "realtime_isl_translator_v3.py"), os.path.join(STAGING_DIR, "realtime_isl_translator_v3.py"))

    # Models (models_v3)
    dest_models = os.path.join(STAGING_DIR, "models_v3")
    shutil.copytree(os.path.join(BASE_DIR, "models_v3"), dest_models, dirs_exist_ok=True)
    log("Copied models_v3 directory.")

    # Frontend (dist only - no node_modules!)
    dest_frontend_dist = os.path.join(STAGING_DIR, "frontend", "dist")
    shutil.copytree(os.path.join(BASE_DIR, "frontend", "dist"), dest_frontend_dist, dirs_exist_ok=True)
    log("Copied frontend/dist build.")

def step5_create_batch_and_docs():
    log("Creating run scripts and user instructions...")

    run_studio_bat = r"""@echo off
title ISL Translation Studio — Real-Time Web Platform
cd /d "%~dp0"

echo =====================================================================
echo    ISL Translation Studio — Real-Time Web Platform (V3 Parity)
echo    Static Residual Dense MLP (35 Classes) + Dynamic BiLSTM (11 Classes)
echo    DirectShow Native Camera + Authentic V3 HUD + Indian Languages NLP
echo =====================================================================
echo.
echo Starting Web Server on http://127.0.0.1:8000 ...
echo The studio will open automatically in your default browser.
echo Press Ctrl+C in this command window anytime to stop the server.
echo.

:: Automatically open default browser after a brief delay
start "" http://127.0.0.1:8000

:: Run server with portable runtime or fallback
if exist "runtime\python.exe" (
    "runtime\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000
) else if exist "isl_env\Scripts\python.exe" (
    "isl_env\Scripts\python.exe" -m uvicorn server:app --host 127.0.0.1 --port 8000
) else (
    python -m uvicorn server:app --host 127.0.0.1 --port 8000
)

if errorlevel 1 (
    echo.
    echo [ERROR] The server exited with an error.
    echo Please ensure no other app is using port 8000 and try again.
    pause
)
"""
    with open(os.path.join(STAGING_DIR, "run_translation_studio.bat"), "w", encoding="utf-8") as f:
        f.write(run_studio_bat)

    run_hud_bat = r"""@echo off
title ISL Real-Time Translator V3 — Desktop HUD Mode
cd /d "%~dp0"

echo =====================================================================
echo    ISL Real-Time Translator V3 — Desktop OpenCV HUD Mode
echo    Press TAB or M inside the camera window to toggle Static/Dynamic mode.
echo    Press Q inside the camera window to quit.
echo =====================================================================
echo.

if exist "runtime\python.exe" (
    "runtime\python.exe" realtime_isl_translator_v3.py %*
) else if exist "isl_env\Scripts\python.exe" (
    "isl_env\Scripts\python.exe" realtime_isl_translator_v3.py %*
) else (
    python realtime_isl_translator_v3.py %*
)

pause
"""
    with open(os.path.join(STAGING_DIR, "run_realtime_hud.bat"), "w", encoding="utf-8") as f:
        f.write(run_hud_bat)

    readme = r"""=============================================================================
ISL Translation Studio — Portable Edition
=============================================================================

This package is completely standalone and pre-configured.
NO installation or setup is required. You do NOT need to install Python,
TensorFlow, or Node.js — everything is included inside the folder!

-----------------------------------------------------------------------------
HOW TO RUN:
-----------------------------------------------------------------------------
1. Extract this entire zip file to a folder on your computer (e.g. Desktop or C:\).
   IMPORTANT: Do NOT run directly from inside the zip file. Always "Extract All".

2. Double-click "run_translation_studio.bat".

3. A command window will launch the backend server, and your default web browser
   will open automatically to:
   http://127.0.0.1:8000

4. In the browser:
   - Click "Allow" if prompted for camera access.
   - Switch between STATIC (letters/digits) and DYNAMIC (words) modes.
   - Enjoy real-time Indian Sign Language translation into English and Indian languages!

-----------------------------------------------------------------------------
BONUS - DESKTOP HUD MODE:
-----------------------------------------------------------------------------
If you prefer a direct high-speed OpenCV desktop camera window instead of the web UI:
- Double-click "run_realtime_hud.bat".
- Press [TAB] or [M] on your keyboard to switch between Static and Dynamic sign modes.
- Press [Q] to quit.

-----------------------------------------------------------------------------
TROUBLESHOOTING:
-----------------------------------------------------------------------------
- Camera not opening: Ensure no other application (like Zoom, Teams, or another browser
  tab) is currently locking your webcam.
- Port 8000 in use: Close any other web servers running on port 8000.
=============================================================================
"""
    with open(os.path.join(STAGING_DIR, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme)

def step6_verify_portable():
    log("Verifying portable runtime by testing imports and model loading...")
    python_exe = os.path.join(STAGING_DIR, "runtime", "python.exe")
    check_cmd = [
        python_exe,
        "-c",
        "import cv2, mediapipe, tensorflow, fastapi, uvicorn; import server; print('PORTABLE VERIFICATION SUCCESSFUL!')"
    ]
    res = subprocess.run(check_cmd, cwd=STAGING_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        log(f"Verification failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        raise RuntimeError("Portable runtime verification check failed!")
    log("Portable runtime verification check passed with zero errors!")

def step7_create_zip():
    log(f"Creating zip archive at {ZIP_PATH}...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    total_files = 0
    for root, dirs, files in os.walk(STAGING_DIR):
        total_files += len(files)

    log(f"Archiving {total_files} files with Deflate compression...")
    
    # Compress with zipfile
    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        count = 0
        for root, dirs, files in os.walk(STAGING_DIR):
            for file in files:
                abs_file = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file, BASE_DIR)
                zf.write(abs_file, rel_path)
                count += 1
                if count % 2000 == 0:
                    log(f"Compressed {count}/{total_files} files...")

    size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    log(f"Zip created successfully! File size: {size_mb:.1f} MB ({ZIP_PATH})")

if __name__ == "__main__":
    step1_prepare_dirs()
    step2_setup_embed_python()
    step3_copy_site_packages()
    step4_copy_app_files()
    step5_create_batch_and_docs()
    step6_verify_portable()
    step7_create_zip()
    log("ALL STEPS COMPLETED!")
