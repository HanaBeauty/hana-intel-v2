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

from sqlalchemy import DateTime, Enum
import enum
import datetime

class CampaignStatus(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class Campaign(Base):
    """
    Tabela principal para gerenciar intenções, rascunhos e campanhas da Hana Intel.
    A IA cria aqui com status `draft` ou `pending_approval`.
    """
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    intent = Column(Text) # O que o usuário pediu para a IA fazer
    channel = Column(String) # email, whatsapp, instagram
    target_audience = Column(String) # Ex: clientes que compraram Adesivo Etil
    
    # O conteúdo gerado pela inteligência artificial
    generated_content = Column(Text, nullable=True)
    
    status = Column(Enum(CampaignStatus), default=CampaignStatus.draft)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

class CampaignDelivery(Base):
    """
    Tabela Anti-Loop: Garante que um lead jamais receba o mesmo disparo estrutural.
    """
    __tablename__ = "campaign_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, index=True) # Ligação lógica com a Campaign
    customer_contact = Column(String, index=True) # Email ou Telefone
    
    delivery_status = Column(String, default="sent") # sent, failed, opened
    error_message = Column(Text, nullable=True)
    
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
