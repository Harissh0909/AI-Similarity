<<<<<<< HEAD
from email.mime.text import MIMEText
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Only sending email, so this scope is sufficient
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_code_to_user(name, phone, recipient_email, unique_code):
    try:
        # Load authorized credentials from token.json
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        # Email content
        subject = "Your Unique Code"
        body = f"""Hi {name},

Thank you for your submission.

Your unique code is: {unique_code}

If you have any questions, feel free to contact us.

Regards,
Support Team
"""

        # Construct MIME email
        message = MIMEText(body)
        message['to'] = recipient_email
        message['from'] = "me"
        message['subject'] = subject

        # Encode and send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw}
        sent = service.users().messages().send(userId="me", body=create_message).execute()

        print(f"✅ Email sent to {recipient_email}. Message ID: {sent['id']}")
        return True

    except Exception as e:
        print(f"❌ Error sending email to {recipient_email}: {e}")
        return False

# 🧪 Example usage (can be removed if importing from main.py)
if __name__ == "__main__":
    send_code_to_user("MrA", "0177485335", "ehekekek@gmail.com", "TWW67")
=======
from email.mime.text import MIMEText
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Only sending email, so this scope is sufficient
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_code_to_user(name, phone, recipient_email, unique_code):
    try:
        # Load authorized credentials from token.json
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        # Email content
        subject = "Your Unique Code"
        body = f"""Hi {name},

Thank you for your submission.

Your unique code is: {unique_code}

If you have any questions, feel free to contact us.

Regards,
Support Team
"""

        # Construct MIME email
        message = MIMEText(body)
        message['to'] = recipient_email
        message['from'] = "me"
        message['subject'] = subject

        # Encode and send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw}
        sent = service.users().messages().send(userId="me", body=create_message).execute()

        print(f"✅ Email sent to {recipient_email}. Message ID: {sent['id']}")
        return True

    except Exception as e:
        print(f"❌ Error sending email to {recipient_email}: {e}")
        return False

# 🧪 Example usage (can be removed if importing from main.py)
if __name__ == "__main__":
    send_code_to_user("MrA", "0177485335", "ehekekek@gmail.com", "TWW67")
>>>>>>> c2afe95 (Save local changes before rebase)
