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

## Features
- **Dynamic Phase Shifting:** AI adapts its tutoring style based on learner performance.
- **Psycholinguistic Profiling:** Real-time analysis of user confidence, motivation, and cognitive friction.
- **Skill Tracking:** Turn-by-turn performance evaluation across five key axes (Communication, Tech Depth, System Design, Behavioral, Delivery).
- **Dual ICP Support:** Supports tailored tutoring for High Wage (Software Engineering) and Low Wage (CX/Data Entry) demographics.

## Quick Start
1. **Clone the repository.**
2. **Install dependencies:**
   `pip install -r requirements.txt`
3. **Configure Environment:** Create a `.env` file and add your Google Gemini API Key:
   `GEMINI_API_KEY=your_api_key_here`
4. **Launch:**
   `uvicorn app.main:app --reload`
5. **Access:** Open `http://localhost:8000` in your browser.

## Deployment
This project is configured for seamless deployment on [Render](https://render.com/). Ensure your `requirements.txt` is updated and push to GitHub to trigger an automatic build.