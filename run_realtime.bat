@echo off
title ISL to Text Translation - Real-time Detection Engine
echo =====================================================================
echo  Starting Real-Time Indian Sign Language Translation Engine...
echo =====================================================================
cd /d "%~dp0"

if exist isl_env\Scripts\python.exe (
    isl_env\Scripts\python.exe realtime_isl_translator.py %*
) else (
    python realtime_isl_translator.py %*
)

pause
