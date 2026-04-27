from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(150), index=True, nullable=False)
    interaction_type = Column(String(80), default="Meeting")
    topics = Column(Text, default="")
    materials_shared = Column(Text, default="")
    samples_discussed = Column(Text, default="")
    outcome = Column(String(50), default="Neutral")
    objections = Column(Text, default="")
    follow_up = Column(Text, default="")
    sentiment = Column(String(50), default="Neutral")
    ai_summary = Column(Text, default="")
    raw_note = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
