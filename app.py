import os
from flask import Flask, render_template
from lakebase import run_query

app = Flask(__name__)

@app.route("/")
def home():

    tickets = run_query("""
        SELECT 
            ticket_id,
            title,
            status,
            created_by,
            created_at
        FROM tickets
        ORDER BY ticket_id
    """)

    return render_template(
        "index.html",
        tickets=tickets
    )


if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    print(f"Flask app starting on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)