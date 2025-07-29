import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="📈 Desempenho (%) por Função", layout="wide")
st.title("📊 Análise de Desempenho por Colaborador")

# Verifica login e acesso
if "logado" not in st.session_state or not st.session_state.logado:
    st.error("❌ Faça login para acessar esta página.")
    st.stop()

if st.session_state.funcao != "Líder":
    st.warning("🔒 Apenas líderes podem visualizar esta página.")
    st.stop()

# Carrega dados
DB_PATH = "usuarios.db"
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("""
    SELECT usuario, funcao, quantidade
    FROM relatorios
""", conn)
conn.close()

if df.empty:
    st.info("Nenhum dado encontrado.")
    st.stop()

# Calcula média por função
media_por_funcao = df.groupby("funcao")["quantidade"].mean().reset_index()
media_por_funcao.rename(columns={"quantidade": "media_funcao"}, inplace=True)

# Soma de quantidade por usuário e função
soma_usuario_funcao = df.groupby(["usuario", "funcao"])["quantidade"].sum().reset_index()

# Junta as tabelas
resultado = pd.merge(soma_usuario_funcao, media_por_funcao, on="funcao")

# Calcula desempenho em %
resultado["desempenho_%"] = (resultado["quantidade"] / resultado["media_funcao"]) * 100
resultado["desempenho_%"] = resultado["desempenho_%"].round(1)

# Define ícones
def icone(valor):
    if valor >= 110:
        return "🟢"
    elif valor >= 90:
        return "🟡"
    else:
        return "🔴"

resultado["Indicador"] = resultado["desempenho_%"].apply(icone)

# Reorganiza colunas
resultado = resultado[["usuario", "funcao", "media_funcao", "quantidade", "desempenho_%", "Indicador"]]
resultado.columns = ["👤 Colaborador", "🧩 Função", "📊 Média da Função", "📦 Quantidade Total", "📈 Desempenho (%)", "🔍 Status"]

# Mostra tabela
st.dataframe(resultado, use_container_width=True)

# Gráfico opcional
st.subheader("📊 Gráfico de Desempenho (%) por Colaborador")
import plotly.express as px

fig = px.bar(
    resultado,
    x="👤 Colaborador",
    y="📈 Desempenho (%)",
    color="🧩 Função",
    text="📈 Desempenho (%)",
    title="Desempenho percentual em relação à média da função",
)
fig.update_traces(textposition='outside')
fig.update_layout(yaxis_tickformat="%")
st.plotly_chart(fig, use_container_width=True)
