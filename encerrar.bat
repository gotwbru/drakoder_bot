@echo off
title Encerrando Sistema de Pedidos WhatsApp
color 0C

echo ============================================
echo        ENCERRANDO SISTEMA DE PEDIDOS        
echo ============================================

echo.
echo ⛔ Encerrando Bot do WhatsApp (node.exe)...
taskkill /f /im node.exe >nul 2>&1

echo ⛔ Encerrando Auto Watcher (python.exe)...
taskkill /f /im python.exe >nul 2>&1

echo ⛔ Encerrando Dashboard (streamlit.exe)...
taskkill /f /im streamlit.exe >nul 2>&1

echo.
echo ✅ Todos os processos foram encerrados com sucesso.
echo ============================================
pause
