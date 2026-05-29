import asyncio
import websockets
import json

# The "Gold Standard" test suite
TEST_SUITE = [
    {"text": "What is a function in Python?", "expected_phase": "MODEL"},
    {"text": "A function is like a box that holds code I can reuse.", "expected_phase": "COACH"},
    {"text": "Can you show me how to define one?", "expected_phase": "COACH"},
    {"text": "I'm a bit stuck on the syntax, help?", "expected_phase": "MODEL"},
    {"text": "Oh, right, def function_name():, thanks!", "expected_phase": "COACH"},
    {"text": "I think I get it now, it's about scope too.", "expected_phase": "SCAFFOLD"},
    {"text": "Here is my code: def add(a,b): return a+b", "expected_phase": "SCAFFOLD"},
    {"text": "It works! That was easier than I thought.", "expected_phase": "FADE"},
    {"text": "Functions make code clean and modular.", "expected_phase": "FADE"},
    {"text": "I feel confident about functions now.", "expected_phase": "FADE"}
]

async def run_benchmark():
    uri = "wss://ai-tutor-kinx.onrender.com/ws" # Update with your live link
    async with websockets.connect(uri) as ws:
        print(f"🚀 Starting Benchmark on {uri}")
        
        for i, test in enumerate(TEST_SUITE):
            # Send turn to backend
            await ws.send(json.dumps({"text": test["text"], "icp_context": "high_wage"}))
            response = await ws.recv()
            data = json.loads(response)
            
            # Benchmark Logic
            actual_phase = data.get("updated_ca_phase")
            success = actual_phase == test["expected_phase"]
            
            print(f"Turn {i+1} | Input: {test['text'][:30]}... | Phase: {actual_phase} | {'✅' if success else '❌'}")
            await asyncio.sleep(1) # Small delay for real-time feel

asyncio.run(run_benchmark())