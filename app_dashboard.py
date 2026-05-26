import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import json
import os

# --- 1. PAGE ARCHITECTURE SETUP ---
st.set_page_config(page_title="Vidya v3 Live Multimodal POC", layout="wide", page_icon="🎙️")
st.title("🎙️ Vidya v3: Universal Voice & Text Live POC")
st.subheader("Cloud-Deployed Multi-Modal Browser Interface")
st.markdown("---")

# --- 2. SECURE API HANDSHAKE ---
api_key = None
if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]:
    api_key = os.environ["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_key = st.secrets["GEMINI_API_KEY"]

if api_key:
    genai.configure(api_key=api_key)

# --- 3. PERSISTENT STATE MANAGEMENT CHANNELS ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL"}
    ]

if "telemetry" not in st.session_state:
    st.session_state.telemetry = {
        "confidence": "NEUTRAL 💾",
        "friction": "LOW 🟢",
        "motivation": "INTRINSIC 🎯",
        "velocity": "STEADY 📈",
        "certainty": "STABLE ✅",
        "frustration": "0/10 ⚠️",
        "depth": "SURFACE 🔍",
        "alignment": "HIGH 🤝",
        "phase": "MODEL", # Automatically managed initial phase
        "register": "ENGLISH",
        "skills": {"communication": 50, "tech_depth": 0, "system_design": 40, "behavioural": 10, "delivery": 50}
    }

if "active_audio_playback" not in st.session_state:
    st.session_state.active_audio_playback = None
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None
if "last_processed_audio_key" not in st.session_state:
    st.session_state.last_processed_audio_key = None

# --- 4. RUNTIME DIAGNOSTICS CONTROL PANEL ---
st.sidebar.header("🕹️ Global Run Options")
selected_tier = st.sidebar.selectbox("Student Tier Profile", ["Low-Wage Tier", "High-Wage Tier"])

if st.sidebar.button("🧹 Reset Shared Session"):
    st.session_state.chat_history = [{"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL"}]
    st.session_state.telemetry = {
        "confidence": "NEUTRAL 💾", "friction": "LOW 🟢", "motivation": "INTRINSIC 🎯", "velocity": "STEADY 📈",
        "certainty": "STABLE ✅", "frustration": "0/10 ⚠️", "depth": "SURFACE 🔍", "alignment": "HIGH 🤝",
        "phase": "MODEL", "register": "ENGLISH",
        "skills": {"communication": 50, "tech_depth": 0, "system_design": 40, "behavioural": 10, "delivery": 50}
    }
    st.session_state.last_processed_audio_key = None
    st.session_state.pending_user_input = None
    st.session_state.active_audio_playback = None
    st.rerun()

# --- 5. ACTIVE MULTI-TURN CONVERSATION STREAM ---
st.subheader("💬 Active Multi-Turn Script")
for msg in st.session_state.chat_history:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        tag = f" `[{msg.get('phase', 'COACH')}]`" if msg["role"] == "assistant" else ""
        st.markdown(f"**{'Vidya Tutor AI' if msg['role']=='assistant' else 'Student'}{tag}:** {msg['text']}")

st.markdown("---")

# --- 6. UNIFIED AUDIO/TEXT INPUT CAPTURE LAYER ---
st.subheader("📥 Submit Response")
col_text, col_voice = st.columns([4, 1])

with col_text:
    text_input = st.chat_input("Type your answer here...", key="text_chat_input")
    if text_input:
        st.session_state.pending_user_input = {"type": "text", "data": text_input}
        st.rerun()

with col_voice:
    audio_record = mic_recorder(
        start_prompt="🎙️ Click to Record",
        stop_prompt="🛑 Stop Recording",
        key="browser_mic",
        use_container_width=True
    )
    
    if audio_record and audio_record["bytes"]:
        audio_id = hash(audio_record["bytes"])
        if audio_id != st.session_state.last_processed_audio_key:
            st.session_state.pending_user_input = {"type": "audio", "data": audio_record["bytes"]}
            st.session_state.last_processed_audio_key = audio_id
            st.rerun()

