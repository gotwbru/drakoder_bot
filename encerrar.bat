@echo off
chcp 65001 >nul
cls
echo ==================================================
echo 🛑 Encerrando o Projeto - Dashboard Pedidos...
echo ==================================================

:: Encerrar auto_watcher.py e outros scripts Python
echo.
echo ⏳ Encerrando processos Python...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Processos Python encerrados com sucesso.
) else (
    echo ⚠️ Nenhum processo Python encontrado ou falha no encerramento.
)

:: Encerrar Streamlit Dashboard
echo.
echo ⏳ Encerrando Dashboard Streamlit...
taskkill /f /im streamlit.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Dashboard Streamlit encerrado com sucesso.
) else (
    echo ⚠️ Nenhuma instância do Streamlit encontrada ou falha no encerramento.
)

echo.
echo 🎯 Todos os processos foram finalizados.
pause
