import requests
import os
import speech_recognition as sr
import pygame
import time
import asyncio
import edge_tts
import io
import sys
from threading import Thread

SERVER_URL = "http://127.0.0.1:8000/tutor/turn"

# Initialize pygame mixer safely for audio handling
pygame.mixer.init()

# PREMIUM EXPRESSIVE VOICE SELECTION
VOICE_CHARACTER = "en-US-AndrewNeural"

def monitor_interruption():
    """Background listener that kills audio playback if the user hits Enter."""
    input()  # Waits for user to press Enter
    if pygame.mixer.music.get_busy():
        print("\n🛑 [UX Flow] Interruption caught! Cutting audio stream short...")
        pygame.mixer.music.stop()

def speak_and_print_ux(text):
    """UX IMPROVEMENTS: 
    1. Streams audio from RAM (no slow disk files).
    2. Types text word-by-word at human speech pace.
    3. Allows user to press Enter to instantly skip/interrupt long explanations.
    4. SELF-HEALING: Implements a 3-pass exponential backoff retry loop to bypass weak internet drops.
    """
    async def fetch_audio_stream():
        max_retries = 3
        retry_delay = 0.5  # Seconds to wait before retrying
        
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text, VOICE_CHARACTER, rate="+20%")
                communicate.output_format = "audio-16khz-32kbitrate-mono-mp3"
                audio_bytes = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
                return audio_bytes  # Success! Break out of retry loop and return data
            except Exception as stream_err:
                if attempt < max_retries - 1:
                    # Connection dropped; sleep momentarily and clear socket for a clean retry
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    # Exceeded all 3 attempts, pass the error up to the fallback handler
                    raise stream_err

    try:
        # Stream Directly to Memory Buffer with our retry logic active
        audio_data = asyncio.run(fetch_audio_stream())
        audio_buffer = io.BytesIO(audio_data)
        
        pygame.mixer.music.load(audio_buffer)
        
        print("🤖 Tutor: ", end="", flush=True)
        pygame.mixer.music.play()
        
        # Spin up concurrent interruption thread
        interrupt_thread = Thread(target=monitor_interruption, daemon=True)
        interrupt_thread.start()
        
        # Typewriter Effect Pacing
        words = text.split(" ")
        delay_per_word = 45.0 / 180.0  
        
        for word in words:
            if not pygame.mixer.music.get_busy(): 
                break
            sys.stdout.write(word + " ")
            sys.stdout.flush()
            time.sleep(delay_per_word)
            
        while pygame.mixer.music.get_busy():
            time.sleep(0.01)
            
        print() 
        pygame.mixer.music.unload()
        audio_buffer.close()
        
    except Exception as e:
        # Absolute Worst-Case Fallback: If all 3 network retries fail completely
        print(f"\n🤖 Tutor (Text Only Fallback): {text}")
        print(f"⚠️ UX Stream Bypass Notice: Network dropped consistently after 3 retries. ({e})")

