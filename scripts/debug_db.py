import asyncio
import os
from sqlalchemy.future import select
from src.database import async_session_maker
from src.models import Campaign, CampaignStatus

async def debug_campaigns():
    print("--- Debugging Campaigns ---")
    async with async_session_maker() as session:
        query = select(Campaign)
        result = await session.execute(query)
        campaigns = result.scalars().all()
        
        print(f"Total campaigns found: {len(campaigns)}")
        for c in campaigns:
            try:
                print(f"ID: {c.id} | Status: {c.status} | Title: {c.title}")
                # Test the serialization that happens in the API
                data = {
                    "id": c.id,
                    "title": c.title,
                    "intent": c.intent,
                    "channel": c.channel,
                    "audience": c.target_audience,
                    "content": c.generated_content,
                    "status": c.status.value if c.status else None,
                    "created_at": str(c.created_at)
                }
                print(f"  OK: {data['status']}")
            except Exception as e:
                print(f"  ERROR on ID {c.id}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_campaigns())
