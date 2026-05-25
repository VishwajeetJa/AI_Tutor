import streamlit as st
import google.generativeai as genai
import json
import os

# 1. Page Configuration Setup
st.set_page_config(page_title="Vidya v3 Live POC", layout="wide", page_icon="🤖")

st.title("🤖 Vidya v3: Live Intelligent Tutor POC")
st.subheader("Autonomous Cognitive State Machine & Multi-Turn Conversation Thread")
st.markdown("---")

# 2. Secure API Key Initialization (Looks for Streamlit Secrets or local Environment)
if "GEMINI_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
elif "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.configure = None

# 3. Initialize Persistent Memory State Channels
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL"}
    ]
if "telemetry" not in st.session_state:
    st.session_state.telemetry = {
        "friction": "LOW 🟢", "confidence": "NEUTRAL 💾", "motivation": "INTRINSIC 🎯", "frustration": "0/10", "register": "ENGLISH (Formal)", "phase": "MODEL"
    }

# --- SIDEBAR CONTROL CONTROL ENGINE ---
st.sidebar.header("🕹️ POC Runtime Diagnostics")
selected_tier = st.sidebar.selectbox("Simulated Student ICP Tier", ["Low-Wage Tier (Hinglish/Hindi Scaffolding)", "High-Wage Tier (Advanced Engineering)"])

if st.sidebar.button("🧹 Clear & Reset State Machine"):
    st.session_state.chat_history = [{"role": "assistant", "text": "Hi, I am Vidya! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?", "phase": "MODEL"}]
    st.session_state.telemetry = {"friction": "LOW 🟢", "confidence": "NEUTRAL 💾", "motivation": "INTRINSIC 🎯", "frustration": "0/10", "register": "ENGLISH (Formal)", "phase": "MODEL"}
    st.rerun()

# --- MAIN CONVERSATION DISPLAYER ---
st.subheader("💬 Active Multi-Turn Conversation History")
for msg in st.session_state.chat_history:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        tag = f" `[{msg.get('phase', '')}]`" if msg["role"] == "assistant" else ""
        st.markdown(f"**{ 'Vidya Tutor AI' if msg['role']=='assistant' else 'Student Input' }{tag}:** {msg['text']}")

st.markdown("---")

# --- LIVE INTELLIGENT INFERENCE PIPELINE ---
if not genai.get_default_api_key():
    st.error("❌ API key missing. Please add your GEMINI_API_KEY in the Streamlit cloud advanced setting secrets console.")
else:
    if user_input := st.chat_input("Type your student answer here..."):
        # Log student's text instantly
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        
        # Build the background instruction profile based on your prompt frameworks
        system_instruction = f"""
        You are Vidya v3, an AI tutor evaluating a student on Python scopes.
        Current Context: Student is classified under {selected_tier}.
        
        Your task is to analyze the student text and output a strict, valid JSON block matching this layout:
        {{
            "tutor_response": "Your immediate response text following the Cognitive Apprenticeship Model framework",
            "cognitive_friction": "HIGH or LOW",
            "confidence_level": "HIGH or LOW or NEUTRAL",
            "motivation_profile": "INTRINSIC or EXTRINSIC or DEFENSIVE",
            "frustration_index": "Scale from 1 to 10",
            "pedagogical_phase": "MODEL or COACH or SCAFFOLD or FADE",
            "target_register": "ENGLISH or HINGLISH"
        }}
        
        CRITICAL RULES:
        1. If tier is Low-Wage and cognitive friction is HIGH or user shows deep confusion, switch register to Hinglish immediately.
        2. Keep your tutor response concise.
        """
        
        try:
            with st.spinner("Analyzing psycholinguistic vectors & generating streaming inference..."):
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_instruction,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.0}
                )
                
                # Format full thread history context to pass to Gemini
                formatted_prompt = f"Full Thread History:\n{json.dumps(st.session_state.chat_history)}\n\nLatest Input: {user_input}"
                response = model.generate_content(formatted_prompt)
                
                # Parse deterministic data schemas
                result = json.loads(response.text)
                
                # Update visual telemetry metrics
                st.session_state.telemetry = {
                    "friction": f"{result.get('cognitive_friction', 'LOW')} 🧠",
                    "confidence": f"{result.get('confidence_level', 'NEUTRAL')} 📊",
                    "motivation": f"{result.get('motivation_profile', 'INTRINSIC')} 🎯",
                    "frustration": f"{result.get('frustration_index', '0')}/10 ⚠️",
                    "register": result.get('target_register', 'ENGLISH'),
                    "phase": result.get('pedagogical_phase', 'COACH')
                }
                
                # Append the response to the persistent thread
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "text": result.get("tutor_response", ""), 
                    "phase": result.get("pedagogical_phase", "COACH")
                })
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Inference Thread Halted: {e}")

# --- REAL-TIME VISUALIZATION TELEMETRY LAYER ---
st.subheader("📊 Dynamic Layer Analysis")
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