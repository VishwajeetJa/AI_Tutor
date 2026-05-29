import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Literal, List
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Vidya V3 - Multi-Phase Dynamic AI Tutor Engine")

# ⚡ GLOBAL ACCELERATION SINGLETON
# Declared globally to warm up connection networks and prevent startup lag inside the socket handshake thread block.
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
GLOBAL_GENAI_CLIENT = genai.Client(api_key=gemini_key) if gemini_key else None

TARGET_MODEL = "gemini-2.0-flash"

# =====================================================================
# STRICT GROUP 4 TASK BRIEF SCHEMAS (100% ORIGINAL)
# =====================================================================
class LearnerSignals(BaseModel):
    confidence_level: Literal["LOW", "MEDIUM", "HIGH"]
    motivation_profile: Literal["INTRINSIC", "EXTRINSIC", "DEFENSIVE"]
    cognitive_friction: Literal["NONE", "MILD", "HIGH"]
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

class TutorTurnSchema(BaseModel):
    tutor_response: str
    updated_ca_phase: Literal["MODEL", "COACH", "SCAFFOLD", "FADE"]
    on_topic_flag: bool
    suggested_next_action: str
    learner_signals: LearnerSignals
    performance_delta: PerformanceDelta

class FinalReportSchema(BaseModel):
    overall_summary: str
    final_learner_signals: LearnerSignals
    final_skill_marks: PerformanceDelta

