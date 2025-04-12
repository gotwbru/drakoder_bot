# 📊 Dashboard de Pedidos - WhatsApp

Este é um projeto de dashboard interativo para acompanhamento de solicitações e respostas comerciais feitas via WhatsApp. Desenvolvido em **Python + Streamlit**, com visual personalizado inspirado no mascote do sistema: um dragão verdinho empurrando um carrinho do WhatsApp 🐉🛂

## 📊 Funcionalidades
- Importa dados diretamente do banco de dados MySQL (Railway)
- Apresenta métricas e gráficos por:
  - Dia, Loja, Comprador, Motivo e Status
- Destaques visuais com cores baseadas no mascote oficial
- Interface leve, responsiva e organizada em abas:
  - **Solicitações**: Filtro por loja e comprador, tabela e gráficos
  - **Respostas**: Lista e top 5 respondentes
  - **Análises Estratégicas**: Tempo de resposta, % respondido, lojas e motivos mais frequentes

## 🌐 Acesse o Dashboard Online
Acesse a versão ao vivo na nuvem:
👉 [https://drakoderbot.streamlit.app/](https://drakoderbot.streamlit.app/)

## 🚀 Tecnologias utilizadas
- [Streamlit](https://streamlit.io/) — para o frontend interativo
- [Python 3.12](https://www.python.org/)
- [MySQL + Railway](https://railway.app) — para banco de dados na nuvem
- [dotenv](https://pypi.org/project/python-dotenv/) — para gerenciamento de credenciais
- [Pandas](https://pandas.pydata.org/) — para tratamento e análise de dados

## 🎨 Identidade visual
Inspirado no mascote oficial do sistema Dräkorder:

**Cores principais:**
- Verde folha: `#50b13d`
- Verde limão: `#72cb3e`
- Fundo bege claro: `#f5e4c4`

**Cores secundárias:**
- Bege claro: `#fffbe6`
- Preto carvão: `#231f1e`

## 📁 Estrutura
```
|-- drakoder_bot/
|   |-- app.py               # arquivo principal Streamlit
|   |-- .env                # variáveis de ambiente (host, user, password...)
|   |-- requirements.txt    # dependências
```

## 🗒️ Como rodar localmente
```bash
# Clone o repositório
git clone https://github.com/gotwbru/drakoder_bot.git
cd drakoder_bot

# Crie e ative seu ambiente virtual
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Instale as dependências
pip install -r requirements.txt

# Crie um arquivo .env com as credenciais do seu banco:
DB_HOST=seuhost
DB_USER=seuusuario
DB_PASSWORD=suasenha
DB_PORT=3306
DB_NAME=nomedobanco

# Execute o Streamlit
streamlit run app.py
```

## 🎡 Autor
Desenvolvido com carinho por **Bruna Pedroso** 🦊

Se quiser me encontrar:
- GitHub: [@gotwbru](https://github.com/gotwbru)
- LinkedIn: [linkedin.com/in/brunapedroso](https://linkedin.com/in/brunapedroso)

---
Feito com muito dragão e cafeína ☕️🐉

