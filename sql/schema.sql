CREATE TABLE tickets (

    ticket_id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,

    status TEXT NOT NULL,

    created_by TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE ticket_messages (

    message_id SERIAL PRIMARY KEY,

    ticket_id INTEGER,

    message_text TEXT,

    author TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)

);