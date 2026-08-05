INSERT INTO tickets
(title,status,priority,category,created_by)

VALUES

('Not able to login','open','high','bug','Bhavika'),

('Keyboard is not working','in_progress','medium','bug','Nidhi'),

('Not able to connect wi-fi','resolved','low','bug','Chitra'),

('Add dark mode feature','open','medium','feature','Alice'),

('How to reset password?','closed','low','question','Bob');


INSERT INTO ticket_messages
(ticket_id,message_text,author)

VALUES

(1,'Login page shows error','Bhavika'),

(1,'Looking into it','Support'),

(2,'keyboard keys are not working','Nidhi'),

(2,'Please reconnect','Support'),

(3,'resolved','Support'),

(3,'Thanks!','Chitra');