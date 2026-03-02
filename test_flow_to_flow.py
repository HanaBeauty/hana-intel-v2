import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv(".env")
# Habilitar logs detalhados para o teste E2E
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

from src.agents_crew import crew_social_media

async def run_e2e_simulation():
    """
    Simula uma coversa (Flow to Flow) vinda da Evolution API no WhatsApp
    buscando ativamente ler e extrair a tool de ShopifyOrderStatusTool.
    """
    logger.info("=====================================================================")
    logger.info("[E2E SIMULATION] INICIANDO O BATISMO DE FOGO DA HANA AI CORE")
    logger.info("=====================================================================")

    lead_phone = "5511999999999"

    # Criamos um mock de um histórico curto do cliente conforme o padrao do Redis
    history_mock = "[Cliente]: olá, tudo bem?\n[Hana IA]: Olá, Lash de Ouro! Tudo ótimo por aqui na Hana Beauty. Como posso te auxiliar hoje em relação aos seus procedimentos ou produtos?"

    # Mensagem de Desafio: Exige interpretação do NLP + Acionamento de Ferramenta
    user_challenge_message = "Eu comprei recentemente com o e-mail juliano@teste.com, queria ver como está o status de entrega (rastreio) da minha nova cola etil que acabei de pagar. Consegue checar pra mim fazendo favor?"

    logger.info(f"👨‍💻 [Lead WhatsApp]: {user_challenge_message}")
    logger.info("🧠 [Hana Intel]: Processando a Intent e avaliando Tool Calling...")
    
    wa_context = {
        "plataforma": "WhatsApp",
        "usuario": lead_phone,
        "comentario": user_challenge_message,
        "historico": history_mock
    }

    try:
        # A API Core da Hana tem a inteligência de analisar as tools e decidir chamar a do Shopify
        response = await asyncio.to_thread(
            crew_social_media.process_social_comment, 
            social_context=wa_context
        )
        
        print("\n\n")
        logger.info("✅ [Hana Intel - Resposta Final do Agente]:")
        for line in str(response).split("\n"):
            print(f"      {line}")
            
    except Exception as e:
        logger.error(f"❌ [Falha no E2E]: O agente crashou durante a simulação: {e}")

if __name__ == "__main__":
    asyncio.run(run_e2e_simulation())
