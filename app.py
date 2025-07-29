from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "answer": "Input is empty.",
                "severity": "Unknown",
                "action": "Please enter a message to analyze."
            })

        # Preprompt
        prompt = f"""
You are a scam and phishing detector assistant.

Analyze the following message:
"{question}"

Return your answer in this format (must follow the structure):
Response: <clear and brief response>
Severity: <Low / Medium / High>
Recommended Action: <what should the user do?>
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
            "action": "Try again later or contact support."
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)