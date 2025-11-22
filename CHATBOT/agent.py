import os
import sqlite3
from mangaba_ai import MangabaAgent
from dotenv import load_dotenv
from utils import carregar_dados

# Carrega configs
load_dotenv()

# ---------------------------
# BANCO DE DADOS (SQLite)
# ---------------------------

def inicializar_banco():
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensagem_usuario TEXT,
            resposta_ia TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_interacao(mensagem_usuario, resposta_ia):
    conn = sqlite3.connect("respostas.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interacoes (mensagem_usuario, resposta_ia)
        VALUES (?, ?)
    """, (mensagem_usuario, resposta_ia))
    conn.commit()
    conn.close()

# Inicializa BD ao iniciar o programa
inicializar_banco()

# ---------------------------
# LÓGICA DO AGENTE
# ---------------------------

def gerar_resposta_do_vendedor(mensagem_usuario, contexto_do_catalogo):
    """
    Função Mestra da IA.
    Recebe: Pergunta do Cliente + Texto do Catálogo
    Retorna: A resposta do Vendedor
    """

    print("AGENTE: Recebi os dados. Preparando cérebro...")

    try:
        agent = MangabaAgent()
    except Exception as e:
        return f"Erro ao ligar a IA: {e}"

    # Gera resposta
    text = agent.chat_with_context(contexto_do_catalogo)(mensagem_usuario)

    # Print normal
    print(text)

    # Salva em banco de dados, para devolver a empresa
    salvar_interacao(mensagem_usuario, text)

    return text
