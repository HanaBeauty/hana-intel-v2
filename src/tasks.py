import time
import logging
import os
import requests
from .celery_app import celery_app
from .agents_crew import crew_content_lab, crew_social_media

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="src.tasks.process_strategic_intent")
def process_strategic_intent(self, user_intent: str, content_type: str = "conteúdo geral"):
    """
    Tarefa de background base para processar intents pesados.
    Executa o CrewAI (Sub-Agentes) sem travar a API.
    """
    logger.info(f"🚀 [Celery Worker] Iniciando processamento do intent: {user_intent} (Formato: {content_type})")
    
    # Executa o esquadrão de redação da Hana Beauty
    resultado_crew = crew_content_lab.process_campaign(user_intent, content_type)
    
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
        
        # Identificando a origem da mensagem e configurando o client Redis puro (usando a mesma var do Celery)
        import redis
        import json
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Pega o número do cliente e o texto da mensagem
        remote_jid = key.get("remoteJid", "Desconhecido")
        number = remote_jid.replace("@s.whatsapp.net", "")
        
        texto_msg = message_info.get("conversation", "")
        if not texto_msg and isinstance(message_info.get("extendedTextMessage"), dict):
            texto_msg = message_info["extendedTextMessage"].get("text", "")

        # 1. Lógica de Intervenção Humana (Handoff)
        handoff_key = f"human_handoff:{number}"
        if key.get("fromMe") is True:
            comando = texto_msg.strip().lower()
            
            # Comandos de Sistema via WhatsApp Web (Sobrecarga de Administrador)
            if comando == "/bot_on":
                logger.info(f"🟢 Comando de Sistema: Bot acordado manualmente para {number}.")
                r.delete(handoff_key)
                return {"status": "ignored", "reason": "system_command_bot_on"}
            elif comando == "/bot_off":
                logger.info(f"🔴 Comando de Sistema: Bot silenciado manualmente para {number}.")
                r.setex(handoff_key, 43200, "active") # 12 horas
                return {"status": "ignored", "reason": "system_command_bot_off"}

            logger.info(f"⏸️ Mensagem enviada pela Loja (fromMe). Ativando Hand-off para {number} por 12 horas.")
            r.setex(handoff_key, 43200, "active") # 12 horas em segundos
            
            # Mesmo sendo fromMe e não sendo comando, gravamos no histórico
            history_key = f"chat_history:{number}"
            r.rpush(history_key, f"[Hana Beauty]: {texto_msg}")
            r.ltrim(history_key, -10, -1)
            return {"status": "ignored", "reason": "human_handoff_activated"}
            
        # 2. Verificação de Handoff já Ativo
        if r.exists(handoff_key):
            logger.info(f"🤫 IA Silenciada: O cliente {number} está sob atendimento humano e enviou resposta.")
            # Continuamos salvando a resposta do cliente para o histórico não ficar quebrado quando a IA voltar
            history_key = f"chat_history:{number}"
            r.rpush(history_key, f"[Cliente]: {texto_msg}")
            r.ltrim(history_key, -10, -1)
            return {"status": "ignored", "reason": "human_handoff_active_silence"}

        logger.info(f"📱 Nova mensagem WhatsApp de {remote_jid}: {texto_msg}")
        
        # 3. Lógica de Memória Conversacional
        history_key = f"chat_history:{number}"
        r.rpush(history_key, f"[Cliente]: {texto_msg}")
        r.ltrim(history_key, -10, -1)
        
        # Resgatando o histórico completo (formatado como string para a IA ler)
        history_list = r.lrange(history_key, 0, -1)
        historico_formatado = "\n".join(history_list)
        
        # Construindo o contexto para enviar ao Agente do CrewAI
        wa_context = {
            "plataforma": "WhatsApp",
            "usuario": number,
            "comentario": texto_msg,
            "historico": historico_formatado
        }
        
        logger.info("🧠 Disparando Agente RAG para analisar a mensagem contextualizada...")
        resposta = crew_social_media.process_social_comment(wa_context)
        
        logger.info(f"✅ [Celery Worker] Resposta do Agente Gerada:\n{resposta}")
        
        # Assim que a IA responde, gravamos a resposta dela no histórico do Redis
        r.rpush(history_key, f"[Hana IA]: {resposta}")
        r.ltrim(history_key, -10, -1)
        
        # Enviar a resposta de volta via Evolution API
        try:
            # A instância vem no payload (ex: "Hana_Intel_PRO")
            instance_name = payload.get("instance", "Hana_Intel_PRO")
            evo_url = os.getenv("EVOLUTION_API_URL", "https://webhook.adsai.com.br")
            evo_token = os.getenv("EVOLUTION_API_TOKEN", "978C405A-31F2-439D-9A63-C439ADEEF30E") # Fallback provisório
            
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
