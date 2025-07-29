import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="📊 Desempenho Geral", layout="wide")
st.title("📦 Desempenho Geral dos Colaboradores")

# Protege a página: só Líder pode ver
if "logado" not in st.session_state or not st.session_state.logado:
    st.error("❌ Faça login para acessar esta página.")
    st.stop()

if st.session_state.funcao != "Líder":
    st.warning("🔒 Apenas líderes podem visualizar esta página.")
    st.stop()

# Conexão com banco
DB_PATH = "usuarios.db"
conn = sqlite3.connect(DB_PATH)

# Carrega dados do banco
df = pd.read_sql_query("""
    SELECT usuario, funcao, quantidade, timestamp
    FROM relatorios
""", conn)

conn.close()

if df.empty:
    st.info("Nenhum dado registrado ainda.")
    st.stop()

# Converte timestamp e extrai períodos
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["Ano"] = df["timestamp"].dt.year
df["Mês"] = df["timestamp"].dt.strftime('%B')
df["Dia"] = df["timestamp"].dt.date
df["Semana"] = df["timestamp"].dt.strftime("Sem. %U")
df["Turno"] = df["timestamp"].dt.hour

# Define turno baseado no horário (ajuste se necessário)
def classificar_turno(hora):
    if 6 <= hora < 15:
        return "1º Turno"
    elif 15 <= hora < 23:
        return "2º Turno"
    else:
        return "3º Turno"

df["Turno"] = df["Turno"].apply(classificar_turno)

# Filtros
periodo = st.selectbox("📆 Agrupar por período:", ["Dia", "Semana", "Mês", "Ano"])
funcao_filtro = st.multiselect("🧩 Filtrar por função:", df["funcao"].unique(), default=list(df["funcao"].unique()))

df = df[df["funcao"].isin(funcao_filtro)]

# Agrupamento
df_group = df.groupby([periodo, "usuario", "Turno"])["quantidade"].sum().reset_index()

# Gráfico
st.subheader("📊 Quantidade de Paletes Carregados (por período e turno)")

fig = px.bar(
    df_group,
    x=periodo,
    y="quantidade",
    color="Turno",
    barmode="group",
    facet_col="usuario",
    labels={"quantidade": "Qtd. Paletes"},
    title="Total e Distribuição de Paletes por Turno e Colaborador"
)

fig.update_layout(xaxis_title="Período", yaxis_title="Qtd. Paletes", legend_title="Turno")
st.plotly_chart(fig, use_container_width=True)
