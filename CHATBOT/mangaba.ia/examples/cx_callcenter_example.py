#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso do Mangaba AI para Customer Experience (CX)
Cenário: Análise e Resposta de Tickets de Suporte em Call Center
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangaba import Agent, Task, Crew, Process


def cx_callcenter_example():
    """
    Exemplo: Crew de CX para análise de tickets e garantia de qualidade
    """
    print("="*80)
    print("🎧 EXEMPLO: CX Call Center - Análise e Resposta de Tickets")
    print("="*80)
    
    # 1. Definir Agentes Especializados
    
    # Agente 1: Especialista em Suporte (Analisa e Responde)
    support_specialist = Agent(
        role="Especialista Sênior em Suporte ao Cliente",
        goal="Analisar problemas dos clientes e fornecer soluções empáticas e precisas",
        backstory="""Você é um especialista experiente em suporte ao cliente com 5 anos de experiência
        lidando com reclamações complexas. Você é conhecido por sua empatia, paciência
        e capacidade de acalmar situações tensas enquanto fornece soluções técnicas claras.
        Você sempre segue o tom de voz da empresa: profissional, acolhedor e prestativo.
        IMPORTANTE: Você deve sempre responder em Português do Brasil.""",
        verbose=True
    )
    
    # Agente 2: Especialista em QA (Avalia Qualidade e Sentimento)
    qa_specialist = Agent(
        role="Especialista em Garantia de Qualidade (QA)",
        goal="Garantir alta qualidade nas respostas de suporte e analisar o sentimento do cliente",
        backstory="""Você é um especialista meticuloso em QA que revisa interações de suporte.
        Você verifica a conformidade com as políticas da empresa, precisão do tom e correção da solução.
        Você também é um especialista em análise de sentimento, capaz de detectar sinais emocionais
        sutis nas mensagens dos clientes para prevenir cancelamentos (churn).
        IMPORTANTE: Você deve sempre responder em Português do Brasil.""",
        verbose=True
    )
    
    # Agente 3: Supervisor de CX (Visão Estratégica)
    cx_supervisor = Agent(
        role="Supervisor de Experiência do Cliente (CX)",
        goal="Supervisionar o processo de suporte e fornecer recomendações estratégicas",
        backstory="""Você é o líder de equipe responsável pela experiência geral do cliente.
        Você olha para o quadro geral, identificando problemas sistêmicos a partir de tickets individuais.
        Você fornece treinamento (coaching) aos agentes e sugere melhorias de processo para reduzir
        o volume de tickets e aumentar a satisfação do cliente (CSAT).
        IMPORTANTE: Você deve sempre responder em Português do Brasil.""",
        verbose=True
    )
    
    # 2. Definir Tasks
    
    # Task 1: Análise Inicial e Classificação
    analysis_task = Task(
        description="""Analise o seguinte ticket de cliente:
        "{ticket_content}"
        
        1. Identifique o problema principal.
        2. Classifique a categoria do ticket (ex: Faturamento, Técnico, Sugestão).
        3. Determine o nível de urgência (Baixo, Médio, Alto, Crítico).
        4. Extraia detalhes chave do cliente (se houver).
        
        Responda em Português do Brasil.""",
        expected_output="""Uma análise estruturada contendo:
        - Resumo do Problema Principal
        - Categoria
        - Nível de Urgência
        - Detalhes Chave""",
        agent=support_specialist
    )

    # Task 2: Elaboração da Resposta
    draft_response_task = Task(
        description="""Redija uma resposta para o cliente com base na análise.
        
        Diretrizes:
        - Reconheça a frustração do cliente (empatia).
        - Aborde o problema principal diretamente.
        - Forneça uma solução clara ou próximos passos.
        - Mantenha um tom profissional e acolhedor.
        - NÃO prometa reembolsos sem aprovação (assuma aprovação para valores < R$ 250).
        
        A resposta deve ser em Português do Brasil.""",
        expected_output="""Um rascunho completo de email de resposta pronto para ser enviado ao cliente.""",
        agent=support_specialist,
        context=[analysis_task]
    )
    
    # Task 3: Avaliação de QA e Sentimento
    qa_review_task = Task(
        description="""Revise a resposta redigida e o ticket original.
        
        1. Analise o sentimento do cliente no ticket original (Positivo, Neutro, Negativo, Irritado).
        2. Avalie a resposta redigida contra os padrões de qualidade (Empatia, Clareza, Solução).
        3. Dê uma nota para a resposta (0-10).
        4. Sugira melhorias específicas se a nota for menor que 9.
        
        Responda em Português do Brasil.""",
        expected_output="""Um relatório de QA com:
        - Análise de Sentimento do Cliente
        - Nota de Qualidade da Resposta
        - Pontos Fortes e Fracos
        - Sugestões de Melhoria (se houver)""",
        agent=qa_specialist,
        context=[analysis_task, draft_response_task]
    )
    
    # Task 4: Relatório Gerencial e Recomendações
    supervisor_report_task = Task(
        description="""Revise toda a interação (Ticket, Análise, Resposta, Relatório de QA).
        
        1. Forneça um veredito final sobre o tratamento deste caso.
        2. Identifique se este problema representa uma tendência maior ou problema sistêmico.
        3. Sugira uma correção de longo prazo para prevenir este tipo de ticket.
        4. Crie uma nota de coaching para o especialista de suporte.
        
        Responda em Português do Brasil.""",
        expected_output="""Um resumo gerencial incluindo:
        - Veredito do Caso (Aprovado/Precisa de Revisão)
        - Identificação de Problema Sistêmico
        - Recomendação de Melhoria de Processo
        - Nota de Coaching""",
        agent=cx_supervisor,
        context=[analysis_task, draft_response_task, qa_review_task],
        output_file="cx_case_report.md"
    )
    
    # 3. Criar Crew
    cx_crew = Crew(
        agents=[support_specialist, qa_specialist, cx_supervisor],
        tasks=[analysis_task, draft_response_task, qa_review_task, supervisor_report_task],
        process=Process.SEQUENTIAL,
        verbose=True
    )
    
    # 4. Executar o Crew
    print("\n🚀 Iniciando execução do Crew de CX...\n")
    
    # Exemplo de Ticket de Cliente (Traduzido)
    sample_ticket = """
    Assunto: URGENTE - Cobrança Duplicada no meu Cartão de Crédito!!
    
    Olá, acabei de verificar minha fatura e vejo DUAS cobranças da minha assinatura este mês!
    Isso é inaceitável. Sou cliente fiel há 3 anos e é assim que vocês me tratam?
    Preciso que uma delas seja estornada IMEDIATAMENTE ou vou cancelar minha conta e ir para o concorrente.
    Resolvam isso agora!
    
    - João Silva
    ID da Conta: 12345
    """
    
    result = cx_crew.kickoff(inputs={
        "ticket_content": sample_ticket
    })
    
    print("\n" + "="*80)
    print("✅ CASO DE CX PROCESSADO")
    print("="*80)
    print(f"\n📊 Duração: {result.duration:.2f} segundos")
    print(f"\n📄 Relatório Gerencial Final:")
    print("-"*80)
    print(result.final_output)
    print("\n💾 Relatório completo salvo em: cx_case_report.md")


if __name__ == "__main__":
    cx_callcenter_example()
