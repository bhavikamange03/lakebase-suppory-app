import os
from lakebase import run_query, run_write
from flask import Flask, render_template, request, redirect, flash, abort

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

@app.route("/")
def home():
    filter_status = request.args.get('status', 'all')

    if filter_status == 'all':
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
    else:
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
            WHERE status = %s
            ORDER BY ticket_id
        """, (filter_status,))

    # Fetch statistics
    stats = {}
    
    # Total tickets
    total_result = run_query("SELECT COUNT(*) as total FROM tickets")
    stats['total'] = total_result[0]['total'] if total_result else 0
    
    # Tickets by status
    status_stats = run_query("""
        SELECT status, COUNT(*) as count
        FROM tickets
        GROUP BY status
    """)
    stats['by_status'] = {row['status']: row['count'] for row in status_stats} if status_stats else {}
    
    # Tickets by priority
    priority_stats = run_query("""
        SELECT priority, COUNT(*) as count
        FROM tickets
        GROUP BY priority
    """)
    stats['by_priority'] = {row['priority']: row['count'] for row in priority_stats} if priority_stats else {}
    
    # Tickets by category
    category_stats = run_query("""
        SELECT category, COUNT(*) as count
        FROM tickets
        GROUP BY category
    """)
    stats['by_category'] = {row['category']: row['count'] for row in category_stats} if category_stats else {}
    
    # Recent activity (tickets created in last 7 days)
    recent_result = run_query("""
        SELECT COUNT(*) as recent
        FROM tickets
        WHERE created_at >= NOW() - INTERVAL '7 days'
    """)
    stats['recent_7_days'] = recent_result[0]['recent'] if recent_result else 0

    return render_template(
        "index.html",
        tickets=tickets,
        filter_status=filter_status,
        stats=stats
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

    # Validate ticket exists
    if not ticket:
        abort(404, description=f"Ticket #{ticket_id} not found")

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
    # Validate required fields
    title = request.form.get("title", "").strip()
    created_by = request.form.get("created_by", "").strip()
    status = request.form.get("status", "").strip()
    category = request.form.get("category", "").strip()
    priority = request.form.get("priority", "").strip()

    # Validation checks
    errors = []
    if not title:
        errors.append("Title is required")
    elif len(title) < 3:
        errors.append("Title must be at least 3 characters")
    elif len(title) > 200:
        errors.append("Title must be less than 200 characters")
    
    if not created_by:
        errors.append("Creator name is required")
    elif len(created_by) > 100:
        errors.append("Creator name must be less than 100 characters")
    
    if not status:
        errors.append("Status is required")
    elif status not in ['open', 'in_progress', 'resolved', 'closed']:
        errors.append("Invalid status value")
    
    if not category:
        errors.append("Category is required")
    elif category not in ['bug', 'feature', 'support', 'question']:
        errors.append("Invalid category value")
    
    if not priority:
        errors.append("Priority is required")
    elif priority not in ['low', 'medium', 'high', 'critical']:
        errors.append("Invalid priority value")
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect("/")

    try:
        run_write("""
            INSERT INTO tickets
            (
                title,
                status,
                priority,
                category,
                created_by,
                created_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
        """,
        (
            title,
            status,
            priority,
            category,
            created_by
        ))
        flash("Ticket created successfully!", 'success')
    except Exception as e:
        flash(f"Error creating ticket: {str(e)}", 'error')

    return redirect("/")

@app.route(
    "/ticket/<int:ticket_id>/message",
    methods=["POST"]
)
def add_message(ticket_id):
    # Validate required fields
    message_text = request.form.get("message_text", "").strip()
    author = request.form.get("author", "").strip()

    # Validation checks
    if not message_text:
        flash("Message text is required", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if len(message_text) < 1:
        flash("Message cannot be empty", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if len(message_text) > 5000:
        flash("Message must be less than 5000 characters", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if not author:
        flash("Author name is required", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if len(author) > 100:
        flash("Author name must be less than 100 characters", 'error')
        return redirect(f"/ticket/{ticket_id}")

    try:
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
        flash("Message added successfully!", 'success')
    except Exception as e:
        flash(f"Error adding message: {str(e)}", 'error')

    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/status",
    methods=["POST"]
)
def update_status(ticket_id):
    status = request.form.get("status", "").strip()

    # Validate status
    if not status:
        flash("Status is required", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if status not in ['open', 'in_progress', 'resolved', 'closed']:
        flash("Invalid status value", 'error')
        return redirect(f"/ticket/{ticket_id}")

    try:
        run_write("""
            UPDATE tickets
            SET status = %s
            WHERE ticket_id = %s
        """,
        (
            status,
            ticket_id
        ))
        flash(f"Status updated to '{status}' successfully!", 'success')
    except Exception as e:
        flash(f"Error updating status: {str(e)}", 'error')

    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/priority",
    methods=["POST"]
)
def update_priority(ticket_id):
    priority = request.form.get("priority", "").strip()

    # Validate priority
    if not priority:
        flash("Priority is required", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if priority not in ['low', 'medium', 'high', 'critical']:
        flash("Invalid priority value", 'error')
        return redirect(f"/ticket/{ticket_id}")

    try:
        run_write("""
            UPDATE tickets
            SET priority = %s
            WHERE ticket_id = %s
        """,
        (
            priority,
            ticket_id
        ))
        flash(f"Priority updated to '{priority}' successfully!", 'success')
    except Exception as e:
        flash(f"Error updating priority: {str(e)}", 'error')

    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/category",
    methods=["POST"]
)
def update_category(ticket_id):
    category = request.form.get("category", "").strip()

    # Validate category
    if not category:
        flash("Category is required", 'error')
        return redirect(f"/ticket/{ticket_id}")
    
    if category not in ['bug', 'feature', 'support', 'question']:
        flash("Invalid category value", 'error')
        return redirect(f"/ticket/{ticket_id}")

    try:
        run_write("""
            UPDATE tickets
            SET category = %s
            WHERE ticket_id = %s
        """,
        (
            category,
            ticket_id
        ))
        flash(f"Category updated to '{category}' successfully!", 'success')
    except Exception as e:
        flash(f"Error updating category: {str(e)}", 'error')

    return redirect(
        f"/ticket/{ticket_id}"
    )

@app.route(
    "/ticket/<int:ticket_id>/delete",
    methods=["POST"]
)
def delete_ticket(ticket_id):
    # Validate ticket exists before deleting
    ticket = run_query("""
        SELECT ticket_id
        FROM tickets
        WHERE ticket_id = %s
    """, (ticket_id,))

    if not ticket:
        flash(f"Ticket #{ticket_id} not found", 'error')
        return redirect("/")

    try:
        # Delete associated messages first (foreign key constraint)
        run_write("""
            DELETE FROM ticket_messages
            WHERE ticket_id = %s
        """, (ticket_id,))

        # Delete the ticket
        run_write("""
            DELETE FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))

        flash(f"Ticket #{ticket_id} deleted successfully!", 'success')
    except Exception as e:
        flash(f"Error deleting ticket: {str(e)}", 'error')

    return redirect("/")

@app.route(
    "/ticket/<int:ticket_id>/message/<int:message_id>/delete",
    methods=["POST"]
)
def delete_message(ticket_id, message_id):
    # Validate message exists
    message = run_query("""
        SELECT message_id
        FROM ticket_messages
        WHERE message_id = %s AND ticket_id = %s
    """, (message_id, ticket_id))

    if not message:
        flash(f"Message #{message_id} not found", 'error')
        return redirect(f"/ticket/{ticket_id}")

    try:
        run_write("""
            DELETE FROM ticket_messages
            WHERE message_id = %s
        """, (message_id,))

        flash("Message deleted successfully!", 'success')
    except Exception as e:
        flash(f"Error deleting message: {str(e)}", 'error')

    return redirect(f"/ticket/{ticket_id}")

@app.errorhandler(404)
def not_found_error(error):
    flash(str(error.description) if error.description else "Page not found", 'error')
    return redirect("/")

@app.errorhandler(500)
def internal_error(error):
    flash("An internal error occurred. Please try again.", 'error')
    return redirect("/")
    
if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))
    print(f"Flask app starting on http://{host}:{port}")
    app.run(debug=True, host=host, port=port)