# 🤖 Vidya v3: Adaptive Voice Tutor AI (POC)

Vidya v3 is an ultra-low latency, voice-first Intelligent Tutoring System (ITS) built to personalize coding education using advanced cognitive architectures.

---

## 🚀 Step-by-Step Installation & Run Configurations

### 1. Set Up the Local Environment
Open your VS Code terminal and run the following commands:

cd vidya-tutor-poc
python -m venv venv

On Windows use this to activate:
venv\Scripts\activate

On macOS/Linux use this to activate:
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

### 2. Configure Your Environment Keys
Create a file named .env in the root directory and add your key:
GEMINI_API_KEY=your_actual_google_gemini_api_key_here

---

## 💻 Running the Application

To launch the full proof of concept live, open three separate terminal tabs inside VS Code and execute the following:

* Terminal 1 (Backend FastAPI Server):
uvicorn app.main:app --reload

* Terminal 2 (Streamlit UI Dashboard Frontend):
streamlit run app_dashboard.py

* Terminal 3 (Voice/Terminal Client Loop):
python run_tests.py