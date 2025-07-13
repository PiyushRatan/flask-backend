from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allows frontend (like GitHub Pages) to access this backend

# Route: Home
@app.route('/')
def home():
    return "🔥 Hello from Render backend!"

# Route: About
@app.route('/about')
def about():
    return "This is a Flask backend hosted on Render."

# Route: JSON response
@app.route('/json')
def json_data():
    data = {
        "name": "Piyush",
        "status": "Backend Connected",
        "platform": "Render"
    }
    return jsonify(data)

# Route: Handle POST request (like a chatbot or form)
@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.json.get('question', '').strip()
        if not user_input:
            return jsonify({"error": "No question provided"}), 400

        # Simulate AI response (you can replace this later with Gemini/OpenAI)
        response = f"You asked: '{user_input}' — and I heard you loud and clear 🔥"
        return jsonify({"answer": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for Render hosting
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)