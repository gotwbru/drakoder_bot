#!/bin/bash

echo "🔧 Installing Node.js dependencies..."
npm install

echo "🐍 Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

echo "📦 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Setup completed. You can now run iniciar_sistema.bat"