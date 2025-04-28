import streamlit as st
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import re
import unidecode

st.set_page_config(page_title="Dashboard Pedidos WhatsApp", layout="wide")

# Estilo Visual Melhorado
st.markdown("""
    <style>
        body { background-color: #1e1e1e; }
        .main { background-color: #2b2b2b; }
        h1, h2, h3, h4, .stTextInput>label, .stSelectbox>label {
            color: #ffffff;
        }
        .css-10trblm { text-align: center; font-size: 2.5rem; font-weight: bold; color: #ffffff; }
        .block-container { padding-top: 2rem; }

        .stButton>button {
            background-color: #50b13d;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #4CAF50;
            transform: scale(1.05);
        }
        .stMetricLabel, .stMetricValue {
            color: #ffffff;
        }
        .stDataFrame table {
            background-color: white;
        }
        .titulo-notas {
            font-size: 1.2rem;
            color: #ffffff !important;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .stSelectbox label, .stTextInput label {
            color: #ffffff !important;
            font-weight: bold;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #333;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #ffffff;
            padding: 0.5rem;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #50b13d;
            color: #fff;
            border-radius: 8px 8px 0 0;
        }
        .element-container .stPlotlyChart {
            background-color: transparent !important;
        }
    </style>
""", unsafe_allow_html=True)

# Conexão com o banco
load_dotenv()

def conectar():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as err:
        st.error(f"❌ Erro ao conectar ao banco de dados: {err}")
        st.stop()

@st.cache_data(ttl=300)
def carregar_dados():
    conn = conectar()
    solicitacoes = pd.read_sql("SELECT * FROM solicitacoes", conn)
    respostas = pd.read_sql("SELECT * FROM respostas", conn)
    conn.close()
    return solicitacoes, respostas

def padronizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unidecode.unidecode(texto)
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto

# Título com Emoji
st.title("📱 Dashboard de Pedidos - WhatsApp")
st.markdown("---")

# Carregar Dados
df_solic, df_resp = carregar_dados()

if df_solic.empty or df_resp.empty:
    st.warning("⚠️ Alguns dados não foram encontrados no banco.")
    st.stop()

# Padronizar status
df_resp["status"] = df_resp["status"].apply(padronizar_texto).replace({"feito": "Feito"})

# Padronizar nomes
df_resp['respondido_por'] = df_resp['respondido_por'].apply(padronizar_texto).replace({
    'wesley': 'Wesley',
    'wesley flv': 'Wesley',
    'jorge eduardo salvador': 'Jorge',
    'jorge comercial': 'Jorge',
    'andreia': 'Andreia',
    'andreia comercial': 'Andreia',
    'eliane felix': 'Eliane',
    'eliane comercial': 'Eliane',
    'tere': 'Tere'
})

mapa_compradores = {
    "@554799043869": "Andreia Comercial",
    "@554792469843": "Jorge Comercial",
    "@554797424883": "Tere Producao",
    "@554796768889": "Wesley FLV",
    "@554784549969": "Eliane Comercial"
}

df_solic["comprador"] = df_solic["comprador"].str.strip().map(mapa_compradores).fillna(df_solic["comprador"])

def normalizar_loja(valor):
    if isinstance(valor, str):
        match = re.search(r'\d+', valor)
        if match:
            return f'LOJA {int(match.group()):02d}'
    return valor

df_solic['loja'] = df_solic['loja'].apply(normalizar_loja)

df_solic['motivo'] = df_solic['motivo'].apply(padronizar_texto).replace({
    'itens sem pedido': 'item sem pedido',
    'item sem pedido': 'item sem pedido',
    'produto nao encontrado': 'produto nao encontrado',
    'item nao puxando cadastro': 'item nao puxando cadastro'
})

df_solic['data_solicitacao'] = pd.to_datetime(df_solic['data_solicitacao'], errors='coerce')
df_resp['data_resposta'] = pd.to_datetime(df_resp['data_resposta'], errors='coerce')
df_solic['dia'] = df_solic['data_solicitacao'].dt.date

df_merged = df_solic.merge(df_resp, left_on="id", right_on="solicitacao_id", suffixes=("_sol", "_resp"), how="left")
df_merged["tempo_resposta"] = df_merged["data_resposta"] - df_merged["data_solicitacao"]

