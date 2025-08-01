from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


# Get Gemini API key from environment variable (set in Render or .env file)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.Oopsie heheehehee 😅😄😅")

genai.configure(api_key=GEMINI_API_KEY) # Using the hardcoded key
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is running!"}), 200

@app.route("/", methods=["GET"])
def index():
    return "<h2>Welcome to the Cyber Alert Flask Backend!<br>Use <code>/ask</code> to POST scam/phishing messages for analysis.<br>Status: <span style='color:green;'>Running</span></h2>", 200

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        language = data.get("language", "").strip()


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

Respond strictly in this structured format, and reply in {language} severity should be in english(must):

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