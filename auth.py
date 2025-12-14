import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes needed for uploading
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_token():
    # Make sure client_secrets.json is in the same folder
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    # This will open your browser to log in
    creds = flow.run_local_server(port=0)
    
    # Save the credentials for Colab
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    print("✅ token.json created! Upload this file to your Colab Drive.")

if __name__ == "__main__":
    generate_token()