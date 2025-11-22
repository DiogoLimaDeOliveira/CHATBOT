import os

# O main.py vai salvar o JSON neste arquivo aqui.
# O utils só precisa ler ele.
NOME_ARQUIVO_DADOS = "catalogo_loja.txt"

def carregar_dados():
    # 1. Verifica se o arquivo existe
    if not os.path.exists(NOME_ARQUIVO_DADOS):
        return "ERRO CRÍTICO: A empresa ainda não enviou o catálogo pelo site."

    try:
        # 2. Abre e lê o conteúdo
        with open(NOME_ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
            
            # se o arquivo estive vazio
            if not conteudo:
                return "AVISO: O catálogo existe mas esta vazio"
                
            return conteudo

    except Exception as e:
        return f"Erro ao tentar ler o catálogo: {e}"