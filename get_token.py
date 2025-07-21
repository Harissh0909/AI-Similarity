<<<<<<< HEAD
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("✅ Token saved as token.json")

if __name__ == '__main__':
    main()
=======
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    print("✅ Token saved as token.json")

if __name__ == '__main__':
    main()
>>>>>>> c2afe95 (Save local changes before rebase)
