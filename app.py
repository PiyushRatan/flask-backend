from flask import Flask, request, jsonify
from flask_cors import CORS
# from dotenv import load_dotenv # Commented out as per request
import google.generativeai as genai
import os

# load_dotenv() # Commented out as per request

app = Flask(__name__)
CORS(app)

# Replace "YOUR_ACTUAL_GEMINI_API_KEY_HERE" with your real API key
# You can find your key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
GEMINI_API_KEY = "AIzaSyCgwBmkDlSoJm5DgsxgnwtyRAMNxGir2D0"
# ----------------------------------------------------------------------------

genai.configure(api_key=GEMINI_API_KEY) # Using the hardcoded key
# Using 'gemini-2.0-flash' as it was suggested by your test script and is often more available
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is running!"}), 200

# Default root endpoint returns a simple HTML welcome message
@app.route("/", methods=["GET"])
def index():
    return "<h2>Welcome to the Cyber Alert Flask Backend!<br>Use <code>/ask</code> to POST scam/phishing messages for analysis.<br>Status: <span style='color:green;'>Running</span></h2>", 200

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        language = data.get("language", "").strip()


        # Print received data for debugging
        print(f"[DEBUG] /ask received: question='{question}', language='{language}'")

        if not question:
            return jsonify({
                "answer": "Input is empty.",
                "severity": "Unknown",
                "action": "Please enter a message to analyze."
            })

        # Preprompt for the scam/phishing detector
        prompt = f"""
You are a scam and phishing detection assistant trained to identify deceptive,
unethical, fraudulent, or harmful messages. (Take severity sincerely: if life threatening then label as Critical, otherwise use the appropriate severity.)

Analyze the following message (in {language} language):
"{question}"

Respond strictly in this structured format, and reply in {language}:

Response: <clear, concise explanation of whether it's a scam or not, and why>
Severity: <Low / Moderate / High / Critical>
Recommended Action: <specific advice for the user (e.g., ignore, report, block, take legal help)>
"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Parse Gemini output
        lines = text.split('\n')
        result = {
            "answer": "Not Available",
            "severity": "Unknown",
            "action": "No recommendation."
        }

        for line in lines:
            if line.lower().startswith("response:"):
                result["answer"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("severity:"):
                result["severity"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("recommended action:"):
                result["action"] = line.split(":", 1)[1].strip()

        return jsonify(result)

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "answer": "Something went wrong while processing your request.",
            "severity": "Unknown",
            "action": "Try again later or contact support.",
            "language": language.capitalize()
        })

@app.route("/language", methods=["GET"])
def language_info():
    language = request.args.get("language", "").strip()
    return f"Your Language is {language}", 200

if __name__ == "__main__":
    # Use the PORT environment variable for Render deployment, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)