import asyncio
from src.database import async_session_maker
from src.models import Contact
from sqlalchemy.future import select

async def get_count():
    async with async_session_maker() as session:
        query = select(Contact).order_by(Contact.last_interaction.desc()).limit(10)
        result = await session.execute(query)
        data = result.scalars().all()
        print(f"Contacts in DB: {len(data)}")
        if data:
            for c in data:
                print(f"Contact: {c.id}, {c.name}, {c.total_spent}, interaction: {c.last_interaction}")

asyncio.run(get_count())
