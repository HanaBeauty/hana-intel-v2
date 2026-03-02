from src.celery_app import celery_app
from src.database import async_session_maker
from src.models import Campaign, CampaignStatus
from src.agents_crew import crew_content_lab
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

# Definição das Linhas Editoriais para o Nurture Hub
linhas_editoriais = [
    ("Técnicas de Retenção", "Dê uma dica sobre como a umidade do ambiente afeta a polimerização do adesivo."),
    ("Cuidados Pós-Procedimento", "Explique a importância de não molhar as extensões nas primeiras 24h."),
    ("Diferencial Hana Beauty", "Fale sobre a tecnologia japonesa por trás dos nossos adesivos ETIL."),
    ("Venda Consultiva", "Como explicar para a cliente que o 'barato sai caro' na saúde dos olhos."),
    ("Mentalidade Ouro", "Uma frase motivacional para Lash Designers que buscam faturar mais de 20k/mês.")
]

async def run_nurture_logic():
    """Lógica assíncrona do Motor Autônomo de Nutrição"""
    logger.info("Iniciando Motor de Nutrição (Nurture Hub) Hana Intel...")
    
    async with async_session_maker() as db:
        
        # Sorteia o canal (WhatsApp ou Email)
        canal_sorteado = random.choice(["whatsapp", "email"])
        tema_sorteado, instrucao = random.choice(linhas_editoriais)
        
        contexto = (
            f"Sua missão é gerar um conteúdo de NUTRIÇÃO para a comunidade de Lash Designers Ouro da Hana Beauty.\n"
            f"Linha Editorial Sorteada: {tema_sorteado}\n"
            f"Canal de Destino: {canal_sorteado.upper()}\n"
            f"Instrução: {instrucao}\n\n"
        )
        
        if canal_sorteado == "whatsapp":
            contexto += (
                "Escreva diretamente o texto pronto para ser enviado no WHATSAPP VIP.\n"
                "Use Emojis elegantes (✨, 🤍, 🏆) e evite exageros. Seja direta, não pareça um robô."
            )
        else:
            contexto += (
                "Escreva um E-MAIL PREMIUM. Você DEVE seguir o layout 'PREMIUM GOLD TEMPLATE'.\n"
                "Garanta que o HTML retornado seja válido e luxuoso."
            )
        
        try:
            logger.info(f"Enviando para o CrewAI (Content Lab) - Tema: {tema_sorteado} | Canal: {canal_sorteado}")
            # Envia para a thread pool do agent para não bloquear o event loop do celery
            copy_gerada = await asyncio.to_thread(crew_content_lab.process_campaign, contexto, canal_sorteado)
            
            nova_nutricao = Campaign(
                title=f"[Nurture Hub] {canal_sorteado.capitalize()}: {tema_sorteado}",
                intent="Nurture (Nutrição de Base)",
                channel=canal_sorteado,
                target_audience="Clientes Opt-In VIP (Tag: Ouro)",
                generated_content=copy_gerada,
                status=CampaignStatus.draft
            )
            
            db.add(nova_nutricao)
            await db.commit()
            logger.info(f"✅ Nurture Hub: Conteúdo ({canal_sorteado}) gerado e enviado ao deck de aprovação!")
            
            # Telemetria de Sucesso
            try:
                import redis
                import json
                r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
                log_entry = {"time": "Agora", "origin": "NURTURE_AI", "action": "GENERATION_SUCCESS", "dest": f"Novo conteúdo: {tema_sorteado}"}
                r.lpush("dashboard_logs", json.dumps(log_entry))
                r.ltrim("dashboard_logs", 0, 19)
            except:
                pass
            
        except Exception as e:
            error_msg = f"Erro Nurture AI: {str(e)[:100]}"
            logger.error(error_msg)
            try:
                import redis
                import json
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                r = redis.Redis.from_url(redis_url, decode_responses=True)
                log_entry = {"time": "Agora", "origin": "NURTURE_AI", "action": "GENERATION_ERROR", "dest": error_msg}
                r.lpush("dashboard_logs", json.dumps(log_entry))
                r.ltrim("dashboard_logs", 0, 19)
            except:
                pass

@celery_app.task(name="tasks.nurture_hub_generator")
def nurture_hub_task():
    """
    Worker autônomo. Roda em background segundo o schedule cron.
    Gera as dicas do Calendário Editorial no Nurture Hub (Tabela Campaign com status draft).
    """
    logger.info("Celery [nurture_hub_task] disparada.")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_nurture_logic())
    return {"status": "success", "message": "Insight Nurture gerado."}
