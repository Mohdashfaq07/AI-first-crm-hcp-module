# AI-First CRM HCP Module – Log Interaction Screen

This project is a Round 1 assignment implementation for an AI-first Customer Relationship Management module focused on Healthcare Professional (HCP) interactions.

The solution provides two ways for a field representative to log an HCP interaction:

1. A structured form-based interface.
2. A conversational AI chat interface powered by LangGraph and Groq LLM.

## Tech Stack

### Frontend
- React
- Redux Toolkit
- Axios
- Google Inter font
- Responsive CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- LangGraph
- Groq LLM using `gemma2-9b-it`
- SQL database support: SQLite by default, PostgreSQL/MySQL supported through `DATABASE_URL`

## Key Features

- Log HCP interactions using a structured form.
- Log HCP interactions using natural language chat.
- AI extraction of HCP name, topics, sentiment, outcome, objections, follow-up and summary.
- Interaction history table.
- Edit logged interactions.
- SQL persistence.
- LangGraph workflow for routing and extraction.

## LangGraph Agent Role

The LangGraph agent acts as the intelligence layer between the field representative and the CRM database. It reads the representative's message, identifies the intended action, extracts structured CRM fields using the Groq LLM, and routes the request to the correct sales tool.

This helps the field representative save time, reduce manual typing, and maintain cleaner CRM data.

## Five LangGraph / Sales Tools

### 1. Log Interaction
Captures a new HCP interaction. The LLM extracts structured fields such as HCP name, discussion topics, sentiment, objections, outcome and follow-up action from a raw visit note.

### 2. Edit Interaction
Allows modification of already logged interaction data. This is useful when a representative wants to correct an HCP name, update a summary, or change a follow-up action.

### 3. Search HCP Profile
Fetches HCP profile information such as speciality, location and potential. In a production system, this would connect to a master HCP database.

### 4. Suggest Follow-up Action
Recommends the next best action based on the interaction note. For example, sharing pricing, scheduling a revisit, or sending medical literature.

### 5. Summarize Visit Notes
Converts long representative notes into a short CRM-friendly summary with key topics, sentiment and next steps.

## Project Structure

```text
hcp_crm_task1/
  backend/
    app/
      main.py
      agent.py
      database.py
      models.py
      schemas.py
    requirements.txt
    .env.example
  frontend/
    src/
      main.jsx
      style.css
      store/store.js
    package.json
    .env.example
```

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq API key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=gemma2-9b-it
DATABASE_URL=sqlite:///./hcp_crm.db
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

API Docs:

```text
http://localhost:8000/docs
```

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Demo Prompt for AI Chat

Use this prompt in the AI assistant box:

```text
Met Dr Sharma today. Discussed new diabetes product. Doctor was interested but asked for pricing details next week. Shared product brochure and discussed sample availability.
```

Expected AI output:

- Logs the interaction.
- Extracts HCP name.
- Creates summary.
- Detects sentiment.
- Suggests follow-up action.

## Code Flow

1. User enters data through the React form or AI chat panel.
2. Redux sends the request to FastAPI.
3. FastAPI passes chat requests to the LangGraph agent.
4. LangGraph classifies the intent and extracts structured fields.
5. The selected tool executes the action.
6. SQLAlchemy saves or updates records in the database.
7. React refreshes the interaction history table.

## Video Walkthrough Script

1. Introduce the project as an AI-first CRM HCP Log Interaction module.
2. Explain the two input modes: structured form and AI chat.
3. Demonstrate saving an interaction from the form.
4. Demonstrate logging through AI chat using a natural sales visit note.
5. Show the interaction history table.
6. Edit one logged interaction.
7. Explain the five tools: Log Interaction, Edit Interaction, Search HCP Profile, Suggest Follow-up and Summarize Notes.
8. Explain the architecture: React + Redux → FastAPI → LangGraph → Groq → SQL database.
9. End with what you understood: the goal is to reduce field rep manual effort and improve CRM data quality.

## Notes

The project uses SQLite by default to make local demo simple. For production, replace `DATABASE_URL` with PostgreSQL or MySQL connection string.
