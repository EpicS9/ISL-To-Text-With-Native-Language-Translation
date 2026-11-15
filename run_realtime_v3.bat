@echo off
title ISL to Text Translation - V3 Engine (Mode Toggle)
echo =====================================================================
echo  Starting ISL Translation Engine V3 (Decoupled with Mode Toggle) ...
echo  Press TAB or M inside the window to switch Static / Dynamic modes!
echo =====================================================================
cd /d "%~dp0"

if exist isl_env\Scripts\python.exe (
    isl_env\Scripts\python.exe realtime_isl_translator_v3.py %*
) else (
    python realtime_isl_translator_v3.py %*
)

pause
