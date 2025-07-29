import sqlite3

# Conectar ou criar o banco
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Criar tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL,
    funcao TEXT NOT NULL
)
""")

# Inserir usuário admin (se ainda não existir)
cursor.execute("SELECT * FROM usuarios WHERE nome = 'admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO usuarios (nome, senha, funcao) VALUES (?, ?, ?)", ("admin", "admin", "Admin"))
    print("Usuário admin criado com sucesso!")

conn.commit()
conn.close()
