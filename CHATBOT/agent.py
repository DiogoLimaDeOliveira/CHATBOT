import os
from mangaba_ai import MangabaAgent
from dotenv import load_dotenv #procura key nop arquivo env

# importa  função de leitura 
from utils import carregar_dados

# Carrega configus
load_dotenv()

# personalidade do bot
def gerar_resposta_do_vendedor(mensagem_usuario, contexto_do_catalogo):
    """
    Função Mestra da IA.
    Recebe: Pergunta do Cliente + Texto do Catálogo
    Retorna: A resposta do Vendedor
    """
    
    print("AGENTE: Recebi os dados. Preparando cérebro...")

    # inicializa o Manga
    try:
        agent = MangabaAgent()
    except Exception as e:
        return f"Erro ao ligar a IA: {e}"



