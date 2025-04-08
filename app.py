import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

# Função para conectar ao banco de dados
def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='cpd2025',
        database='pedidos_whatsapp'
    )
    
# Função para carregar dados
def carregar_dados():
    conn = conectar()
    solicitacoes = pd.read_sql("SELECT * FROM solicitacoes", conn)
    respostas = pd.read_sql("SELECT * FROM respostas", conn)
    conn.close()
    return solicitacoes, respostas

# Layout do Streamlit
st.set_page_config(page_title="Dashboard Pedidos WhatsApp", layout="wide")
st.title("📊 Dashboard de Pedidos - WhatsApp")

# Carregar dados
df_solic, df_resp = carregar_dados()

# Garantir que data_solicitacao esteja no formato datetime
if 'data_solicitacao' in df_solic.columns:
    df_solic['data_solicitacao'] = pd.to_datetime(df_solic['data_solicitacao'], errors='coerce')
    df_solic['dia'] = df_solic['data_solicitacao'].dt.date

# Tabs
aba1, aba2, aba3 = st.tabs(["Solicitações", "Respostas", "Análises Estratégicas"])

# --- ABA 1: SOLICITAÇÕES ---
with aba1:
    st.subheader("Solicitações Registradas")

    col1, col2 = st.columns(2)
    with col1:
        lojas = sorted(df_solic['loja'].dropna().unique().tolist()) if not df_solic.empty else []
        loja_filtrada = st.selectbox("Filtrar por loja", options=['Todas'] + lojas)
    with col2:
        compradores = sorted(df_solic['comprador'].dropna().unique().tolist()) if not df_solic.empty else []
        comprador_filtrado = st.selectbox("Filtrar por comprador", options=['Todos'] + compradores)

    filtro = df_solic.copy()
    if loja_filtrada != 'Todas':
        filtro = filtro[filtro['loja'] == loja_filtrada]
    if comprador_filtrado != 'Todos':
        filtro = filtro[filtro['comprador'] == comprador_filtrado]

    filtro = filtro.sort_values(by='data_solicitacao', ascending=False)
    st.dataframe(filtro)

    st.markdown("### Gráfico de Solicitações por Motivo")
    if not filtro.empty:
        st.bar_chart(filtro['motivo'].value_counts())

    st.markdown("### Gráfico de Solicitações por Dia")
    if 'dia' in df_solic:
        st.line_chart(df_solic.groupby('dia').size())

# --- ABA 2: RESPOSTAS ---
with aba2:
    st.subheader("Respostas Comerciais")
    st.dataframe(df_resp)

    st.markdown("### Gráfico de Status das Respostas")
    if not df_resp.empty:
        st.bar_chart(df_resp['status'].value_counts())

# --- ABA 3: ANÁLISES ESTRATÉGICAS ---
with aba3:
    st.subheader("Métricas e Análises")

    df_merged = pd.merge(df_solic, df_resp, on='nota_fiscal', how='left', suffixes=('_solic', '_resp'))
    df_merged['tempo_resposta'] = pd.to_datetime(df_merged['data_resposta'], errors='coerce') - pd.to_datetime(df_merged['data_solicitacao'], errors='coerce')

    tempo_medio = df_merged['tempo_resposta'].dropna().mean()
    st.metric("⏱️ Tempo médio de resposta", str(tempo_medio).split('.')[0] if not pd.isna(tempo_medio) else "N/A")

    sem_resposta = df_merged[df_merged['data_resposta'].isna()]
    st.metric("🔴 Solicitações sem resposta", len(sem_resposta))

    st.markdown("### Solicitações por Dia")
    if 'dia' in df_solic:
        st.line_chart(df_solic.groupby('dia').size())
