import asyncio
import os
import sys

# Ajusta o PYTHONPATH para importar módulos locais
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.database import Base, database_url
from src.models import User, UserRole
from src.routers.auth_api import get_password_hash

async def seed_admin():
    print("🌱 Iniciando o Seeding C-Level do Banco de Dados...")
    
    # Criar engine e dar echo nas execuções para debugar
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Cria todas as tabelas caso não existam (migração forçada do BD)
    async with engine.begin() as conn:
        print("🔨 Construindo tabelas do sistema...")
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Verifica se o admin já existe
        from sqlalchemy.future import select
        result = await session.execute(select(User).where(User.email == "juliano@adsai.com.br"))
        admin = result.scalars().first()
        
        if admin:
            print(f"⚠️ Administrador {admin.email} já existente no banco de dados. Cancelando seed.")
        else:
            # Cria o admin padrão
            raw_password = "admin" # Em produção será gerada ou resetada no painel
            hashed = get_password_hash(raw_password)
            
            new_admin = User(
                name="Juliano Takimoto",
                email="juliano@adsai.com.br",
                hashed_password=hashed,
                phone="5511999999999", # Alterar depois para o seu WhatsApp no banco
                role=UserRole.ADMIN,
                is_active=1
            )
            
            session.add(new_admin)
            await session.commit()
            print(f"✅ Administrador {new_admin.email} criado com sucesso!")
            print(f"🔑 Use a senha: {raw_password} para acessar o primeiro boot.")
            
    await engine.dispose()
    print("🌱 Seed finalizado.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
