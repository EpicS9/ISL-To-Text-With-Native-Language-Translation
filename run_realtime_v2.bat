@echo off
title ISL to Text Translation - V2 Detection Engine
echo =====================================================================
echo  Starting Real-Time ISL Translation Engine V2 (Calibrated) ...
echo =====================================================================
cd /d "%~dp0"

if exist isl_env\Scripts\python.exe (
    isl_env\Scripts\python.exe realtime_isl_translator_v2.py %*
) else (
    python realtime_isl_translator_v2.py %*
)

pause
