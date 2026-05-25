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
        {"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL", "audio_bytes": None}
    ]
if "telemetry" not in st.session_state:
    st.session_state.telemetry = {
        "friction": "LOW 🟢", "confidence": "NEUTRAL 💾", "motivation": "INTRINSIC 🎯", "frustration": "0/10", "register": "ENGLISH (Formal)", "phase": "MODEL"
    }
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None
if "last_processed_audio_key" not in st.session_state:
    st.session_state.last_processed_audio_key = None

# --- 4. RUNTIME DIAGNOSTICS CONTROL PANEL ---
st.sidebar.header("🕹️ Global Run Options")
selected_tier = st.sidebar.selectbox("Student Tier Profile", ["Low-Wage Tier", "High-Wage Tier"])

if st.sidebar.button("🧹 Reset Shared Session"):
    st.session_state.chat_history = [{"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL", "audio_bytes": None}]
    st.session_state.telemetry = {"friction": "LOW 🟢", "confidence": "NEUTRAL 💾", "motivation": "INTRINSIC 🎯", "frustration": "0/10", "register": "ENGLISH (Formal)", "phase": "MODEL"}
    st.session_state.last_processed_audio_key = None
    st.session_state.pending_user_input = None
    st.rerun()

# --- 5. ACTIVE MULTI-TURN CONVERSATION STREAM ---
st.subheader("💬 Active Multi-Turn Script")
for msg in st.session_state.chat_history:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        # Dynamically draw the current cognitive phase label assigned to that specific response
        tag = f" `[{msg.get('phase', 'COACH')}]`" if msg["role"] == "assistant" else ""
        st.markdown(f"**{'Vidya Tutor AI' if msg['role']=='assistant' else 'Student'}{tag}:** {msg['text']}")
        
        # If the response has valid browser audio bytes attached, display the player control block
        if msg["role"] == "assistant" and msg.get("audio_bytes"):
            st.audio(msg["audio_bytes"], format="audio/mp3")

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
                system_instruction = f"""
                You are Vidya v3, an expert AI tutor evaluating a student on Python execution scopes and functional states.
                Current Context: Student is classified under the {selected_tier}.
                
                Analyze the conversation history alongside the student's latest response. You MUST generate a strict, single, valid JSON block following this schema:
                {{
                    "tutor_response": "Your immediate response text following the Cognitive Apprenticeship Model framework",
                    "cognitive_friction": "HIGH or LOW",
                    "confidence_level": "HIGH or LOW or NEUTRAL",
                    "motivation_profile": "INTRINSIC or EXTRINSIC or DEFENSIVE",
                    "frustration_index": "Scale from 1 to 10",
                    "pedagogical_phase": "MODEL or COACH or SCAFFOLD or FADE",
                    "target_register": "ENGLISH or HINGLISH"
                }}
                
                CRITICAL PHASE TRANSITION RULES:
                1. If the student repeats 'Next' or shows complete confusion, set pedagogical_phase to 'SCAFFOLD' and speak in Hinglish.
                2. If the student answers confidently and correctly, transition the phase to 'COACH' or 'FADE'.
                3. Keep your tutor_response extremely concise and dialogic.
                """
                
                combined_analytics_prompt = f"{system_instruction}\n\nFull Thread History:\n{json.dumps(st.session_state.chat_history)}\n\nLatest Student Phrase: {processed_text}"
                
                agent_res = base_model.generate_content(
                    combined_analytics_prompt, 
                    generation_config={
                        "response_mime_type": "application/json", 
                        "temperature": 0.0
                    }
                )
                result = json.loads(agent_res.text)
                tutor_reply = result.get("tutor_response", "")
                current_phase = result.get("pedagogical_phase", "COACH")

                # --- PHASE C: HIGH-AVAILABILITY CLOUD TEXT-TO-SPEECH ---
                # Converts the AI reply text into standard web-playable mp3 format data streams
                tts = gTTS(text=tutor_reply, lang='en', tld='co.in' if result.get("target_register") == "HINGLISH" else 'com')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                audio_bytes = fp.getvalue()

                # --- PHASE D: ENGINE STATE RETRIEVAL AND UPDATE ---
                st.session_state.telemetry = {
                    "friction": f"{result.get('cognitive_friction', 'LOW')} 🧠",
                    "confidence": f"{result.get('confidence_level', 'NEUTRAL')} 📊",
                    "motivation": f"{result.get('motivation_profile', 'INTRINSIC')} 🎯",
                    "frustration": f"{result.get('frustration_index', '0')}/10 ⚠️",
                    "register": result.get('target_register', 'ENGLISH'),
                    "phase": current_phase
                }
                
                # Append response containing text, specific adaptive phase, and audio track
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "text": tutor_reply, 
                    "phase": current_phase,
                    "audio_bytes": audio_bytes
                })
                st.rerun()

    except Exception as e:
        st.error(f"Inference Failure: {e}")

# --- 8. REAL-TIME TELEMETRY GRAPHICS VISUALIZATION ---
st.markdown("---")
st.subheader("📊 Dynamic Analytics Layer")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Cognitive Working Load", st.session_state.telemetry["friction"])
    st.metric("Linguistic Register", st.session_state.telemetry["register"])
with c2:
    st.metric("Motivation Core Mode", st.session_state.telemetry["motivation"])
    st.metric("Frustration Marker", st.session_state.telemetry["frustration"])
with c3:
    st.metric("Active Execution Phase", st.session_state.telemetry["phase"])
    st.metric("Confidence Profile", st.session_state.telemetry["confidence"])