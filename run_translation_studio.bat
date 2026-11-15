@echo off
title ISL Translation Studio — V3 Real-Time Platform
echo =====================================================================
echo    ISL Translation Studio — Real-Time Web Platform (V3 Parity)
echo    Static Residual Dense MLP (35 Classes) + Dynamic BiLSTM (11 Classes)
echo    DirectShow Native Camera + Authentic V3 HUD + Indian Languages NLP
echo =====================================================================
echo.
echo Starting Web Server on http://127.0.0.1:8000 ...
echo Press Ctrl+C in this window to stop the server anytime.
echo.

cd /d "%~dp0"

start "" http://127.0.0.1:8000

if exist isl_env\Scripts\python.exe (
    isl_env\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000
) else (
    python -m uvicorn server:app --host 127.0.0.1 --port 8000
)

pause
