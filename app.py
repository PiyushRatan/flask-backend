from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Hello from Render backend!"

if __name__ == '__main__':
    app.run()
