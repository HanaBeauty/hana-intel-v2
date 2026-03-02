import asyncio
import sys
import os
import logging

# Garante import do src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.shopify_sync import shopify_customer_sync_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MassiveSync")

async def run_massive_sync():
    from src.database import database_url
    
    print("=" * 60)
    print("🚀 HANA INTEL V2 - MOTOR DE IMPORTAÇÃO MASSIVA (BULLETPROOF)")
    print("=" * 60)
    
    # Mascarar URL do banco para segurança
    db_info = "Localhost/Unknown"
    if database_url:
        if "@" in database_url:
            db_info = database_url.split("@")[-1] # Pega o host:porta/db
        else:
            db_info = database_url
            
    print(f"📍 Destino: {db_info}")
    print("-" * 60)
    print("Este módulo utiliza cursores para paginação segura e")
    print("controla automaticamente limites de requisição da API (HTTP 429).")
    print("=" * 60)
    
    await shopify_customer_sync_service.run_sync_job()
    
    print("=" * 60)
    print("✅ CARGA COMPLETA! Cancele este script a qualquer momento (Ctrl+C).")

if __name__ == "__main__":
    try:
        asyncio.run(run_massive_sync())
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo abortado pelo usuário. Fique tranquilo, todos os lotes 100% processados até agora já foram salvos com segurança no PostgreSQL.")
        sys.exit(0)
