import asyncio
import csv
import os
import sys
import datetime
import logging

# Configuração de Caminhos
sys.path.append(os.getcwd())

from sqlalchemy import select
from src.database import async_session_maker
from src.models import Contact

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CSVImport")

CSV_PATH = "/Users/takimotojuliano/.gemini/antigravity/Hana Intel/hana-intel/shopify_customers_export_26-02-2026.csv"

def clean_phone(phone_str):
    if not phone_str or phone_str == "":
        return None
    # Remove tudo que não é dígito
    digits = ''.join(filter(str.isdigit, str(phone_str)))
    if not digits:
        return None
    # Adiciona prefixo 55 se parecer um número brasileiro sem DDI
    if len(digits) in (10, 11):
        digits = f"55{digits}"
    return digits

async def run_import():
    if not os.path.exists(CSV_PATH):
        logger.error(f"❌ Arquivo CSV não encontrado em: {CSV_PATH}")
        return

    logger.info(f"🚀 Iniciando importação de contatos via CSV: {CSV_PATH}")
    
    stats = {"added": 0, "updated": 0, "errors": 0}
    
    async with async_session_maker() as session:
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            # O CSV parece usar vírgula, mas tem aspas em alguns campos com vírgula interna
            reader = csv.DictReader(f)
            
            # Lendo em lotes de 100 para eficiência
            batch_size = 100
            current_batch = []
            
            for row in reader:
                try:
                    customer_id = row.get("Customer ID", "").strip().replace("'", "")
                    first_name = row.get("First Name", "").strip()
                    last_name = row.get("Last Name", "").strip()
                    email = row.get("Email", "").strip()
                    if not email:
                        email = None
                    
                    # Hierarquia de Telefone: Phone > Default Address Phone
                    raw_phone = row.get("Phone", "").strip().replace("'", "")
                    if not raw_phone:
                        raw_phone = row.get("Default Address Phone", "").strip().replace("'", "")
                    
                    phone_clean = clean_phone(raw_phone)
                    nome = f"{first_name} {last_name}".strip()
                    
                    # ID do contato segue a lógica do sync: phone_clean ou shp_ID
                    contact_pk = phone_clean if phone_clean else f"shp_{customer_id}"
                    
                    # Busca se já existe
                    query = select(Contact).where(Contact.id == contact_pk)
                    result = await session.execute(query)
                    existing = result.scalars().first()
                    
                    if existing:
                        # Atualiza dados
                        if nome:
                            existing.name = nome
                        existing.email = email
                        # Se tinhamos shp_ID e agora temos telefone (ou vice-versa), mantemos consistência
                        if phone_clean and not existing.phone:
                            existing.phone = phone_clean
                        stats["updated"] += 1
                    else:
                        # Cria novo
                        new_contact = Contact(
                            id=contact_pk,
                            name=nome or f"Cliente Shopify {customer_id}",
                            phone=phone_clean,
                            email=email,
                            total_spent=row.get("Total Spent", "0.0").strip(),
                            last_interaction=datetime.datetime.utcnow(),
                            status="client"
                        )
                        session.add(new_contact)
                        stats["added"] += 1
                    
                    if (stats["added"] + stats["updated"]) % batch_size == 0:
                        await session.commit()
                        logger.info(f"⏳ Processados: {stats['added'] + stats['updated']} | Novos: {stats['added']} | Updates: {stats['updated']}")

                except Exception as e:
                    logger.error(f"❌ Erro ao processar linha {row.get('Customer ID')}: {e}")
                    stats["errors"] += 1
            
            await session.commit()
            
    logger.info("=" * 60)
    logger.info(f"✅ IMPORTAÇÃO CONCLUÍDA!")
    logger.info(f"✨ Novos Contatos: {stats['added']}")
    logger.info(f"🔄 Contatos Atualizados: {stats['updated']}")
    logger.info(f"⚠️ Erros: {stats['errors']}")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_import())