# --- 7. RECURRENT INFERENCE & COGNITIVE PIPELINE ---
if st.session_state.pending_user_input and api_key:
    active_payload = st.session_state.pending_user_input
    st.session_state.pending_user_input = None
    
    try:
        with st.spinner("Processing cognitive vectors & structuring multimodal data..."):
            base_model = genai.GenerativeModel("gemini-2.5-flash")
            
            # --- PHASE A: AUDIO SPEECH-TO-TEXT RESOLUTION ---
            if active_payload["type"] == "audio":
                audio_part = {"mime_type": "audio/wav", "data": active_payload["data"]}
                transcription_prompt = "Transcribe this student audio response accurately. Output only the plain text transcription, nothing else."
                trans_res = base_model.generate_content([audio_part, transcription_prompt])
                processed_text = trans_res.text.strip()
            else:
                processed_text = active_payload["data"]

            if processed_text:
                st.session_state.chat_history.append({"role": "user", "text": processed_text})

                # --- PHASE B: PSYCHOLINGUISTIC EVALUATION AND METRICS INFERENCE ---
                # ✅ BACK TO AUTOMATION: Prompt explicitly commands the AI to control the phase transitions dynamically
                system_instruction = f"""
                You are Vidya v3, an expert AI tutor evaluating a student on Python execution scopes.
                Current Student Tier: {selected_tier}.
                
                Analyze the conversation history alongside the student's latest response. You MUST dynamically choose the next pedagogical phase based on the student's state.
                Generate a single, valid JSON block matching this schema:
                {{
                    "tutor_response": "Your immediate response text following your dynamically selected pedagogical phase framework.",
                    "confidence_profile": "LOW, HIGH, or NEUTRAL",
                    "cognitive_friction": "HIGH or LOW",
                    "motivation_mode": "INTRINSIC, EXTRINSIC, or DEFENSIVE",
                    "engagement_velocity": "STAGNANT, STEADY, or ACCELERATING",
                    "conceptual_certainty": "CONFUSED or STABLE",
                    "frustration_index": "Scale from 1 to 10",
                    "knowledge_schema_depth": "SURFACE or DEEP",
                    "linguistic_alignment": "LOW or HIGH",
                    "pedagogical_phase": "MODEL, COACH, SCAFFOLD, or FADE",
                    "target_register": "ENGLISH or HINGLISH",
                    "skills": {{
                        "communication": "integer 0-100",
                        "tech_depth": "integer 0-100",
                        "system_design": "integer 0-100",
                        "behavioural": "integer 0-100",
                        "delivery": "integer 0-100"
                    }}
                }}
                
                CRITICAL COGNITIVE APPRENTICESHIP PHASE TRANSITION LOGIC:
                - If cognitive_friction is HIGH and knowledge_schema_depth is SURFACE -> Set pedagogical_phase to 'SCAFFOLD' and adopt a supportive Hinglish register.
                - If conceptual_certainty is CONFUSED and confidence_profile is LOW -> Set pedagogical_phase to 'MODEL' and demonstrate a clear code layout example.
                - If conceptual_certainty is STABLE and cognitive_friction is LOW -> Set pedagogical_phase to 'COACH' and push with interactive questions.
                - If confidence_profile is HIGH and knowledge_schema_depth is DEEP -> Set pedagogical_phase to 'FADE' and fade your guidance back.
                
                Keep your tutor_response extremely concise, punchy, and dialogic.
                """
                
                clean_serializable_history = [{"role": m["role"], "text": m["text"], "phase": m.get("phase", "COACH")} for m in st.session_state.chat_history]
                combined_analytics_prompt = f"{system_instruction}\n\nFull Thread History:\n{json.dumps(clean_serializable_history)}\n\nLatest Student Phrase: {processed_text}"
                
                agent_res = base_model.generate_content(
                    combined_analytics_prompt, 
                    generation_config={"response_mime_type": "application/json", "temperature": 0.0}
                )
                result = json.loads(agent_res.text)
                tutor_reply = result.get("tutor_response", "")
                current_phase = result.get("pedagogical_phase", "COACH")

                # --- PHASE C: HIGH-AVAILABILITY CLOUD TEXT-TO-SPEECH ---
                tts = gTTS(text=tutor_reply, lang='en', tld='co.in' if result.get("target_register") == "HINGLISH" else 'com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                st.session_state.active_audio_playback = fp.getvalue()

                # --- PHASE D: ENGINE STATE RETRIEVAL AND UPDATE ---
                st.session_state.telemetry = {
                    "confidence": f"{result.get('confidence_profile', 'NEUTRAL')} 📊",
                    "friction": f"{result.get('cognitive_friction', 'LOW')} 🧠",
                    "motivation": f"{result.get('motivation_mode', 'INTRINSIC')} 🎯",
                    "velocity": f"{result.get('engagement_velocity', 'STEADY')} 📈",
                    "certainty": f"{result.get('conceptual_certainty', 'STABLE')} ✅",
                    "frustration": f"{result.get('frustration_index', '0')}/10 ⚠️",
                    "depth": f"{result.get('knowledge_schema_depth', 'SURFACE')} 🔍",
                    "alignment": f"{result.get('linguistic_alignment', 'HIGH')} 🤝",
                    "phase": current_phase,
                    "register": result.get('target_register', 'ENGLISH'),
                    "skills": result.get('skills', {"communication": 50, "tech_depth": 0, "system_design": 40, "behavioural": 10, "delivery": 50})
                }
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "text": tutor_reply, 
                    "phase": current_phase
                })
                st.rerun()

    except Exception as e:
        st.error(f"Inference Failure: {e}")