# =====================================================================
# ROUTING SYSTEMS CONTROLLERS
# =====================================================================
@app.get("/")
async def get():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(root_dir, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not GLOBAL_GENAI_CLIENT:
        await websocket.close(code=1011)
        return

    await websocket.accept()
    print("📡 Stateful Multi-Phase Conversation Loop Active.")

    # Fix 3: Keepalive ping task — prevents Render free-tier WebSocket idle timeout (55s default)
    async def _keepalive_ping():
        try:
            while True:
                await asyncio.sleep(30)
                await websocket.send_text(json.dumps({"type": "ping"}))
        except Exception:
            pass  # Connection closed, task exits silently

    keepalive_task = asyncio.create_task(_keepalive_ping())

    # Explicit phase-shifting transition layout constraints mapping
    SYSTEM_PREAMBLE = (
        "You are operating as Vidya AI, a warm coding tutor conducting a strict 10-turn dialogue lesson on Python functions and scopes.\n"
        "Your absolute core directive is to step the student through the Cognitive Apprenticeship (CA) framework.\n\n"
        "--- CRITICAL CA PHASE SHIFTING LOGIC RULES (DETERMINISTIC — FOLLOW EXACTLY) ---\n"
        "You MUST evaluate the phase transition on every turn using the strict binary decision tree below.\n"
        "Do NOT apply subjective judgment. Apply these IF/THEN rules in order and stop at the first match:\n\n"
        "STEP 1 — CHECK FOR REGRESSION (overrides all progression):\n"
        "  IF (cognitive_friction == HIGH) OR (frustration_index == HIGH):\n"
        "    → Regress one phase: MODEL stays MODEL, COACH→MODEL, SCAFFOLD→COACH, FADE→SCAFFOLD.\n"
        "    → Set updated_ca_phase to the regressed phase. STOP here.\n\n"
        "STEP 2 — CHECK FOR HOLD (no change):\n"
        "  IF (conceptual_certainty == CONFUSED):\n"
        "    → Keep current phase unchanged. STOP here.\n"
        "  IF (engagement_velocity == DROPPING) AND (frustration_index != LOW):\n"
        "    → Keep current phase unchanged. STOP here.\n\n"
        "STEP 3 — CHECK FOR MASTERY PROGRESSION (must satisfy ALL four simultaneously):\n"
        "  IF (confidence_level == HIGH) AND (cognitive_friction == NONE) AND (conceptual_certainty == ASSERTIVE) AND (frustration_index == LOW):\n"
        "    → Advance one phase: MODEL→COACH, COACH→SCAFFOLD, SCAFFOLD→FADE, FADE stays FADE.\n"
        "    → Set updated_ca_phase to the advanced phase. STOP here.\n\n"
        "STEP 4 — DEFAULT (none of the above conditions matched):\n"
        "    → Keep current phase unchanged.\n\n"
        "ANTI-STAGNATION OVERRIDE: If the active phase in context is MODEL or COACH and STEP 3 mastery conditions are ALL met, "
        "you are REQUIRED to advance the phase. Holding a learner in MODEL or COACH when mastery is confirmed is a calibration failure.\n\n"
        "--- REAL-TIME PSYCHOLINGUISTIC SIGNAL PROFILING CONTROLS ---\n"
        "Dynamically calculate psycholinguistic signals according to the depth of the user\'s last answer:\n"
        "- If user indicates confusion, says \'I don\'t know\', or stalls: confidence_level=\'LOW\', cognitive_friction=\'HIGH\', motivation_profile=\'DEFENSIVE\', conceptual_certainty=\'CONFUSED\'.\n"
        "- If user demonstrates clear comprehension or answers technical details accurately: confidence_level=\'HIGH\', cognitive_friction=\'NONE\', motivation_profile=\'INTRINSIC\', conceptual_certainty=\'ASSERTIVE\'.\n\n"
        "--- SKILL SCORE DELTA RULES (MANDATORY — MUST UPDATE EVERY SINGLE TURN) ---\n"
        "You MUST return a non-zero performance_delta on EVERY turn based on the user\'s answer. Never return all zeros.\n"
        "Calculate a delta between -1.00 and +1.00 for each axis based ONLY on the user\'s latest reply:\n"
        "- communication: clarity of explanation, vocabulary, sentence structure.\n"
        "- tech_depth: technical accuracy, correct use of Python concepts, syntax knowledge.\n"
        "- behavioural: ownership, persistence, composure, professionalism.\n"
        "- system_design: architectural thinking, scalability awareness, scoping.\n"
        "- delivery: speed of response, task focus, directness.\n"
        "SCORING RULES:\n"
        "- Strong correct answer on an axis: +0.20 to +0.40\n"
        "- Partially correct or hesitant answer: +0.05 to +0.15\n"
        "- Confused, wrong, or evasive answer: -0.10 to -0.30\n"
        "- Axis not touched at all this turn: 0.00 ONLY — but communication and behavioural are ALWAYS touched by every reply.\n\n"
        "Constraints: Responses must be short and conversational (2-3 sentences max). Never use markdown or plain text—always output a valid JSON object matching the turn schema layout."
    )

    current_turn = 1
    max_turns = 10
    current_phase = "MODEL"
    conversation_history = []
    # Fix 4: Stateful transition memory — records the "why" behind every phase change for debugging
    phase_transition_log = []
    
    # Pre-allocate tracking memory to maintain live signal flows seamlessly
    current_signals = {
        "confidence_level": "MEDIUM",
        "motivation_profile": "INTRINSIC",
        "cognitive_friction": "NONE",
        "engagement_velocity": "STAGNANT",
        "conceptual_certainty": "SPECULATIVE",
        "frustration_index": "LOW",
        "knowledge_retrieval_depth": "SURFACE",
        "linguistic_alignment": "MEDIUM"
    }
    current_scores = {
        "communication": 0.0,
        "tech_depth": 0.0,
        "behavioural": 0.0,
        "system_design": 0.0,
        "delivery": 0.0
    }
    # Cumulative running totals (sum of all deltas so far, clamped to [0.0, 5.0])
    cumulative_scores = {
        "communication": 0.0,
        "tech_depth": 0.0,
        "behavioural": 0.0,
        "system_design": 0.0,
        "delivery": 0.0
    }

    # 🚀 INSTANT KICKSTART SEED GREETING (Keeps startup delay at 0ms)
    try:
        instant_greeting = {
            "tutor_response": "Hello there! I'm Vidya, your coding tutor. Today, we'll explore Python functions and how they help organize our code. To start, can you tell me in your own words what a function is in programming?",
            "updated_ca_phase": current_phase,
            "on_topic_flag": True,
            "suggested_next_action": "Assess initial baseline understanding of function concepts.",
            "learner_signals": current_signals,
            "performance_delta": current_scores,
            "cumulative_scores": cumulative_scores,
            "current_turn_count": current_turn,
            "is_session_complete": False,
            "target_icp_type": "high_wage"
        }
        
        conversation_history.append({"role": "tutor", "content": instant_greeting["tutor_response"]})
        await websocket.send_text(json.dumps(instant_greeting))
        print("⚡ Instant Seed Greeting dispatched successfully.")
        
    except Exception as ex:
        print(f"❌ Handshake greeting acceleration failure: {ex}")

    try:
        while True:
            # Captures packed incoming string data via WebSockets channel
            raw_incoming_message = await websocket.receive_text()
            
            # Cleanly split user transcript words from their chosen ICP profile selection drop-down matrix
            parsed_socket_packet = json.loads(raw_incoming_message)
            user_input = parsed_socket_packet.get("text", "")
            active_icp_selection = parsed_socket_packet.get("icp_context", "high_wage")
            
            print(f"📥 Processing turn input: {user_input} | Active Demographic ICP: {active_icp_selection}")
            
            conversation_history.append({"role": "user", "content": user_input})
            current_turn += 1
            
            if current_turn > max_turns:
                print("🏁 Session turn ceiling hit. Moving to cumulative compilation...")
                final_prompt = (
                    f"You are the senior educational evaluator producing the final performance report for a 10-turn Python tutoring session.\n"
                    f"Target audience profile: {active_icp_selection}.\n\n"
                    f"--- ALREADY COMPUTED CUMULATIVE SKILL SCORES (use these exact values for final_skill_marks) ---\n"
                    f"{json.dumps(cumulative_scores)}\n\n"
                    f"--- LAST KNOWN LEARNER SIGNALS (use as basis for final_learner_signals) ---\n"
                    f"{json.dumps(current_signals)}\n\n"
                    f"--- FULL SESSION TRANSCRIPT ---\n"
                    f"{json.dumps(conversation_history)}\n"
                    f"------------------------------\n\n"
                    f"Write a 2-3 sentence overall_summary reflecting the student's full session journey.\n"
                    f"For final_skill_marks use the ALREADY COMPUTED values above — do not recalculate them.\n"
                    f"For final_learner_signals assess the student's overall profile across all 10 turns.\n\n"
                    f"Return strictly a JSON object in EXACTLY this structure:\n"
                    f"{{\n"
                    f'  "overall_summary": "<2-3 sentence summary of the student performance across the full session>",\n'
                    f'  "final_learner_signals": {{\n'
                    f'    "confidence_level": "<LOW or MEDIUM or HIGH>",\n'
                    f'    "motivation_profile": "<INTRINSIC or EXTRINSIC or DEFENSIVE>",\n'
                    f'    "cognitive_friction": "<NONE or MILD or HIGH>",\n'
                    f'    "engagement_velocity": "<ACCELERATING or STAGNANT or DROPPING>",\n'
                    f'    "conceptual_certainty": "<SPECULATIVE or ASSERTIVE or CONFUSED>",\n'
                    f'    "frustration_index": "<LOW or MEDIUM or HIGH>",\n'
                    f'    "knowledge_retrieval_depth": "<SURFACE or STRUCTURAL or SYNTACTIC>",\n'
                    f'    "linguistic_alignment": "<HIGH or MEDIUM or LOW>"\n'
                    f'  }},\n'
                    f'  "final_skill_marks": {{\n'
                    f'    "communication": {cumulative_scores["communication"]},\n'
                    f'    "tech_depth": {cumulative_scores["tech_depth"]},\n'
                    f'    "behavioural": {cumulative_scores["behavioural"]},\n'
                    f'    "system_design": {cumulative_scores["system_design"]},\n'
                    f'    "delivery": {cumulative_scores["delivery"]}\n'
                    f'  }}\n'
                    f"}}"
                )
                
                response = await asyncio.to_thread(
                    GLOBAL_GENAI_CLIENT.models.generate_content,
                    model=TARGET_MODEL,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.4)
                )
                
                final_report_data = json.loads(response.text.strip())
                await websocket.send_text(json.dumps({
                    "is_session_complete": True,
                    "final_outcome": final_report_data
                }))
                break
                
            else:
                # CONVERSATION TURN EVALUATION STATE PROCESSING
                turn_prompt = (
                    f"{SYSTEM_PREAMBLE}\n\n"
                    f"--- ACTIVE TARGET USER PROFILE CONTEXT ---\n"
                    f"The user profile belongs to the demographic category: {active_icp_selection.upper()}.\n"
                    f"Tailor language structures, conversational terminology depth, phrasing complexity, and hints specifically for this audience type.\n\n"
                    f"Session State context matrix: TURN {current_turn}/{max_turns}.\n"
                    f"Active Phase before evaluating this turn was: {current_phase}.\n"
                    f"Current Tracker Signal Metric States: {json.dumps(current_signals)}\n"
                    f"Current Cumulative Skill Scores (running totals so far, each axis clamped to -5.0 to +5.0): {json.dumps(cumulative_scores)}\n"
                    f"Prior Conversation History (context only — do NOT extract signals from this): {json.dumps(conversation_history[:-1])}\n\n"
                    f"════════════════════════════════════════════════════════════\n"
                    f"STUDENT'S LATEST REPLY (THIS TURN ONLY — extract ALL learner_signals from THIS text exclusively):\n"
                    f">>> {user_input} <<<\n"
                    f"════════════════════════════════════════════════════════════\n\n"
                    f"Action: Step through the transition logic rules carefully. "
                    f"Examine ONLY the student reply above (between the ═══ markers), compute dynamic new turn metrics from that text alone, output the updated_ca_phase string parameter reflecting the state shift, and ask your follow-up tutoring question.\n"
                    f"Output Constraint: Return strictly a valid JSON object in EXACTLY this structure.\n"
                    f"CRITICAL: updated_ca_phase MUST reflect the actual phase shift based on the student's answer — do NOT keep it as MODEL if the student showed confidence. Choose from: MODEL, COACH, SCAFFOLD, FADE.\n"
                    f"CRITICAL: learner_signals MUST be extracted EXCLUSIVELY from the student reply between the ═══ markers above — NOT from the tutor messages, NOT from the history, ONLY from the student's own words this turn.\n"
                    f"CRITICAL: performance_delta values MUST be non-zero for communication and behavioural on every turn.\n"
                    f"CRITICAL: If the student reply shows clear knowledge (defines a concept, gives an example, explains logic), set confidence_level=HIGH, cognitive_friction=NONE, conceptual_certainty=ASSERTIVE. Do NOT default to LOW/HIGH/CONFUSED without evidence in their words.\n"
                    f"{{\n"
                    f'  "tutor_response": "<your actual 2-3 sentence tutoring reply>",\n'
                    f'  "updated_ca_phase": "<MODEL or COACH or SCAFFOLD or FADE — based on student answer>",\n'
                    f'  "on_topic_flag": true,\n'
                    f'  "suggested_next_action": "<what you will do next turn>",\n'
                    f'  "learner_signals": {{\n'
                    f'    "confidence_level": "<LOW or MEDIUM or HIGH based on student answer>",\n'
                    f'    "motivation_profile": "<INTRINSIC or EXTRINSIC or DEFENSIVE>",\n'
                    f'    "cognitive_friction": "<NONE or MILD or HIGH>",\n'
                    f'    "engagement_velocity": "<ACCELERATING or STAGNANT or DROPPING>",\n'
                    f'    "conceptual_certainty": "<SPECULATIVE or ASSERTIVE or CONFUSED>",\n'
                    f'    "frustration_index": "<LOW or MEDIUM or HIGH>",\n'
                    f'    "knowledge_retrieval_depth": "<SURFACE or STRUCTURAL or SYNTACTIC>",\n'
                    f'    "linguistic_alignment": "<HIGH or MEDIUM or LOW>"\n'
                    f'  }},\n'
                    f'  "performance_delta": {{\n'
                    f'    "communication": <float between -1.0 and +1.0>,\n'
                    f'    "tech_depth": <float between -1.0 and +1.0>,\n'
                    f'    "behavioural": <float between -1.0 and +1.0>,\n'
                    f'    "system_design": <float between -1.0 and +1.0>,\n'
                    f'    "delivery": <float between -1.0 and +1.0>\n'
                    f'  }}\n'
                    f"}}"
                )
                
                response = await asyncio.to_thread(
                    GLOBAL_GENAI_CLIENT.models.generate_content,
                    model=TARGET_MODEL,
                    contents=turn_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.1)
                )
                
                parsed_data = json.loads(response.text.strip())
                print(f"🤖 AI RAW RESPONSE: {json.dumps(parsed_data)}")
                
                # Update loop registers sequentially so runtime values are passed dynamically into subsequent queries
                ai_proposed_phase = parsed_data.get("updated_ca_phase", current_phase)

                # SIGNAL FIX: Validate and normalize learner_signals from AI before using or sending
                # Guards against: missing keys, wrong types, AI returning a string instead of dict
                VALID_SIGNAL_KEYS = {
                    "confidence_level":         ["LOW", "MEDIUM", "HIGH"],
                    "motivation_profile":        ["INTRINSIC", "EXTRINSIC", "DEFENSIVE"],
                    "cognitive_friction":        ["NONE", "MILD", "HIGH"],
                    "engagement_velocity":       ["ACCELERATING", "STAGNANT", "DROPPING"],
                    "conceptual_certainty":      ["SPECULATIVE", "ASSERTIVE", "CONFUSED"],
                    "frustration_index":         ["LOW", "MEDIUM", "HIGH"],
                    "knowledge_retrieval_depth": ["SURFACE", "STRUCTURAL", "SYNTACTIC"],
                    "linguistic_alignment":      ["HIGH", "MEDIUM", "LOW"]
                }
                raw_signals = parsed_data.get("learner_signals", {})
                # If AI returned a non-dict (string, None, etc.), discard it entirely
                if not isinstance(raw_signals, dict):
                    raw_signals = {}
                    print(f"⚠️  learner_signals from AI was not a dict — using prior signals")
                # Build a clean, fully-populated signals dict:
                # Use AI value if it is a valid enum option, otherwise fall back to prior known-good value
                normalized_signals = {}
                for key, valid_options in VALID_SIGNAL_KEYS.items():
                    ai_val = str(raw_signals.get(key, "")).strip().upper()
                    if ai_val in valid_options:
                        normalized_signals[key] = ai_val
                    else:
                        # AI gave invalid/missing value — preserve the last known-good signal
                        normalized_signals[key] = current_signals.get(key, valid_options[0])
                        if ai_val:
                            print(f"⚠️  Invalid signal value for {key}: '{ai_val}' — kept prior: {normalized_signals[key]}")
                # Update current_signals with the clean normalized version
                current_signals = normalized_signals
                # Overwrite parsed_data learner_signals with the guaranteed-clean version
                parsed_data["learner_signals"] = normalized_signals
                print(f"🧠 SIGNALS: {json.dumps(normalized_signals)}")

                # Fix 1+2: Server-side deterministic phase enforcement — overrides AI variance using same rule tree
                PHASE_ORDER = ["MODEL", "COACH", "SCAFFOLD", "FADE"]
                def _enforce_phase(current, signals):
                    cf = signals.get("cognitive_friction", "NONE")
                    fi = signals.get("frustration_index", "LOW")
                    cc = signals.get("conceptual_certainty", "SPECULATIVE")
                    ev = signals.get("engagement_velocity", "STAGNANT")
                    cl = signals.get("confidence_level", "MEDIUM")
                    idx = PHASE_ORDER.index(current) if current in PHASE_ORDER else 0
                    # Step 1: Regression
                    if cf == "HIGH" or fi == "HIGH":
                        return PHASE_ORDER[max(0, idx - 1)], "REGRESSION"
                    # Step 2: Hold
                    if cc == "CONFUSED":
                        return current, "HOLD_CONFUSED"
                    if ev == "DROPPING" and fi != "LOW":
                        return current, "HOLD_DROPPING"
                    # Step 3: Progression
                    if cl == "HIGH" and cf == "NONE" and cc == "ASSERTIVE" and fi == "LOW":
                        return PHASE_ORDER[min(3, idx + 1)], "PROGRESSION"
                    # Step 4: Default
                    return current, "DEFAULT_HOLD"

                enforced_phase, transition_reason = _enforce_phase(current_phase, current_signals)

                # Fix 4: Log the transition with full signal context for debuggability
                phase_transition_log.append({
                    "turn": current_turn,
                    "phase_before": current_phase,
                    "ai_proposed": ai_proposed_phase,
                    "enforced_phase": enforced_phase,
                    "reason": transition_reason,
                    "signals_snapshot": dict(current_signals)
                })
                print(f"🔀 Phase: {current_phase} → {enforced_phase} (reason={transition_reason}, AI proposed={ai_proposed_phase})")

                # Overwrite AI output with enforced phase to ensure consistency
                current_phase = enforced_phase
                parsed_data["updated_ca_phase"] = enforced_phase
                
                # Safely extract performance_delta as flat floats regardless of how AI returns it
                raw_delta = parsed_data.get("performance_delta", {})
                if isinstance(raw_delta, dict):
                    def safe_float(val):
                        if isinstance(val, (int, float)):
                            return float(val)
                        if isinstance(val, dict):
                            # Sometimes AI wraps value e.g. {"value": 0.3}
                            return float(val.get("value", val.get("score", 0.0)))
                        try:
                            return float(val)
                        except:
                            return 0.0
                    current_scores = {axis: safe_float(raw_delta.get(axis, 0.0)) for axis in cumulative_scores}
                
                # Accumulate this turn's delta into the running cumulative totals (clamped to [0.0, 5.0])
                for axis in cumulative_scores:
                    delta_val = current_scores.get(axis, 0.0)
                    cumulative_scores[axis] = max(0.0, min(5.0, round(cumulative_scores[axis] + delta_val, 2)))
                
                print(f"📊 CUMULATIVE SCORES: {json.dumps(cumulative_scores)}")
                
                parsed_data["current_turn_count"] = current_turn
                parsed_data["is_session_complete"] = False
                parsed_data["target_icp_type"] = active_icp_selection
                # Send cumulative scores to frontend so UI always shows running totals
                parsed_data["cumulative_scores"] = cumulative_scores
                # Fix 4: Expose transition log so frontend/debug tools can trace every phase decision
                parsed_data["phase_transition_log"] = phase_transition_log
                
                conversation_history.append({"role": "tutor", "content": parsed_data["tutor_response"]})
                await websocket.send_text(json.dumps(parsed_data))
                
    except WebSocketDisconnect:
        keepalive_task.cancel()
        print("🛑 Session disconnected cleanly.")
    except Exception as e:
        print(f"❌ Core pipeline processing exception occurred: {e}")