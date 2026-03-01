import time
import logging
import os
import requests
from .celery_app import celery_app
from .agents_crew import crew_content_lab, crew_social_media

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="src.tasks.process_strategic_intent")
def process_strategic_intent(self, user_intent: str):
    """
    Tarefa de background base para processar intents pesados.
    Executa o CrewAI (Sub-Agentes) sem travar a API.
    """
    logger.info(f"🚀 [Celery Worker] Iniciando processamento do intent: {user_intent}")
    
    # Executa o esquadrão de redação da Hana Beauty
    resultado_crew = crew_content_lab.process_campaign(user_intent)
    
    logger.info(f"✅ [Celery Worker] Tarefa concluída.")
    logger.info(f"✅ [Celery Worker] Tarefa concluída.")
    return {"status": "success", "result": resultado_crew}

@celery_app.task(bind=True, name="src.tasks.process_evolution_webhook_task")
def process_evolution_webhook_task(self, payload: dict):
    """
    Tarefa de background que processa os webhooks recebidos da Evolution API (WhatsApp).
    Aqui a Hana AI Core (Agente) é acionada de forma autônoma e segura.
    """
    event_type = payload.get('event')
    logger.info(f"⚙️ [Celery Worker] Processando webhook Evolution API: {event_type}")
    
    # Evento quando uma nova mensagem entra no WhatsApp conectado
    if event_type == "messages.upsert":
        data = payload.get("data", {})
        message_info = data.get("message", {})
        key = data.get("key", {})
        
        # Ignora mensagens enviadas pela própria Hana (fromMe = True) para evitar looping
        if key.get("fromMe") is True:
            logger.info("⏸️ Ignorando mensagem enviada por nós mesmos.")
            return {"status": "ignored", "reason": "fromMe"}
            
        # Pega o número do cliente e o texto da mensagem
        remote_jid = key.get("remoteJid", "Desconhecido")
        texto_msg = message_info.get("conversation", "")
        
        # Casos onde o texto vem dentro de message.extendedTextMessage.text
        if not texto_msg and isinstance(message_info.get("extendedTextMessage"), dict):
            texto_msg = message_info["extendedTextMessage"].get("text", "")
            
        logger.info(f"📱 Nova mensagem WhatsApp de {remote_jid}: {texto_msg}")
        
        # Construindo o contexto para enviar ao Agente do CrewAI
        wa_context = {
            "plataforma": "WhatsApp",
            "usuario": remote_jid.replace("@s.whatsapp.net", ""),
            "comentario": texto_msg
        }
        
        logger.info("🧠 Disparando Agente de Atendimento/Vendas para analisar a mensagem...")
        resposta = crew_social_media.process_social_comment(wa_context)
        
        logger.info(f"✅ [Celery Worker] Resposta do Agente Gerada:\n{resposta}")
        
        # Enviar a resposta de volta via Evolution API
        try:
            # A instância vem no payload (ex: "Hana_Intel_PRO")
            instance_name = payload.get("instance", "Hana_Intel_PRO")
            evo_url = os.getenv("EVOLUTION_API_URL", "https://webhook.adsai.com.br")
            evo_token = os.getenv("EVOLUTION_API_TOKEN", "978C405A-31F2-439D-9A63-C439ADEEF30E") # Fallback provisório baseado no seu log
            
            # Formata o número (remoteJid pode vir como 551199999999@s.whatsapp.net)
            number = remote_jid.replace("@s.whatsapp.net", "")
            
            send_url = f"{evo_url.rstrip('/')}/message/sendText/{instance_name}"
            headers = {
                "apikey": evo_token,
                "Content-Type": "application/json"
            }
            body = {
                "number": number,
                "text": resposta
            }
            
            logger.info(f"📤 Enviando resposta para {send_url} (Destino: {number})")
            resp = requests.post(send_url, json=body, headers=headers, timeout=15)
            
            if resp.status_code in (200, 201):
                logger.info("✅ Mensagem enviada com sucesso pela Evolution API!")
            else:
                logger.error(f"❌ Erro ao enviar para Evolution. Status: {resp.status_code}, Body: {resp.text}")
                
        except Exception as e:
            logger.error(f"❌ Falha crítica ao tentar disparar webhook de resposta: {e}")
        
        return {"status": "success", "event": event_type, "agent_response": resposta, "remote_jid": remote_jid}
        
    else:
        logger.warning(f"⚠️ Evento Evolution ignorado ou não tratado: {event_type}")
        return {"status": "ignored", "event": event_type}
