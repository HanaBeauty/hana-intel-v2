from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any
import logging
from src.rag.ingestion import ingestion_pipeline
# from src.database import get_db_session

logger = logging.getLogger(__name__)

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
        
        # 2. Busca Semântica no PostgreSQL (Mock por enquanto)
        # return session.query(ProductKnowledge).order_by(ProductKnowledge.embedding.cosine_distance(vector_query)).limit(3).all()
        
        # Simulação do que o VectorDB vai retornar:
        if "pincel" in query.lower():
            return "Catálogo Retornado:\n1. Pincel Chanfrado Super Kolinsky (SKU: PC-001) - Preço: R$ 59,90 - Em estoque.\n2. Pincel Oval para Gel (SKU: PO-002) - Preço: R$ 45,00 - Em estoque."
        elif "lash" in query.lower() or "cílio" in query.lower():
            return "Catálogo Retornado:\n1. Cola Premium Amlash (SKU: CA-100) - Preço: R$ 120,00 - Baixo estoque.\n2. Removedor em Gel Amlash - Preço: R$ 65,00 - Em estoque."
        else:
            return "ALERTA DA TRANSAÇÃO: Nenhum produto foi encontrado no estoque. VOCÊ DEVE RESPONDER AO CLIENTE QUE A HANA BEAUTY NÃO TRABALHA COM ESTE PRODUTO ATUALMENTE. NÃO INVENTE OUTRO NOME."
