import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Vidya V3 - Group 4: Real-Time AI Tutor (Market Tier Build)")

# Verify local API key environment activation
gemini_key = os.environ.get("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)

TARGET_MODEL = "gemini-2.5-flash"

# =====================================================================
# GROUP 4 STRICT SCHEMAS WITH ADVANCED PERSONA METRICS
# =====================================================================
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class TutorRequest(BaseModel):
    skill_topic: str
    mastery_level: float
    icp_type: Literal["high_wage", "low_wage"]
    ca_phase: Literal["MODEL", "COACH", "SCAFFOLD", "FADE"]
    conversation_history: List[Message]

class LearnerSignals(BaseModel):
    # Original Psychological Signals
    confidence_level: Literal["LOW", "MEDIUM", "HIGH"]
    motivation_profile: Literal["INTRINSIC", "EXTRINSIC", "DEFENSIVE"]
    cognitive_friction: Literal["NONE", "MILD", "HIGH"]
    
    # NEW EXPANDED PSYCHOLINGUISTIC SIGNALS
    engagement_velocity: Literal["ACCELERATING", "STAGNANT", "DROPPING"]
    conceptual_certainty: Literal["SPECULATIVE", "ASSERTIVE", "CONFUSED"]
    frustration_index: Literal["LOW", "MEDIUM", "HIGH"]
    knowledge_retrieval_depth: Literal["SURFACE", "STRUCTURAL", "SYNTACTIC"]
    linguistic_alignment: Literal["HIGH", "MEDIUM", "LOW"]

class PerformanceDelta(BaseModel):
    communication: float
    tech_depth: float
    behavioural: float
    system_design: float
    delivery: float

class TutorResponse(BaseModel):
    tutor_response: str
    updated_ca_phase: Literal["MODEL", "COACH", "SCAFFOLD", "FADE"]
    on_topic_flag: bool
    suggested_next_action: str
    learner_signals: LearnerSignals
    performance_delta: PerformanceDelta

# =====================================================================
# INFERENCE ENGINE UTILITIES
# =====================================================================
@app.post("/tutor/turn", response_model=TutorResponse)
async def tutor_turn(payload: TutorRequest):
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY inside environment.")

    # Access your externalized system prompt from the prompts package cleanly
    from app.prompts import SYSTEM_PROMPT_TEMPLATE
    
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        skill_topic=payload.skill_topic,
        mastery_level=payload.mastery_level,
        ca_phase=payload.ca_phase,
        icp_type=payload.icp_type
    )
    
    try:
        model = genai.GenerativeModel(
            model_name=TARGET_MODEL,
            # 🌟 LATENCY FIX: Locked temperature to 0.0 to maximize token completion generation speeds
            generation_config={"temperature": 0.0, "response_mime_type": "application/json"},
            system_instruction=system_prompt
        )
        
        history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in payload.conversation_history])
        response = model.generate_content(history_text if history_text else "Session start.")
        
        return TutorResponse.model_validate_json(response.text.strip())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))