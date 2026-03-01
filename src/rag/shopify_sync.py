import os
import json
import logging
import httpx
from sqlalchemy.future import select
from src.database import async_session_maker
from src.models import ProductKnowledge
from src.rag.ingestion import ingestion_pipeline

logger = logging.getLogger(__name__)

class ShopifyKnowledgeSync:
    """
    Integração de Extração do Catálogo Shopify (ETL) para o VectorDB.
    """
    def __init__(self):
        self.store_url = os.getenv("SHOPIFY_STORE_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = "2024-01"
        
        if self.store_url:
            self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"
        else:
            self.base_url = None

    async def fetch_active_products(self) -> list[dict]:
        """Busca produtos ativos com suas variantes de preço na Shopify."""
        if not self.base_url or not self.access_token:
            logger.error("🚫 Credenciais da Shopify ausentes. Abortando sync.")
            return []

        url = f"{self.base_url}/products.json?status=active&limit=250"
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

        products_data = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                for prod in data.get("products", []):
                    # Extrair o menor preço das variantes como preço base
                    variants = prod.get("variants", [])
                    base_price = min([float(v.get("price", "0.0")) for v in variants]) if variants else 0.0
                    
                    product_info = {
                        "id": str(prod["id"]),
                        "name": prod.get("title", ""),
                        "description": prod.get("body_html", "Sem descrição"),
                        "price": f"R$ {base_price:.2f}".replace(".", ","),
                        "category": prod.get("product_type", "Geral"),
                        "tags": prod.get("tags", "")
                    }
                    products_data.append(product_info)
                    
                logger.info(f"✅ {len(products_data)} produtos extraídos da Shopify (com tags técnicas).")
                return products_data
            
            except Exception as e:
                logger.error(f"❌ Falha ao buscar produtos Shopify: {e}")
                return []

    async def run_sync_job(self):
        """Executa o pipeline completo: Extrai -> Transforma em Vetor -> Salva no Banco"""
        logger.info("🔄 Iniciando rotina de Sincronização Shopify -> VectorDB...")
        
        if not async_session_maker:
            logger.error("❌ Banco de dados não inicializado.")
            return

        products = await self.fetch_active_products()
        if not products:
            logger.warning("Nenhum produto para sincronizar.")
            return

        async with async_session_maker() as session:
            try:
                for prod in products:
                    # Checar se produto já existe
                    query = select(ProductKnowledge).where(ProductKnowledge.product_id == prod["id"])
                    result = await session.execute(query)
                    existing_prod = result.scalars().first()
                    
                    # Formatar string rica para vetorização
                    text_to_embed = f"Produto: {prod['name']}. Categoria: {prod['category']}. Tags: {prod.get('tags', '')}. Preço: {prod['price']}. Detalhes: {prod['description']}"
                    
                    # Gerar Embedding
                    embedding_vector = ingestion_pipeline.generate_embedding(text_to_embed)
                    
                    if existing_prod:
                        logger.info(f"Atualizando produto existente: {prod['name']}")
                        existing_prod.name = prod['name']
                        existing_prod.description = prod['description']
                        existing_prod.price = prod['price']
                        existing_prod.category = prod['category']
                        existing_prod.embedding = embedding_vector
                    else:
                        logger.info(f"Criando novo conhecimento para: {prod['name']}")
                        new_prod = ProductKnowledge(
                            product_id=prod["id"],
                            name=prod["name"],
                            description=prod["description"],
                            price=prod["price"],
                            category=prod["category"],
                            embedding=embedding_vector
                        )
                        session.add(new_prod)
                
                await session.commit()
                logger.info("🎉 Sincronização Vetorial Shopify concluída com sucesso.")
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Erro fatal ao gravar no banco vetorial: {e}")

shopify_sync_service = ShopifyKnowledgeSync()
