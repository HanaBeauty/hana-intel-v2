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

class ShopifyCustomerSync:
    """
    Integração de Extração de Clientes Shopify (CRM) para o Banco Contact.
    Cruza o Telefone do Checkout com os Logs do WhatsApp.
    """
    def __init__(self):
        self.store_url = os.getenv("SHOPIFY_STORE_URL")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = "2024-01"
        if self.store_url:
            self.base_url = f"https://{self.store_url}/admin/api/{self.api_version}"
        else:
            self.base_url = None

    async def run_sync_job(self):
        from src.models import Contact
        import datetime
        import httpx
        import asyncio
        import re
        from sqlalchemy.future import select
        from src.database import async_session_maker, engine, Base
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔄 Iniciando rotina Massiva de Sincronização Shopify Clientes -> CRM Contacts...")
        if not async_session_maker or not self.base_url:
            logger.error("❌ Credenciais Shopify ausentes para sync de Clientes.")
            return

        # Garantir que as tabelas existem (especialmente em novas bases)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        next_url = f"{self.base_url}/customers.json?limit=250"
        total_processed = 0
        
        async with httpx.AsyncClient() as client:
            async with async_session_maker() as session:
                while next_url:
                    try:
                        logger.info(f"📥 Buscando lote (URL: {next_url.split('?')[1][:40]}...)")
                        response = await client.get(next_url, headers=headers, timeout=30.0)
                        
                        if response.status_code == 429:
                            logger.warning("⚠️ Rate Limit da Shopify atingido (HTTP 429). Pausando por 5 segundos...")
                            await asyncio.sleep(5)
                            continue # Tenta a mesma URL de novo
                            
                        response.raise_for_status()
                        
                        customers = response.json().get("customers", [])
                        if not customers:
                            break
                            
                        lote_stats = {"added": 0, "updated": 0, "ignored": 0}
                        for cust in customers:
                            shopify_id = cust.get("id")
                            phone = cust.get("phone") or cust.get("default_address", {}).get("phone")
                            
                            # ID Primário: Preferência por Telefone Clean, senão ID Shopify
                            phone_clean = None
                            if phone:
                                phone_clean = ''.join(filter(str.isdigit, str(phone)))
                                if len(phone_clean) in (10, 11):
                                    phone_clean = f"55{phone_clean}"
                            
                            # Se não tem telefone, usamos o ID da Shopify como ID do contato
                            contact_id = phone_clean if phone_clean else f"shp_{shopify_id}"
                            
                            # Busca por ID primário ou Telefone (se existir)
                            existing_contact = None
                            if phone_clean:
                                query = select(Contact).where((Contact.id == contact_id) | (Contact.phone == phone_clean))
                            else:
                                query = select(Contact).where(Contact.id == contact_id)
                                
                            result = await session.execute(query)
                            existing_contact = result.scalars().first()
                            
                            nome = f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip()
                            email = cust.get("email")
                            total_spent = str(cust.get("total_spent", "0.0"))
                            
                            if existing_contact:
                                if nome:
                                    existing_contact.name = nome
                                if email:
                                    existing_contact.email = email
                                existing_contact.total_spent = total_spent
                                # Atualiza o telefone se ele era nulo e agora temos (caso raro de merge mas util)
                                if phone_clean and not existing_contact.phone:
                                    existing_contact.phone = phone_clean
                                lote_stats["updated"] += 1
                            else:
                                novo_contact = Contact(
                                    id=contact_id,
                                    name=nome or f"Cliente Shopify {shopify_id}",
                                    phone=phone_clean,
                                    email=email,
                                    total_spent=total_spent,
                                    last_interaction=datetime.datetime.utcnow(),
                                    status="client"
                                )
                                session.add(novo_contact)
                                lote_stats["added"] += 1
                                
                        # Commit parcial por lote pra não estourar RAM / Tabela
                        await session.commit()
                        total_processed += len(customers)
                        logger.info(f"✅ Lote OK! [Novos: {lote_stats['added']} | Updates: {lote_stats['updated']}] - Total no CRM: {total_processed}")
                        
                        # Parse do Link Header para Paginação Segura
                        link_header = response.headers.get("Link")
                        next_url = None
                        if link_header:
                            # A sintaxe do Link header da shopify é: <url>; rel="next", <url>; rel="previous"
                            links = link_header.split(",")
                            for link in links:
                                if 'rel="next"' in link:
                                    match = re.search(r'<(.*?)>', link)
                                    if match:
                                        next_url = match.group(1)
                                        
                    except httpx.HTTPError as e:
                        logger.error(f"❌ Erro HTTP na comunicação com Shopify: {e}")
                        break
                    except Exception as e:
                        logger.error(f"❌ Erro Severo na Sincronização de Clientes: {e}")
                        await session.rollback()
                        break
                        
        logger.info(f"🎉 Sincronização Massiva Concluída! 🎉 Importados/Atualizados: {total_processed}")

shopify_customer_sync_service = ShopifyCustomerSync()