def run_voice_tutor_session():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True 
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==========================================================================================")
    print("🚀 VIDYA V3 LIVE VOICE TUTOR INTERFACE (ULTRA-LOW LATENCY UX BUILD)")
    print("==========================================================================================")
    print("✨ UX FEATURES ACTIVE: In-Memory Streaming | Typewriter Sync | Enter to Interrupt | Self-Healing Retries")
    print("==========================================================================================")
    
    print("\nSelect the Target User Persona (ICP Variant):")
    print("1. High-Wage Tier    (Focuses on advanced engineering & system design optimization)")
    print("2. Low-Wage Tier     (Focuses on warm, accessible scaffolding in Hinglish/Hindi)")
    
    icp_choice = ""
    icp_map = {"1": "high_wage", "2": "low_wage"}
    while icp_choice not in icp_map:
        icp_choice = input("\nEnter choice (1-2): ").strip()
    selected_icp = icp_map[icp_choice]

    print("\nSelect the Cognitive Apprenticeship Phase to initialize for this session:")
    print("1. MODEL    (Tutor explains and demonstrates logic out loud)")
    print("2. COACH    (Tutor asks guiding questions to probe logic)")
    print("3. SCAFFOLD (Tutor steps back, providing minor hints only)")
    print("4. FADE     (Tutor mostly confirms performance, letting user lead)")
    
    phase_choice = ""
    phase_map = {"1": "MODEL", "2": "COACH", "3": "SCAFFOLD", "4": "FADE"}
    while phase_choice not in phase_map:
        phase_choice = input("\nEnter choice (1-4): ").strip()
    selected_phase = phase_map[phase_choice]
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🚀 INITIALIZING SESSION ── Target Persona: {selected_icp.upper()} | Phase: {selected_phase}")
    print("Mode: Voice-In / Voice-Out Multi-Turn Scenario Test (Locked to 10 Turns)")
    print("💡 UX Pro-Tip: Press Enter key anytime while the tutor is talking to skip ahead.")
    print("=" * 90)
    
    # INSTANT COLD-START FIX: Pre-seed greeting question directly in conversation memory
    greeting_text = "Hi, I am Vidya, your AI tutor! Let's jump right into things. Tell me, what do you know about Python functions and execution scopes?"
    
    session_state = {
        "skill_topic": "Python Functions and Scopes",
        "mastery_level": 0.3,
        "icp_type": selected_icp, 
        "ca_phase": selected_phase, 
        "conversation_history": [
            {"role": "assistant", "content": greeting_text}
        ] 
    }
    
    cumulative_scores = {
        "communication": 50.0,
        "tech_depth": 55.0,
        "system_design": 40.0,
        "behavioural": 60.0,
        "delivery": 50.0
    }
    
    session_deltas = []
    final_signals = []
    
    # Render greeting and question aloud locally without waiting for any server lag
    speak_and_print_ux(greeting_text)
    print("-" * 90)
    
    for turn in range(1, 11):
        print(f"\n🔄 [TUTOR TURN {turn}/10] ── Active Phase: {session_state['ca_phase']}")
        
        # First listen to user's response for the active question turn
        user_voice_input = ""
        while not user_voice_input.strip():
            with sr.Microphone() as source:
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    print("🎙️ Listening now... Speak clearly! (Or type 'quit' / press Ctrl+C to type)")
                    audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
                    
                    print("⚡ Transcribing audio frequencies...")
                    user_voice_input = recognizer.recognize_google(audio).strip()
                    print(f"👤 You Said: \"{user_voice_input}\"")
                    
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    print("⚠️ Audio quiet or unclear. Let's restart this speech window...")
                    continue
                except KeyboardInterrupt:
                    print("\n⌨️ Keyboard Input Mode Activated.")
                    user_voice_input = input("📝 Type your response here (or type 'quit' to exit): ").strip()
                    break
        
        if user_voice_input.lower() == "quit":
            print("\n🛑 Session terminated early via manual exit.")
            break
            
        session_state["conversation_history"].append({"role": "user", "content": user_voice_input})
        
        # Query backend process now that memory contains the turn data
        print("📡 Querying Backend Evaluation Engine...")
        try:
            response = requests.post(SERVER_URL, json=session_state)
            if response.status_code != 200:
                print(f"  ❌ Backend Network Error: {response.text}")
                return
                
            data = response.json()
            tutor_text = data['tutor_response']
            
            session_state["conversation_history"].append({"role": "assistant", "content": tutor_text})
            
            if 'performance_delta' in data:
                session_deltas.append(data['performance_delta'])
            if 'learner_signals' in data:
                final_signals.append(data['learner_signals'])
            
            speak_and_print_ux(tutor_text)
            
            session_state["ca_phase"] = data['updated_ca_phase']
            print(f"🛡️  [METADATA Logs] On-Topic: {data['on_topic_flag']} | Target Next Step: {data['suggested_next_action']}")
            print("-" * 90)
            
            time.sleep(0.2)

        except Exception as e:
            print(f"❌ Connection Failure: {str(e)}")
            return
            
    print("\n" + "█"*30 + " COMPILING CUMULATIVE SCORECARD " + "█"*30)
    
    for delta in session_deltas:
        for axis in cumulative_scores:
            cumulative_scores[axis] += delta.get(axis, 0.0) * 100
            cumulative_scores[axis] = max(0.0, min(100.0, cumulative_scores[axis]))

    # TRACKING SIGNALS SUMMARY
    conf_modes = [s['confidence_level'] for s in final_signals if 'confidence_level' in s]
    fric_modes = [s['cognitive_friction'] for s in final_signals if 'cognitive_friction' in s]
    mot_modes = [s['motivation_profile'] for s in final_signals if 'motivation_profile' in s]
    eng_modes = [s['engagement_velocity'] for s in final_signals if 'engagement_velocity' in s]
    cert_modes = [s['conceptual_certainty'] for s in final_signals if 'conceptual_certainty' in s]
    frust_modes = [s['frustration_index'] for s in final_signals if 'frustration_index' in s]
    depth_modes = [s['knowledge_retrieval_depth'] for s in final_signals if 'knowledge_retrieval_depth' in s]
    align_modes = [s['linguistic_alignment'] for s in final_signals if 'linguistic_alignment' in s]
    
    primary_conf = max(set(conf_modes), key=conf_modes.count) if conf_modes else "MEDIUM"
    primary_fric = max(set(fric_modes), key=fric_modes.count) if fric_modes else "NONE"
    primary_mot = max(set(mot_modes), key=mot_modes.count) if mot_modes else "INTRINSIC"
    primary_eng = max(set(eng_modes), key=eng_modes.count) if eng_modes else "STAGNANT"
    primary_cert = max(set(cert_modes), key=cert_modes.count) if cert_modes else "ASSERTIVE"
    primary_frust = max(set(frust_modes), key=frust_modes.count) if frust_modes else "LOW"
    primary_depth = max(set(depth_modes), key=depth_modes.count) if depth_modes else "SURFACE"
    primary_align = max(set(align_modes), key=align_modes.count) if align_modes else "MEDIUM"

    print("\n" + "═"*35 + " SESSION FINAL PERFORMANCE REPORT " + "═"*35)
    print(f"🧠 OBSERVED PSYCHOLINGUISTIC SIGNAL PROFILE:")
    print(f"   [Confidence Profile]       : {primary_conf}")
    print(f"   [Cognitive Friction]       : {primary_fric}")
    print(f"   [Motivation Mode]          : {primary_mot}")
    print(f"   [Engagement Velocity]      : {primary_eng}")
    print(f"   [Conceptual Certainty]     : {primary_cert}")
    print(f"   [Frustration Index]        : {primary_frust}")
    print(f"   [Knowledge Schema Depth]   : {primary_depth}")
    print(f"   [Linguistic Alignment]     : {primary_align}")
    
    print("\n📊 CUMULATIVE LAYER C OVERALL SKILL MARKS:")
    print(f"communication: {int(cumulative_scores['communication'])}")
    print(f"tech_depth: {int(cumulative_scores['tech_depth'])}")
    print(f"system_design: {int(cumulative_scores['system_design'])}")
    print(f"behavioural: {int(cumulative_scores['behavioural'])}")
    print(f"delivery: {int(cumulative_scores['delivery'])}")
    print("═" * 104 + "\n")

if __name__ == "__main__":
    run_voice_tutor_session()