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

# Strict pattern to match: "Received Payment of MYR 1.50"
EXPECTED_PATTERN = r"Received Payment of\s+MYR\s+1\.50\b"

def is_payment_received(start_time):
    """
    Check Gmail for payment email received after given UTC datetime AND matching amount.
    """
    try:
        # Ensure start_time is timezone-aware
        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            start_time = start_time.replace(tzinfo=timezone.utc)

        # ✅ Add 3-second grace period buffer to start_time
        adjusted_start = start_time - timedelta(seconds=3)


        if not os.path.exists("token.json"):
            token_str = os.getenv("TOKEN_JSON")
    
            if token_str:
                try:
                    with open("token.json", "w") as f:
                        json.dump(json.loads(token_str), f)
                    print("✅ token.json successfully written from environment secret")
                except Exception as e:
                    print("❌ Failed to write token.json:", str(e))
            else:
                print("❌ TOKEN_JSON environment variable not found!")

        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        unix_time = int(adjusted_start.timestamp())
        query = f'from:alert@bimb.com after:{unix_time}'
        print("🕵️ Querying Gmail with:", query)

        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])

        if not messages:
            print("❌ No payment emails found")
            return False

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

            # 🕒 Step 1: Extract and compare timestamp
            internal_date = int(msg_data.get('internalDate')) / 1000  # convert ms to seconds
            email_time = datetime.fromtimestamp(internal_date, tz=timezone.utc)

            grace_period = timedelta(seconds=30)
            if email_time < (start_time - grace_period):
                print(f"⚠️ Email too early (even with grace): {email_time} < {start_time - grace_period}")
                continue

            # 📨 Step 2: Extract headers and snippet
            snippet = msg_data.get('snippet', '')
            subject = next((h['value'] for h in msg_data['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')

            print("📨 Subject:", subject)
            print("🕒 Email Time:", email_time.isoformat())
            print("🔍 Snippet:", snippet)

            # ✅ Step 3: Check amount strictly
            if re.search(EXPECTED_PATTERN, snippet):
                print("✅ Payment email matches BOTH time & amount")
                return True
            else:
                print("❌ Amount not matched")

        print("❌ No valid payment emails matched all conditions")
        return False

    except HttpError as error:
        print(f"❌ Gmail API Error: {error}")
        return False