# --- 8. GLOBAL NATIVE AUDIO SPEAKING MODULE ---
if st.session_state.active_audio_playback:
    with st.sidebar.container():
        st.audio(st.session_state.active_audio_playback, format="audio/mp3", autoplay=True)
    st.session_state.active_audio_playback = None

# --- 9. REAL-TIME TELEMETRY GRAPHICS VISUALIZATION ---
st.markdown("---")
st.subheader("🧠 Observed Psycholinguistic Signal Profile")
p1, p2, p3, p4 = st.columns(4)
with p1:
    st.metric("Confidence Profile", st.session_state.telemetry["confidence"])
    st.metric("Conceptual Certainty", st.session_state.telemetry["certainty"])
with p2:
    st.metric("Cognitive Friction", st.session_state.telemetry["friction"])
    st.metric("Frustration Index", st.session_state.telemetry["frustration"])
with p3:
    st.metric("Motivation Mode", st.session_state.telemetry["motivation"])
    st.metric("Knowledge Schema Depth", st.session_state.telemetry["depth"])
with p4:
    st.metric("Engagement Velocity", st.session_state.telemetry["velocity"])
    st.metric("Linguistic Alignment", st.session_state.telemetry["alignment"])

st.markdown("---")
st.subheader("📊 Cumulative Layer C Overall Skill Marks")
s1, s2, s3, s4, s5 = st.columns(5)
skills = st.session_state.telemetry["skills"]
with s1:
    st.metric("Communication", f"{skills.get('communication', 50)}/100")
with s2:
    st.metric("Technical Depth", f"{skills.get('tech_depth', 0)}/100")
with s3:
    st.metric("System Design", f"{skills.get('system_design', 40)}/100")
with s4:
    st.metric("Behavioural", f"{skills.get('behavioural', 10)}/100")
with s5:
    st.metric("Delivery Velocity", f"{skills.get('delivery', 50)}/100")

# Live Real-Time Phase Display Monitor Status Panel
st.sidebar.markdown("---")
st.sidebar.metric("🤖 Current Adaptive Phase", st.session_state.telemetry["phase"])
st.sidebar.metric("Linguistic Register Mode", st.session_state.telemetry["register"])