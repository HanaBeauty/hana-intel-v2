import asyncio
import logging
import os
import sys

# Ajusta o sys.path para conseguirmos importar a src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import engine, Base
from src.rag.shopify_sync import shopify_sync_service, shopify_customer_sync_service
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run():
    logger.info("🔧 Inicializando Banco de Dados e Extensão pgvector...")
    if not engine:
        logger.error("Engine não inicializada. Verifique DATABASE_URL.")
        return

    async with engine.begin() as conn:
        # Tenta criar a extensão vector no PostgreSQL
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Cria as tabelas do SQLAlchemy (ProductKnowledge)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Tabelas e Extensão criadas.")
    
    logger.info("🚀 Iniciando Sincronização com Shopify (Produtos / VectorDB)...")
    await shopify_sync_service.run_sync_job()
    
    logger.info("👥 Iniciando Sincronização Shopify Clientes (CRM / Contacts)...")
    await shopify_customer_sync_service.run_sync_job()

if __name__ == "__main__":
    asyncio.run(run())
