@echo off
title Iniciar Sistema de Pedidos WhatsApp
color 0A
echo ============================================
echo         INICIANDO SISTEMA DE PEDIDOS        
echo ============================================

REM Iniciar Bot WhatsApp
echo.
echo 🚀 Iniciando Bot do WhatsApp...
start "Bot WhatsApp" cmd /k "node index.js"
timeout /t 2 >nul

REM Iniciar Watcher Python
echo.
echo 🔄 Iniciando Auto Watcher (Python)...
start "Auto Watcher" cmd /k "python auto_watcher.py"
timeout /t 2 >nul

REM Iniciar Dashboard
echo.
echo 📊 Iniciando Dashboard (Streamlit)...
start "Dashboard" cmd /k "streamlit run app.py"
timeout /t 2 >nul

echo.
echo ✅ Todos os componentes foram iniciados.
echo ============================================
pause
