from src.celery_app import celery_app
from src.database import async_session_maker
from src.models import Campaign, CampaignStatus
from src.agents_crew import crew_content_lab
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

async def run_nurture_logic():
    """Lógica assíncrona do Motor Autônomo de Nutrição"""
    logger.info("Iniciando Motor de Nutrição (Nurture Hub) Hana Intel...")
    
    async with async_session_maker() as db:
        
        # Sorteia uma linha editorial
        linhas_editoriais = [
            ("Técnica: Umidade e Retenção", "Dê uma dica sobre como a umidade afeta o Adesivo Etil, e sugira o uso pontual de higienizador. Tom: Especialista e prestativo."),
            ("Gestão: Precificação de Serviços", "Escreva um post inspiracional dizendo para a Lash Designer não brigar por preço, e sim vender a durabilidade do alongamento (retenção) como diferencial. Tom: Empoderamento e Posicionamento Premium."),
            ("Oferta Oculta: Kit Completo", "Fale sobre a importância de usar a linha inteira (Adesivo + Preparador + Removedor) da mesma marca (Hana Beauty) para não dar reação química, e chame para ver o catálogo.")
        ]
        
        tema_sorteado, instrucao = random.choice(linhas_editoriais)
        
        contexto = (
            f"Sua missão é gerar um conteúdo de NUTRIÇÃO para a comunidade de Lash Designers Ouro da Hana Beauty.\n"
            f"Linha Editorial Sorteada: {tema_sorteado}\n"
            f"Instrução: {instrucao}\n\n"
            f"Escreva diretamente o texto pronto para ser enviado no WHATSAPP VIP.\n"
            f"Use Emojis elegantes (✨, 🤍, 🏆) e evite exageros. Seja direta, não pareça um robô."
        )
        
        try:
            logger.info(f"Enviando para o CrewAI (Content Lab) - Tema de Nutrição: {tema_sorteado}")
            # Envia para a thread pool do agent para não bloquear o event loop do celery
            copy_gerada = await asyncio.to_thread(crew_content_lab.process_campaign, contexto, "Dica de WhatsApp / Pílula de Conhecimento")
            
            nova_nutricao = Campaign(
                title=f"[Nurture Hub] Dica do Dia: {tema_sorteado}",
                intent="Nurture (Nutrição de Base)",
                channel="whatsapp",
                target_audience="Clientes Opt-In VIP (Tag: Ouro)",
                generated_content=copy_gerada,
                status=CampaignStatus.draft
            )
            
            db.add(nova_nutricao)
            await db.commit()
            
            logger.info(f"✅ Nurture Hub: Pílula de conhecimento gerada com sucesso e enviada ao deck de aprovação!")
            
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo de Nurture: {e}")

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
