import os
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Ajuste de caminho: DB junto à raiz do app
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")  # igual ao do login fileciteturn3file1

# Verifica login
if not st.session_state.get("logado", False):
    st.error("❌ Você precisa estar logado para acessar esta página.")
    st.stop()

# Página
st.set_page_config(page_title="📊 Gráficos", layout="wide")
st.title("📈 Análise de Rendimento por Funcionário")

# Busca usuários que registraram relatórios
@st.cache_data
def obter_usuarios():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT DISTINCT usuario FROM relatorios", conn)
    conn.close()
    return df["usuario"].tolist()

# Se não for Líder, só vê a si mesmo
if st.session_state.funcao != "Líder":
    lista_usuarios = [st.session_state.usuario]
    disable_select = True
else:
    lista_usuarios = obter_usuarios()
    disable_select = False

if not lista_usuarios:
    st.warning("Nenhum colaborador com registros encontrados.")
    st.stop()

# Selectbox restrito
usuario_selecionado = st.selectbox(
    "👤 Selecione um funcionário:",
    lista_usuarios,
    disabled=disable_select
)

# Período
data_inicio = st.date_input(
    "Data início", value=pd.to_datetime("today") - pd.Timedelta(days=30)
)
data_fim = st.date_input(
    "Data fim", value=pd.to_datetime("today")
)

# Query de relatórios
conn = sqlite3.connect(DB_PATH)
query = (
    "SELECT usuario AS username, funcao, quantidade, DATE(timestamp) AS data "
    "FROM relatorios "
    "WHERE usuario = ? AND data BETWEEN ? AND ?"
)
df = pd.read_sql_query(query, conn, params=(usuario_selecionado, data_inicio, data_fim))
conn.close()

if df.empty:
    st.warning("Nenhum dado encontrado para o período selecionado.")
    st.stop()

# Charts
fig = px.line(
    df, x="data", y="quantidade",
    title=f"Rendimento de {usuario_selecionado} de {data_inicio} a {data_fim}",
    labels={"quantidade":"Quantidade","data":"Data"}
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Total de atividades por função")
df2 = df.groupby("funcao")["quantidade"].sum().reset_index()
fig2 = px.bar(
    df2, x="funcao", y="quantidade", color="funcao",
    title=f"Total de atividades de {usuario_selecionado}",
    labels={"quantidade":"Quantidade","funcao":"Função"}
)
st.plotly_chart(fig2, use_container_width=True)
st.subheader("📈 Evolução diária")