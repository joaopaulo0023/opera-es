# main.py
import os
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# ————— Configurações —————
st.set_page_config(page_title="🔐 Login", layout="centered")

DB_PATH = "usuarios.db"
FUNCOES = [
    "Líder",
    "Separação 1",
    "Separação 2",
    "Corredor",
    "Gate",
    "Faturamento",
    "Carregamento",
    "Separação Toyota, PSA, Nissan"
]

# ————— Funções auxiliares —————
def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

# — Verifica credenciais —
def verificar_credenciais(username: str, senha: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM usuarios WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and hash_senha(senha) == row[0])

# — Adiciona novo usuário —
def adicionar_usuario(username: str, senha: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, funcao) VALUES (?, ?, ?)",
            (username, hash_senha(senha), "")
        )
        conn.commit()
        st.success("✅ Usuário adicionado com sucesso!")
    except sqlite3.IntegrityError:
        st.error("⚠️ Usuário já existe.")
    conn.close()

# ————— Interface Streamlit —————
st.title("🔐 Sistema Logístico com IA")

# Inicializa sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.session_state.funcao = ""

# ——— TELA DE LOGIN ———
if not st.session_state.logado:
    usuario      = st.text_input("Usuário")
    senha        = st.text_input("Senha", type="password")
    funcao_login = st.selectbox("Função", FUNCOES)
    if st.button("Login"):
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash, funcao FROM usuarios WHERE username = ?",
            (usuario,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            st.error("Usuário não cadastrado.")
        else:
            password_hash_db, funcao_db = row
            if hash_senha(senha) != password_hash_db:
                st.error("Senha incorreta.")
            elif funcao_login == "Líder" and funcao_db != "Líder":
                st.error("Você não tem permissão para a função “Líder”.")
            else:
                st.session_state.logado  = True
                st.session_state.usuario = usuario
                st.session_state.funcao  = funcao_login
                st.rerun()
    st.stop()

# === PÓS-LOGIN ===
now  = datetime.now()
hour = now.hour
if hour < 12:
    cumprimento = "Bom dia"
elif hour < 18:
    cumprimento = "Boa tarde"
else:
    cumprimento = "Boa noite"

st.sidebar.title("Menu")
st.sidebar.write(f"👤 {st.session_state.usuario}")
st.sidebar.write(f"🧩 {st.session_state.funcao}")
if st.sidebar.button("Logout"):
    st.session_state.logado   = False
    st.session_state.usuario  = ""
    st.session_state.funcao   = ""
    st.rerun()

st.header(f"{cumprimento}, {st.session_state.usuario}!")
st.write(f"Você está na função **{st.session_state.funcao}** hoje.")

# ————— Relatório de atividade por função —————
func = st.session_state.funcao
q = None

if func.startswith("Separação"):
    st.info("Assim que você separar alguns paletes, informe abaixo quantos foram separados.")
    q = st.text_input("Paletes separados:", key="input_sep")
elif func == "Corredor":
    st.info("Assim que você amarrar paletes, informe quantos foram amarrados.")
    q = st.text_input("Paletes amarrados:", key="input_cor")
elif func == "Gate":
    st.info("Assim que você montar paletes, informe quantas tartarugas foram batidas.")
    q = st.text_input("Tartarugas batidas:", key="input_gate")
elif func == "Carregamento":
    st.info("Assim que você carregar, informe quantos paletes foram carregados.")
    q = st.text_input("Paletes carregados:", key="input_car")
elif func == "Faturamento":
    st.info("Assim que você gerar notas fiscais, informe quantas NFs foram geradas.")
    q = st.text_input("NFs geradas:", key="input_fat")
else:
    st.info("Use o menu de cadastro ou de tarefas conforme sua função.")

if q is not None and st.button("Enviar relatório"):
    try:
        quantidade = int(q)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relatorios (usuario, funcao, quantidade)
            VALUES (?, ?, ?)
        """, (
            st.session_state.usuario,
            st.session_state.funcao,
            quantidade
        ))
        conn.commit()
        conn.close()
        st.success(f"✅ Registrado: {quantidade} para {func}.")
    except ValueError:
        st.error("Por favor, entre com um número inteiro válido.")

# ————— Listagem de tarefas por função —————
st.markdown("---")
st.subheader("🔔 Suas Tarefas")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    "SELECT id, descricao, concluido FROM tarefas WHERE funcao = ? ORDER BY prioridade DESC",
    (st.session_state.funcao,)
)
tarefas = cursor.fetchall()
conn.close()

for tid, desc, done in tarefas:
    marcado = st.checkbox(desc, value=bool(done), key=f"tarefa_{tid}")
    if marcado and not done:
        cconn = sqlite3.connect(DB_PATH); cc = cconn.cursor()
        cc.execute("UPDATE tarefas SET concluido = 1 WHERE id = ?", (tid,))
        cconn.commit(); cconn.close()
    elif not marcado and done:
        cconn = sqlite3.connect(DB_PATH); cc = cconn.cursor()
        cc.execute("UPDATE tarefas SET concluido = 0 WHERE id = ?", (tid,))
        cconn.commit(); cconn.close()

# ————— Registrar quantidade em função auxiliar —————
st.markdown("---")
st.subheader("➕ Registrar Quantidade em Outra Função")

# Remove a opção "Líder" da lista de funções auxiliares
funcoes_ajuda = [f for f in FUNCOES if f != "Líder"]

with st.form("ajuda_quant_form"):
    func_ajuda = st.selectbox("Em qual função você ajudou?", funcoes_ajuda)
    qtd_ajuda  = st.text_input("Quantidade executada:")
    submit_ajuda = st.form_submit_button("Registrar ajuda")
    if submit_ajuda:
        try:
            qtd = int(qtd_ajuda)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO relatorios (usuario, funcao, quantidade) VALUES (?, ?, ?)",
                (st.session_state.usuario, func_ajuda, qtd)
            )
            conn.commit()
            conn.close()
            st.success(f"✅ Registrado: {qtd} em {func_ajuda}.")
        except ValueError:
            st.error("Por favor, insira um número inteiro válido.")


# ————— Histórico de registros auxiliares —————
st.markdown("**Histórico de registros auxiliares:**")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    "SELECT funcao, quantidade, timestamp FROM relatorios WHERE usuario = ? AND funcao != ? ORDER BY timestamp DESC", 
    (st.session_state.usuario, st.session_state.funcao)
)
aux_historico = cursor.fetchall()
conn.close()

if aux_historico:
    for f, qtd, ts in aux_historico:
        st.write(f"- {f}: {qtd} em {ts}")
else:
    st.write("Nenhum registro auxiliar encontrado.")

# ————— Cadastro de novos usuários (apenas Líder) —————
if st.session_state.funcao == "Líder":
    st.markdown("---")
    st.subheader("🆕 Cadastrar Novo Colaborador")

    with st.form("form_cadastro_usuario"):
        novo_usuario = st.text_input("Novo nome de usuário")
        nova_senha = st.text_input("Senha", type="password")
        nova_funcao = st.selectbox("Função", FUNCOES)
        submit_cadastro = st.form_submit_button("Cadastrar")

        if submit_cadastro:
            if not novo_usuario or not nova_senha:
                st.warning("⚠️ Usuário e senha são obrigatórios.")
            else:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO usuarios (username, password_hash, funcao) VALUES (?, ?, ?)",
                        (novo_usuario, hash_senha(nova_senha), nova_funcao)
                    )
                    conn.commit()
                    st.success(f"✅ Usuário '{novo_usuario}' cadastrado com sucesso.")
                except sqlite3.IntegrityError:
                    st.error("❌ Este nome de usuário já existe.")
                conn.close()
