from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone, timedelta
import re
import base64
import email
import os
import json

# Gmail API read-only scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
EXPECTED_PATTERN = r"Received Payment of\s+MYR\s+1\.50\b"

def is_payment_received(start_time):
    """
    Check Gmail for payment email received after given UTC datetime AND matching amount.
    """
    try:
        # Ensure start_time is timezone-aware
        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        # Grace period
        adjusted_start = start_time - timedelta(seconds=3)

        # 🔐 Load token JSON from environment
        token_json_str = os.getenv("TOKEN_JSON")
        if not token_json_str:
            raise Exception("❌ TOKEN_JSON environment variable not found!")
        token_data = json.loads(token_json_str)
        with open("token.json", "w") as f:
            json.dump(token_data, f)

        # 🔐 Load credentials JSON from environment
        credentials_json_str = os.getenv("CREDENTIALS_JSON")
        if not credentials_json_str:
            raise Exception("❌ CREDENTIALS_JSON environment variable not found!")
        credentials_data = json.loads(credentials_json_str)
        with open("credentials.json", "w") as f:
            json.dump(credentials_data, f)

        # 🔑 Build Gmail service
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        # 📨 Query emails from sender after a specific time
        unix_time = int(adjusted_start.timestamp())
        query = f'from:alert@bimb.com after:{unix_time}'
        print("🕵️ Gmail Query:", query)

        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])

        if not messages:
            print("❌ No payment emails found.")
            return False

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

            # 🕒 Timestamp check
            email_time = datetime.fromtimestamp(int(msg_data.get('internalDate')) / 1000, tz=timezone.utc)
            if email_time < (start_time - timedelta(seconds=30)):
                print(f"⚠️ Email too early: {email_time}")
                continue

            # 🔍 Content check
            snippet = msg_data.get('snippet', '')
            subject = next((h['value'] for h in msg_data['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')

            print("📨 Subject:", subject)
            print("🕒 Email Time:", email_time.isoformat())
            print("🔍 Snippet:", snippet)

            if re.search(EXPECTED_PATTERN, snippet):
                print("✅ Match: Payment confirmed")
                return True
            else:
                print("❌ Match failed: Amount not found")

        print("❌ No matching payment emails")
        return False

    except HttpError as error:
        print(f"❌ Gmail API Error: {error}")
        return False
    except Exception as e:
        print(str(e))
        return False
