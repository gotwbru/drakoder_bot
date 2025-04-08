@echo off
title Reiniciar Sistema de Pedidos WhatsApp
color 0E

echo ============================================
echo       REINICIANDO SISTEMA DE PEDIDOS        
echo ============================================

echo.
echo ⛔ Encerrando processos anteriores...

taskkill /f /im node.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im streamlit.exe >nul 2>&1

timeout /t 2 >nul

echo.
echo 🔁 Reiniciando componentes...

start "Bot WhatsApp" cmd /k "node index.js"
timeout /t 1 >nul

start "Auto Watcher" cmd /k "python auto_watcher.py"
timeout /t 1 >nul

start "Dashboard" cmd /k "streamlit run app.py"
timeout /t 1 >nul

echo.
echo ✅ Sistema reiniciado com sucesso!
echo ============================================
pause
