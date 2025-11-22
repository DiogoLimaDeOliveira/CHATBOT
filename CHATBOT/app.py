# exemplo_basico.py
from mangaba_ai import MangabaAgent

# Criar agente
agent = MangabaAgent()

# Primeira conversa
resposta = agent.chat("o que é um, pi?")
print(resposta)

# Continuar conversa
resposta = agent.chat("quqantos numeros de pi voce consegue printar pra  mim?")
print(resposta)