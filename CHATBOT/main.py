from fastapi import FastAPI, UploadFile, File, HTTPException #p entrada e saida de infos
from fastapi.middleware.cors import CORSMiddleware #evitar erro 
from pydantic import BaseModel #gerantir que chegue o dado certo
import shutil #pegar arquivos no buffer
import os
import requests  

from agent import consultar_ia
from until import carregar_dados_como_txt

app = FastAPI()

origins = ["*"]  # isso aqui e pro navegador nao dar erro, o certo e deixar o dominio do site

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, #aceitar cookies
    allow_methods=["*"], # a web pode usar todas as acoes
    allow_headers=["*"], # aceitar qualquer header do front
)

class ChatRequest(BaseModel):
    mensagem: str

PASTA_UPLOADS = "uploads"
os.makedirs(PASTA_UPLOADS, exist_ok=True)


URL_SERVIDOR_EMPRESA = "https://sua-empresa.com/api/receber"

def salvar_resposta_local(pergunta: str, resposta: str):
    """Salva pergunta + resposta no arquivo de histórico."""
    with open("historico_respostas.txt", "a", encoding="utf-8") as f:
        f.write(f"Pergunta: {pergunta}\n")
        f.write(f"Resposta: {resposta}\n\n")


def salvar_resposta_local(resposta: str):
    """Salva a resposta do chatbot em um arquivo local."""
    with open("historico_respostas.txt", "a", encoding="utf-8") as f:
        f.write(resposta + "\n\n")


def enviar_para_servidor_empresa(resposta: str):
    """Envia a resposta da IA para um servidor externo."""
    try:
        payload = {"resposta": resposta}
        r = requests.post(URL_SERVIDOR_EMPRESA, json=payload, timeout=5)
        
        print("Enviado para servidor da empresa:", r.status_code)
    except Exception as e:
        print("Erro ao enviar para servidor da empresa:", e)


@app.get("/")
def home():
    return {"status": "rodando sem problemas"}

# se post for p upload, recebe o arquivo e salva
@app.post("/upload")
async def upload_catalogo(file: UploadFile = File(...)):
    try:
        caminho_arquivo = os.path.join(PASTA_UPLOADS, file.filename)

        # Salva o arquivo localmente
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"mensagem": f"arquivo {file.filename} recebido com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao salvar arquivo: {str(e)}")
    
@app.get("/historico")
async def get_historico():
    try:
        if not os.path.exists("historico_respostas.txt"):
            return {"historico": "Nenhum histórico encontrado."}

        with open("historico_respostas.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()

        return {"historico": conteudo}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        texto_catalogo = carregar_dados_como_txt()

        if not texto_catalogo:
            return {"resposta": "Nenhum catálogo encontrado. Por favor, faça o upload primeiro."}

        resposta_ia = consultar_ia(request.mensagem, texto_catalogo)

        salvar_resposta_local(resposta_ia)

        enviar_para_servidor_empresa(resposta_ia)

        return {"resposta": resposta_ia}

    except Exception as e:
        print(f"Erro no chat: {e}") # mostra no terminal
        raise HTTPException(status_code=500, detail=str(e))
