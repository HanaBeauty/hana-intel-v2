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
    
    try:
        from src.database import sync_session_maker
        from src.models import Campaign, CampaignStatus
        if sync_session_maker:
            with sync_session_maker() as session:
                # Parsing básico das variantes A/B/C geradas pelo CrewAI
                # Parsing robusto com Regex para Variantes A/B/C
                import re
                variations_dict = {}
                
                # Procura padrões como "VARIANTE A", "Variante A", "--- VARIANTE A ---", "A ---"
                patterns = {
                    "A": [r"(?i)---?\s*VARIANTE\s*A\s*---?", r"(?i)VARIANTE\s*A\s*:"],
                    "B": [r"(?i)---?\s*VARIANTE\s*B\s*---?", r"(?i)VARIANTE\s*B\s*:"],
                    "C": [r"(?i)---?\s*VARIANTE\s*C\s*---?", r"(?i)VARIANTE\s*C\s*:"]
                }
                
                text_content = str(resultado_crew)
                
                # Split simplificado por variantes principais
                split_pattern = r"(?i)---?\s*VARIANTE\s*[ABC]\s*---?"
                content_parts = re.split(split_pattern, text_content)
                
                # Se o split funcionou e temos partes
                if len(content_parts) > 1:
                    # O primeiro item costuma ser introdução, pegamos os subsequentes
                    for i, char in enumerate(["A", "B", "C"]):
                        if i + 1 < len(content_parts):
                            variations_dict[char] = content_parts[i+1].strip()
                else:
                    # Fallback caso a IA não use separadores "---"
                    variations_dict["A"] = text_content

                import json
                nova_campanha = Campaign(
                    title=f"Campanha Gerada: {content_type.capitalize()}",
                    intent=user_intent,
                    channel=content_type,
                    generated_content=str(resultado_crew), # Fallback mantendo o original
                    variations=json.dumps(variations_dict) if variations_dict else None,
                    status=CampaignStatus.draft
                )
                session.add(nova_campanha)
                session.commit()
                logger.info(f"💾 [Celery Worker] Campanha A/B/C salva com sucesso (ID: {nova_campanha.id})")
        else:
            logger.warning("⚠️ sync_session_maker indisponível. Campanha não foi persistida!")
    except Exception as e:
        error_msg = f"❌ Erro ao salvar Draft da Campanha no PostgreSQL: {e}"
        logger.error(error_msg)
        # Injeta log de erro na telemetria (via Redis para consumo rápido na dashboard)
        try:
            import redis
            import json
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.Redis.from_url(redis_url, decode_responses=True)
            log_entry = {
                "time": "Agora",
                "origin": "AI_CORE",
                "action": "DRAFT_SAVE_ERROR",
                "dest": f"Error: {str(e)[:50]}..."
            }
            r.lpush("dashboard_logs", json.dumps(log_entry))
            r.ltrim("dashboard_logs", 0, 19)
        except:
            pass

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
        
        # 0.1. Idempotência por ID de Mensagem (Evita processar o mesmo webhook 2x se o servidor reenviar)
        message_id = key.get("id")
        if message_id:
            msg_id_key = f"processed_msg:{message_id}"
            if r.get(msg_id_key):
                logger.info(f"♻️ [Idempotency] Mensagem {message_id} já processada. Ignorando.")
                return {"status": "ignored", "reason": "already_processed"}
            r.setex(msg_id_key, 600, "done") # Expira em 10 min
        
        # Pega o JID completo (Remetente/Grupo/Canal)
        remote_jid = key.get("remoteJid", "Desconhecido")
        
        # Identifica o tipo de chat: Grupo, Canal ou Pessoa
        is_group = "@g.us" in remote_jid
        is_newsletter = "@newsletter" in remote_jid
        
        # ID Limpo para o Redis/Banco (Se for grupo, mantém o @g.us para separar conversas)
        number = remote_jid.replace("@s.whatsapp.net", "")
        if not is_group and not is_newsletter:
            number = "".join(filter(str.isdigit, number))
        
        texto_msg = message_info.get("conversation", "")
        if not texto_msg and isinstance(message_info.get("extendedTextMessage"), dict):
            texto_msg = message_info["extendedTextMessage"].get("text", "")

        # 0. Registrar / Atualizar Lead no CRM Permanente (Tabela Contact)
        try:
            from src.database import sync_session_maker
            from src.models import Contact
            import datetime
            if sync_session_maker:
                with sync_session_maker() as session:
                    lead = session.query(Contact).filter(Contact.phone == number).first()
                    # pushName às vezes vem na chave, podemos tentar pegar mas focamos no número
                    contact_name = payload.get("data", {}).get("pushName", f"Lead {number[-4:]}")

                    if lead:
                        lead.last_interaction = datetime.datetime.utcnow()
                        # Atualiza nome se for um lead genérico e agora temos o pushName
                        if contact_name and lead.name and "Lead" in lead.name:
                            lead.name = contact_name
                    else:
                        # Se for grupo/newsletter, o nome pode vir diferente no payload
                        if is_group:
                            # Tentar pegar nome do grupo se disponível no futuro, por ora identificamos
                            contact_name = payload.get("data", {}).get("groupName", f"Grupo {number[:8]}")
                            
                        novo_lead = Contact(
                            id=number,
                            name=contact_name,
                            phone=number if not is_group and not is_newsletter else None,
                            last_interaction=datetime.datetime.utcnow(),
                            status="group" if is_group else ("newsletter" if is_newsletter else "lead")
                        )
                        session.add(novo_lead)
                    session.commit()
                    logger.info(f"💾 [CRM Contact] {event_type} para {number} processado no PostgreSQL.")
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar Contato no PostgreSQL via Celery: {e}")

        # 0.5. Lock de Concorrência (Evita disparos duplicados se o usuário mandar 5 msgs seguidas)
        lock_key = f"ia_processing_lock:{number}"
        if r.get(lock_key):
            logger.warning(f"⏳ [Concurrency Lock] Já existe uma tarefa de IA em curso para {number}. Ignorando esta mensagem.")
            return {"status": "ignored", "reason": "concurrent_processing"}
        
        # Define um lock curto (30s) para o processamento da IA
        r.setex(lock_key, 30, "active")

        # 0. Registrar / Atualizar Lead no CRM Permanente (Tabela Contact)
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

        instance_name = payload.get("instance", "Hana_Intel_PRO")
        logger.info(f"📱 [WhatsApp Incoming] de {remote_jid} (Instância: {instance_name}): {texto_msg}")
        
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
        
        logger.info(f"🧠 [IA Thinking] Analisando mensagem de {number}...")
        resposta = crew_social_media.process_social_comment(wa_context)
        
        logger.info(f"✅ [IA Responded] Resposta gerada para {number}")
        
        # Assim que a IA responde, gravamos a resposta dela no histórico do Redis
        r.rpush(history_key, f"[Hana IA]: {resposta}")
        r.ltrim(history_key, -10, -1)
        
        # Enviar a resposta de volta via Evolution API
        try:
            evo_url = os.getenv("EVOLUTION_API_URL")
            evo_token = os.getenv("EVOLUTION_API_TOKEN")
            
            if not evo_url or not evo_token:
                logger.error("❌ [Config Error] EVOLUTION_API_URL ou TOKEN não definidos no .env!")
                return {"status": "error", "reason": "missing_config"}

            send_url = f"{evo_url.rstrip('/')}/message/sendText/{instance_name}"
            headers = {
                "apikey": evo_token,
                "Content-Type": "application/json"
            }
            body = {
                "number": number,
                "text": resposta
            }
            
            logger.info(f"📤 [WhatsApp Sending] para {number} via {instance_name}...")
            resp = requests.post(send_url, json=body, headers=headers, timeout=15)
            
            if resp.status_code in (200, 201):
                logger.info(f"✅ [WhatsApp Success] Resposta enviada para {number}")
            else:
                logger.error(f"❌ [WhatsApp Error] Falha Evolution API. Status: {resp.status_code}, Body: {resp.text}")
                
        except Exception as e:
            logger.error(f"❌ [WhatsApp Critical] Falha ao disparar resposta: {e}")
            r.delete(lock_key) # Garante que o lock morra no erro
        
        # Ao finalizar (sucesso ou erro), removemos o lock para permitir a próxima interação
        r.delete(lock_key)
        return {"status": "success", "event": event_type, "remote_jid": remote_jid}
        
    else:
        logger.warning(f"⚠️ Evento Evolution ignorado ou não tratado: {event_type}")
        return {"status": "ignored", "event": event_type}
