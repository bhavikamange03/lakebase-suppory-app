import os
from lakebase import run_query, run_write
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/")
def home():

    tickets = run_query("""
        SELECT 
            ticket_id,
            title,
            status,
            priority,
            category,
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
            priority,
            category,
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

@app.route("/create-ticket", methods=["POST"])
def create_ticket():

    title = request.form["title"]
    created_by = request.form["created_by"]
    status = request.form["status"]


    run_write("""
        INSERT INTO tickets
        (
            title,
            status,
            created_by,
            created_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            NOW()
        )
    """,
    (
        title,
        status,
        created_by
    ))


    return redirect("/")

@app.route(
    "/ticket/<int:ticket_id>/message",
    methods=["POST"]
)
def add_message(ticket_id):

    message_text = request.form["message_text"]

    author = request.form["author"]


    run_write("""
        INSERT INTO ticket_messages
        (
            ticket_id,
            message_text,
            author,
            created_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            NOW()
        )
    """,
    (
        ticket_id,
        message_text,
        author
    ))


    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/status",
    methods=["POST"]
)
def update_status(ticket_id):

    status = request.form["status"]


    run_write("""
        UPDATE tickets
        SET status = %s
        WHERE ticket_id = %s
    """,
    (
        status,
        ticket_id
    ))


    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/priority",
    methods=["POST"]
)
def update_priority(ticket_id):

    priority = request.form["priority"]


    run_write("""
        UPDATE tickets
        SET priority = %s
        WHERE ticket_id = %s
    """,
    (
        priority,
        ticket_id
    ))


    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/category",
    methods=["POST"]
)
def update_category(ticket_id):

    category = request.form["category"]


    run_write("""
        UPDATE tickets
        SET category = %s
        WHERE ticket_id = %s
    """,
    (
        category,
        ticket_id
    ))


    return redirect(
        f"/ticket/{ticket_id}"
    )
    
if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    print(f"Flask app starting on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)