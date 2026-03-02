import asyncio
from src.database import engine, Base, get_db_session, async_session_maker
from src.models import Contact
from src.routers.dashboard_api import get_contacts_list
import datetime

async def test():
    # Setup in-memory sqlite for test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with async_session_maker() as session:
        session.add(Contact(
            id="5511999999999",
            name="Juliano",
            phone="5511999999999",
            email="test@test.com",
            total_spent="100.0",
            status="lead",
            tags="vip",
            last_interaction=datetime.datetime.utcnow()
        ))
        await session.commit()
        
    async with async_session_maker() as session:
        try:
            res = await get_contacts_list(session)
            print("SUCCESS! Output:")
            print(res)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test())
