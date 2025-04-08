# 🐉 Dräkorder WhatsApp Bot

Dräkorder is a lightweight system that automates order registration through WhatsApp. It captures standardized messages from a group, extracts order or response info, stores it in a MySQL database, and displays everything on a Streamlit dashboard.

## 📦 Features
- WhatsApp bot using `whatsapp-web.js` (Node.js)
- Message parsing for order requests and commercial responses
- Database insertion with Python and MySQL
- Interactive dashboard built with Streamlit
- Real-time data monitoring

## 🚀 Getting Started

### Requirements
- Node.js
- Python 3.10+
- MySQL Server

### Installation
Run the setup script:

```bash
bash setup.sh
```

Then start the system:

```bash
iniciar_sistema.bat
```

To stop:

```bash
encerrar_sistema.bat
```

## 📁 Project Structure

- `index.js`: WhatsApp bot
- `auto_watcher.py`: Monitors and sends messages to DB
- `app.py`: Streamlit dashboard
- `mensagens.json`: Temp message storage

## 📌 License
MIT