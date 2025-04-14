
import streamlit as st
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
import re

st.set_page_config(page_title="Dashboard Pedidos WhatsApp", layout="wide")

st.markdown("""
    <style>
        body { background-color: #f5e4c4; }
        .main { background-color: #fffbe6; }
        h1, h2, h3, h4, .stTextInput>label, .stSelectbox>label {
            color: #231f1e;
        }
        .stButton>button {
            background-color: #50b13d;
            color: white;
            border: none;
            border-radius: 6px;
        }
        .stButton>button:hover {
            background-color: #72cb3e;
        }
        .stMetricLabel, .stMetricValue {
            color: #231f1e;
        }
        .stDataFrame table {
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

load_dotenv()

def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def carregar_dados():
    conn = conectar()
    solicitacoes = pd.read_sql("SELECT * FROM solicitacoes", conn)
    respostas = pd.read_sql("SELECT * FROM respostas", conn)
    conn.close()
    return solicitacoes, respostas

st.title("📊 Dashboard de Pedidos - WhatsApp")

df_solic, df_resp = carregar_dados()

# Padronizar nomes de quem respondeu
df_resp['respondido_por'] = df_resp['respondido_por'].replace({
    'Wesley': 'Wesley FLV',
    'Jorge Eduardo Salvador': 'Jorge Comercial'
})

mapa_compradores = {
    "@554799043869": "Andreia Comercial",
    "@554792469843": "Jorge Comercial",
    "@554797424883": "Tere Producao",
    "@554796768889": "Wesley FLV",
    "@554784549969": "Eliane Comercial"
}

df_solic["comprador"] = df_solic["comprador"].str.strip()
df_solic["comprador"] = df_solic["comprador"].map(mapa_compradores).fillna(df_solic["comprador"])

def normalizar_loja(valor):
    if isinstance(valor, str):
        match = re.search(r'\d+', valor)
        if match:
            numero = int(match.group())
            return f'LOJA {numero:02d}'
    return valor

df_solic['loja'] = df_solic['loja'].apply(normalizar_loja)
df_solic['motivo'] = (
    df_solic['motivo']
    .str.strip()
    .str.lower()
    .replace({
        'itens sem pedido': 'item sem pedido',
        'item sem pedido.': 'item sem pedido',
        'produto não encontrado': 'produto nao encontrado',
        'item não puxando cadastro': 'item nao puxando cadastro'
    })
)

df_solic['data_solicitacao'] = pd.to_datetime(df_solic['data_solicitacao'], errors='coerce')
df_resp['data_resposta'] = pd.to_datetime(df_resp['data_resposta'], errors='coerce')
df_solic['dia'] = df_solic['data_solicitacao'].dt.date

df_merged = df_solic.merge(df_resp, left_on="id", right_on="solicitacao_id", suffixes=("_sol", "_resp"), how="left")
df_merged["tempo_resposta"] = df_merged["data_resposta"] - df_merged["data_solicitacao"]

aba1, aba2, aba3 = st.tabs(["Solicitações", "Respostas", "Análises Estratégicas"])

with aba1:
    st.subheader("Solicitações Registradas")

    col1, col2 = st.columns(2)
    with col1:
        lojas = sorted(df_solic["loja"].dropna().unique().tolist()) if not df_solic.empty else []
        loja_filtrada = st.selectbox("Filtrar por loja", options=["Todas"] + lojas)
    with col2:
        compradores = sorted(df_solic["comprador"].dropna().unique().tolist()) if not df_solic.empty else []
        comprador_filtrado = st.selectbox("Filtrar por comprador", options=["Todos"] + compradores)

    filtro = df_solic.copy()
    if loja_filtrada != "Todas":
        filtro = filtro[filtro["loja"] == loja_filtrada]
    if comprador_filtrado != "Todos":
        filtro = filtro[filtro["comprador"] == comprador_filtrado]

    filtro = filtro.sort_values(by="data_solicitacao", ascending=False)
    st.dataframe(filtro)

    st.markdown("### Gráfico de Solicitações por Motivo")
    if not filtro.empty:
        st.bar_chart(filtro["motivo"].value_counts())

    st.markdown("### Gráfico de Solicitações por Dia")
    if "dia" in df_solic:
        st.line_chart(df_solic.groupby("dia").size())

with aba2:
    st.subheader("Respostas Comerciais")

    if "respondido_por" in df_resp.columns:
        st.markdown("### Top 5 que mais responderam")
        top_respondentes = df_resp["respondido_por"].value_counts().head(5)
        st.bar_chart(top_respondentes)

    st.dataframe(df_resp)

    st.markdown("### Gráfico de Status das Respostas")
    if not df_resp.empty:
        st.bar_chart(df_resp["status"].value_counts())

with aba3:
    st.subheader("Métricas e Análises")

    tempo_medio = df_merged["tempo_resposta"].dropna().mean()
    st.metric("⏱ Tempo médio de resposta", str(tempo_medio).split(".")[0] if not pd.isna(tempo_medio) else "N/A")

    sem_resposta = df_merged[df_merged["data_resposta"].isna()]
    st.metric("🔴 Solicitações sem resposta", len(sem_resposta))

    perc = df_merged["data_resposta"].notnull().mean() * 100
    st.metric("✅ Percentual respondido", f"{perc:.1f}%")

    st.markdown("### Solicitações por Dia")
    if "dia" in df_solic:
        st.line_chart(df_solic.groupby("dia").size())

    st.markdown("### Top Respondentes")
    ranking = df_resp["respondido_por"].value_counts()
    st.bar_chart(ranking)

    st.markdown("### Motivos mais comuns")
    motivos = df_solic["motivo"].value_counts()
    st.bar_chart(motivos)

    st.markdown("### Lojas com mais solicitações")
    lojas = df_solic["loja"].value_counts()
    st.bar_chart(lojas)

    # Tabela adicional: Notas sem resposta
    st.markdown("### 📄 Notas sem Resposta")

    df_sem_resposta = df_merged[df_merged['data_resposta'].isna()].copy()
    df_sem_resposta['tempo_sem_resposta'] = pd.Timestamp.now() - df_sem_resposta['data_solicitacao']
    df_sem_resposta['tempo_sem_resposta'] = df_sem_resposta['tempo_sem_resposta'].apply(
        lambda x: f"{x.days} dias e {x.seconds // 3600} horas"
    )

    tabela = df_sem_resposta[[
        'nota_fiscal', 'comprador', 'loja', 'data_solicitacao', 'tempo_sem_resposta'
    ]].sort_values(by='data_solicitacao', ascending=False)

    st.dataframe(tabela)

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard desenvolvido por Bruna 💫")
