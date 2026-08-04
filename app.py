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

@app.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id):

    ticket = run_query("""
        SELECT
            ticket_id,
            title,
            status,
            created_by,
            created_at
        FROM tickets
        WHERE ticket_id = %s
    """, (ticket_id,))


    messages = run_query("""
        SELECT
            message_id,
            message_text,
            author,
            created_at
        FROM ticket_messages
        WHERE ticket_id = %s
        ORDER BY created_at
    """, (ticket_id,))


    return render_template(
        "ticket.html",
        ticket=ticket[0],
        messages=messages
    )
    
if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    print(f"Flask app starting on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)