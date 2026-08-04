import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1> Lakebase support app is running! </h1>"


if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    print(f"Flask app starting on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)