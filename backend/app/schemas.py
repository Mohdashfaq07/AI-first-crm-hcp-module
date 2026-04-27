from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class InteractionBase(BaseModel):
    hcp_name: str
    interaction_type: str = "Meeting"
    topics: str = ""
    materials_shared: str = ""
    samples_discussed: str = ""
    outcome: str = "Neutral"
    objections: str = ""
    follow_up: str = ""
    sentiment: str = "Neutral"
    ai_summary: str = ""
    raw_note: str = ""

class InteractionCreate(InteractionBase):
    pass

class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = None
    topics: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_discussed: Optional[str] = None
    outcome: Optional[str] = None
    objections: Optional[str] = None
    follow_up: Optional[str] = None
    sentiment: Optional[str] = None
    ai_summary: Optional[str] = None
    raw_note: Optional[str] = None

class InteractionOut(InteractionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    tool_used: str
    reply: str
    data: Dict[str, Any] = {}
    interactions: List[InteractionOut] = []
