import os
import json
import logging
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
# from src.database import engine, Base
# from src.models import KnowledgeBase

logger = logging.getLogger(__name__)

class CatalogIngestionPipeline:
    """
    Transforma texto cru e JSONs de produtos em Embeddings Matemáticos (pgvector)
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=self.api_key)
        else:
            self.embeddings_model = None
            
    def generate_embedding(self, text: str) -> list[float]:
        """Gera o vetor de 1536 dimensões"""
        if not self.embeddings_model:
            logger.warning("OPENAI_API_KEY ausente. Teste mock de embedding.")
            return [0.0] * 1536
        return self.embeddings_model.embed_query(text)

    def process_and_save_products(self, products_list: list[dict], db_session: Session):
        """
        Recebe a lista: [{'id': 1, 'name': 'Pincel', 'desc': '...', 'price': '10.0'}]
        """
        logger.info(f"🔄 Iniciando vetorização de {len(products_list)} produtos...")
        # Lógica futura: Para cada produto, concatenar texto (nome + desc + preço), vetorizar, e salvar no db_session com Modelo SQLAlchemy = KnowledgeBase
        logger.info("✅ Pipeline de Ingestão executado (Mock). Banco Híbrido requer auth de gravação setada.")

ingestion_pipeline = CatalogIngestionPipeline()
