import json, os, re
from typing import Dict, Any, TypedDict
from groq import Groq
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from .models import Interaction

MODEL = os.getenv("GROQ_MODEL", "gemma2-9b-it")

class AgentState(TypedDict):
    message: str
    action: str
    extracted: Dict[str, Any]
    result: Dict[str, Any]

HCP_DIRECTORY = {
    "dr sharma": {"speciality": "Diabetologist", "location": "Bangalore", "potential": "High", "last_visit": "None"},
    "dr mehta": {"speciality": "Cardiologist", "location": "Mumbai", "potential": "Medium", "last_visit": "None"},
    "dr priya": {"speciality": "General Physician", "location": "Hyderabad", "potential": "High", "last_visit": "None"},
}

def _groq_json(prompt: str) -> Dict[str, Any]:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return {}
    try:
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}

def _fallback_extract(text: str) -> Dict[str, Any]:
    hcp = "Unknown HCP"
    match = re.search(r"Dr\.?\s+[A-Z][a-zA-Z]+", text)
    if match:
        hcp = match.group(0)
    sentiment = "Positive" if any(w in text.lower() for w in ["interested", "positive", "agreed", "happy"]) else "Neutral"
    outcome = "Positive" if sentiment == "Positive" else "Neutral"
    follow_up = "Schedule follow-up and share requested details."
    if "pricing" in text.lower():
        follow_up = "Share pricing details in the next follow-up."
    return {
        "hcp_name": hcp,
        "interaction_type": "Meeting",
        "topics": text[:220],
        "materials_shared": "Not specified",
        "samples_discussed": "Not specified",
        "outcome": outcome,
        "objections": "Not specified",
        "follow_up": follow_up,
        "sentiment": sentiment,
        "ai_summary": f"Interaction with {hcp}. Key discussion: {text[:180]}",
        "raw_note": text,
    }

def classify_action(state: AgentState) -> AgentState:
    msg = state["message"].lower()
    if "edit" in msg or "update" in msg or "change" in msg:
        action = "edit_interaction"
    elif "search" in msg or "profile" in msg or "find hcp" in msg:
        action = "search_hcp_profile"
    elif "follow" in msg or "next action" in msg or "recommend" in msg:
        action = "suggest_followup"
    elif "summarize" in msg or "summary" in msg:
        action = "summarize_notes"
    else:
        action = "log_interaction"
    state["action"] = action
    return state

def extract_info(state: AgentState) -> AgentState:
    prompt = f"""
Extract CRM HCP interaction fields from this sales representative note.
Return JSON only with keys: hcp_name, interaction_type, topics, materials_shared, samples_discussed, outcome, objections, follow_up, sentiment, ai_summary, raw_note.
Note: {state['message']}
"""
    data = _groq_json(prompt) or _fallback_extract(state["message"])
    state["extracted"] = data
    return state

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify_action", classify_action)
    graph.add_node("extract_info", extract_info)
    graph.set_entry_point("classify_action")
    graph.add_edge("classify_action", "extract_info")
    graph.add_edge("extract_info", END)
    return graph.compile()

agent_graph = build_graph()

# ----- Five sales tools used by LangGraph/API layer -----
def log_interaction_tool(db: Session, data: Dict[str, Any]) -> Interaction:
    interaction = Interaction(**{k: data.get(k, "") for k in [
        "hcp_name","interaction_type","topics","materials_shared","samples_discussed",
        "outcome","objections","follow_up","sentiment","ai_summary","raw_note"
    ]})
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

def edit_interaction_tool(db: Session, interaction_id: int, updates: Dict[str, Any]) -> Interaction | None:
    item = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not item:
        return None
    for key, value in updates.items():
        if hasattr(item, key) and value is not None:
            setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

def search_hcp_profile_tool(name: str) -> Dict[str, Any]:
    key = name.lower().replace(".", "").strip()
    return HCP_DIRECTORY.get(key, {"speciality": "Unknown", "location": "Unknown", "potential": "Not available"})

def suggest_followup_tool(note: str) -> Dict[str, Any]:
    prompt = f"Return JSON with keys action, priority, due_date, rationale for sales follow-up. Note: {note}"
    return _groq_json(prompt) or {"action": "Share requested information and schedule next visit", "priority": "Medium", "due_date": "Within 7 days", "rationale": "Keeps the HCP engaged after the discussion."}

def summarize_notes_tool(note: str) -> Dict[str, Any]:
    prompt = f"Summarize this HCP interaction. Return JSON keys summary, key_topics, sentiment, next_steps. Note: {note}"
    return _groq_json(prompt) or {"summary": note[:250], "key_topics": "Extracted from visit note", "sentiment": "Neutral", "next_steps": "Follow up with HCP."}