# Abas com Emojis
aba1, aba2, aba3, aba4 = st.tabs(["📋 Solicitações", "✉️ Respostas", "📊 Análises Estratégicas", "📄 Notas sem Resposta"])

with aba1:
    st.subheader("📋 Solicitações Registradas")
    col1, col2 = st.columns(2)
    loja_filtrada = col1.selectbox("Filtrar por loja", ["Todas"] + sorted(df_solic["loja"].dropna().unique()))
    comprador_filtrado = col2.selectbox("Filtrar por comprador", ["Todos"] + sorted(df_solic["comprador"].dropna().unique()))

    filtro = df_solic.copy()
    if loja_filtrada != "Todas":
        filtro = filtro[filtro["loja"] == loja_filtrada]
    if comprador_filtrado != "Todos":
        filtro = filtro[filtro["comprador"] == comprador_filtrado]

    st.dataframe(filtro.sort_values(by="data_solicitacao", ascending=False))
    st.markdown("### 📈 Gráfico de Solicitações por Motivo")
    st.bar_chart(filtro["motivo"].value_counts())
    st.markdown("### 📆 Gráfico de Solicitações por Dia")
    st.line_chart(df_solic.groupby("dia").size())

with aba2:
    st.subheader("✉️ Respostas Comerciais")
    st.markdown("### 👥 Top 5 que mais responderam")
    st.bar_chart(df_resp["respondido_por"].value_counts().head(5))
    st.dataframe(df_resp)
    st.markdown("### 📊 Gráfico de Status das Respostas")
    st.bar_chart(df_resp["status"].value_counts())

with aba3:
    st.subheader("📊 Métricas e Análises")
    tempo_medio = df_merged["tempo_resposta"].dropna().mean()
    st.metric("⏱ Tempo médio de resposta", str(tempo_medio).split(".")[0] if pd.notna(tempo_medio) else "N/A")
    st.metric("🔴 Solicitações sem resposta", df_merged["data_resposta"].isna().sum())
    st.metric("✅ Percentual respondido", f"{df_merged['data_resposta'].notnull().mean() * 100:.1f}%")
    st.markdown("### 📆 Solicitações por Dia")
    st.line_chart(df_solic.groupby("dia").size())
    st.markdown("### 👑 Top Respondentes")
    st.bar_chart(df_resp["respondido_por"].value_counts())
    st.markdown("### ❗ Motivos mais comuns")
    st.bar_chart(df_solic["motivo"].value_counts())
    st.markdown("### 🏬 Lojas com mais solicitações")
    st.bar_chart(df_solic["loja"].value_counts())

with aba4:
    st.subheader("📄 Notas sem Resposta")
    df_sem_resposta = df_merged[df_merged["data_resposta"].isna()].copy()
    df_sem_resposta["tempo_sem_resposta"] = pd.Timestamp.now() - df_sem_resposta["data_solicitacao"]
    df_sem_resposta["tempo_sem_resposta"] = df_sem_resposta["tempo_sem_resposta"].apply(
        lambda x: f"{x.days} dias e {x.seconds // 3600} horas"
    )
    st.markdown(f"<div class='titulo-notas'>📝 Total de Notas sem Resposta: <strong>{len(df_sem_resposta)}</strong></div>", unsafe_allow_html=True)

    colunas_base = ['nota_fiscal_sol', 'comprador', 'loja', 'data_solicitacao', 'tempo_sem_resposta']
    if 'fornecedor' in df_sem_resposta.columns:
        colunas_base.insert(3, 'fornecedor')
        renomear = {'nota_fiscal_sol': 'Nota Fiscal', 'fornecedor': 'Fornecedor'}
    else:
        renomear = {'nota_fiscal_sol': 'Nota Fiscal'}

    tabela = df_sem_resposta[colunas_base].rename(columns=renomear).sort_values(by="data_solicitacao", ascending=False)
    st.dataframe(tabela, use_container_width=True)

# Rodapé Lateral
st.sidebar.markdown("---")
st.sidebar.caption("✨ Desenvolvido com 💻 por Bruna | 2025")
