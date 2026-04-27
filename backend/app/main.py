from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .database import Base, engine, get_db
from .models import Interaction
from .schemas import InteractionCreate, InteractionUpdate, InteractionOut, ChatRequest, ChatResponse
from .agent import agent_graph, log_interaction_tool, edit_interaction_tool, search_hcp_profile_tool, suggest_followup_tool, summarize_notes_tool

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI-First CRM HCP Module", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def health():
    return {"status": "running", "module": "AI-First CRM HCP Log Interaction"}

@app.get("/interactions", response_model=List[InteractionOut])
def list_interactions(db: Session = Depends(get_db)):
    return db.query(Interaction).order_by(Interaction.id.desc()).all()

@app.post("/interactions", response_model=InteractionOut)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    return log_interaction_tool(db, payload.model_dump())

@app.put("/interactions/{interaction_id}", response_model=InteractionOut)
def update_interaction(interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)):
    updated = edit_interaction_tool(db, interaction_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(404, "Interaction not found")
    return updated

@app.delete("/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    item = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not item:
        raise HTTPException(404, "Interaction not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted successfully"}

@app.post("/agent/chat", response_model=ChatResponse)
def agent_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    state = agent_graph.invoke({"message": payload.message, "action": "", "extracted": {}, "result": {}})
    action = state["action"]
    data = state["extracted"]
    interactions = []
    reply = ""
    if action == "log_interaction":
        item = log_interaction_tool(db, data)
        interactions = [item]
        reply = f"Logged interaction for {item.hcp_name}. Suggested follow-up: {item.follow_up}"
    elif action == "search_hcp_profile":
        profile = search_hcp_profile_tool(data.get("hcp_name", payload.message))
        data = profile
        reply = "HCP profile fetched successfully."
    elif action == "suggest_followup":
        data = suggest_followup_tool(payload.message)
        reply = f"Recommended action: {data.get('action')}"
    elif action == "summarize_notes":
        data = summarize_notes_tool(payload.message)
        reply = data.get("summary", "Summary created.")
    else:
        reply = "Use edit from the interaction table for safe updates."
    return ChatResponse(tool_used=action, reply=reply, data=data, interactions=interactions)
