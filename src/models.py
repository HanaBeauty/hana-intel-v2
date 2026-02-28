from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from src.database import Base

class ProductKnowledge(Base):
    __tablename__ = "products_knowledge_vector"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)
    price = Column(String)
    category = Column(String)
    
    # Vector column for 1536 dimensions (OpenAI text-embedding-3-small)
    embedding = Column(Vector(1536))
