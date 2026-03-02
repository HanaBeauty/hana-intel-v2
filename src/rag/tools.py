from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any
import logging
from src.rag.ingestion import ingestion_pipeline
# from src.database import get_db_session

logger = logging.getLogger(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from src.models import ProductKnowledge

sync_url = os.getenv("DATABASE_URL", "postgresql://hana_admin:c0c1164a842da069a9a9@hana-db:5432/hana_intel")
if sync_url.startswith("postgres://"):
    sync_url = sync_url.replace("postgres://", "postgresql://", 1)
if sync_url.startswith("postgresql+asyncpg://"):
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)

sync_engine = None
try:
    sync_engine = create_engine(sync_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
except Exception as e:
    logger.error(f"Failed to bind sync engine: {e}")
    SessionLocal = None

class SearchCatalogInput(BaseModel):
    query: Any = Field(..., description="O produto que deseja buscar no catálogo. Ex: 'Pincel chanfrado para unhas'")

class SearchCatalogTool(BaseTool):
    name: str = "Pesquisar Produtos no Site"
    description: str = (
        "Use esta ferramenta sempre que precisar saber quais produtos a Hana Beauty vende, "
        "seus preços e detalhes de estoque. NUNCA invente preços ou nomes de produtos."
    )
    args_schema: Type[BaseModel] = SearchCatalogInput

    def _run(self, query: Any) -> str:
        # Se a IA enviar um dicionário JSON acidentalmente (ex: {'description': 'unhas'})
        if isinstance(query, dict):
            query = query.get('description', str(query))
            
        logger.info(f"🔎 [SearchCatalogTool] Agente pesquisando por: '{query}'")
        
        # 1. Transformar a 'query' em Embedding
        vector_query = ingestion_pipeline.generate_embedding(str(query))
        
        if not SessionLocal:
            return "ALERTA DA TRANSAÇÃO: Banco de dados indisponível no momento."
            
        try:
            with SessionLocal() as session:
                # Busca Semântica Real no PostgreSQL (RAG)
                # Ordena pelos vetores mais próximos (menor distância cosseno) e pega os top 4
                results = session.query(ProductKnowledge).order_by(
                    ProductKnowledge.embedding.cosine_distance(vector_query)
                ).limit(4).all()
                
                if results:
                    formatted_results = "Catálogo Retornado da HANA BEAUTY (Dados Oficiais):\n"
                    for r in results:
                        formatted_results += f"- {r.name} (Categoria: {r.category}) - Preço: {r.price}\n  Detalhes: {r.description[:100]}...\n\n"
                    return formatted_results
                else:
                    return "ALERTA DA TRANSAÇÃO: Nenhum produto foi encontrado no estoque. VOCÊ DEVE RESPONDER AO CLIENTE QUE A HANA BEAUTY NÃO TRABALHA COM ESTE PRODUTO ATUALMENTE. NÃO INVENTE OUTRO NOME."
        except Exception as e:
            logger.error(f"Erro no banco vetorial: {e}")
            return "ALERTA: Erro ao buscar dados reais. Responda que o sistema de estoque está offline no momento."
