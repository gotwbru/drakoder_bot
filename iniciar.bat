@echo off
chcp 65001 >nul
cls
echo ==================================================
echo 🚀 Inicializando Dashboard Pedidos
echo ==================================================

:: Navegar até a pasta do projeto
echo.
echo 📁 Acessando diretório do projeto...
cd /d "C:\Users\bruna\OneDrive\Documentos\PROJETO PEDIDOS\protipo-pedido"
if %errorlevel% neq 0 (
    echo ❌ Erro: Diretório não encontrado.
    pause
    exit /b
)

:: Ativar ambiente virtual
echo.
echo 🐍 Ativando ambiente virtual...
call ".venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo ❌ Erro: Não foi possível ativar o ambiente virtual.
    pause
    exit /b
)

:: Rodar inserção de mensagens no banco
echo.
echo 🗂️ Inserindo novas mensagens no banco de dados...
python inserir_mensagens.py
if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao inserir mensagens no banco.
    pause
    exit /b
)
echo ✅ Mensagens inseridas com sucesso.

:: Rodar auto_watcher.py em paralelo
echo.
echo 🔍 Iniciando Auto Watcher em paralelo...
start cmd /k "python auto_watcher.py"
if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao iniciar Auto Watcher.
    pause
    exit /b
)
echo ✅ Auto Watcher iniciado com sucesso.

:: Rodar o dashboard com Streamlit
echo.
echo 📊 Abrindo Dashboard Streamlit...
start cmd /k "streamlit run app.py"
if %errorlevel% neq 0 (
    echo ❌ Erro: Falha ao abrir Dashboard Streamlit.
    pause
    exit /b
)
echo ✅ Dashboard inicializado com sucesso.

echo.
echo 🎉 Todos os processos foram iniciados!
pause
