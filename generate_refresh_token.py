import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    client_secrets_file = "client_secret.json"
    
    if not os.path.exists(client_secrets_file):
        print(f"Error: {client_secrets_file} not found.")
        print("Please place your client_secret.json in this directory.")
        return

    # Create the flow using the client secrets file
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES
    )

    # Run the local server to authorize
    creds = flow.run_local_server(port=0)

    print("\nSuccessfully authenticated!")
    print(f"Refresh Token: {creds.refresh_token}")
    print("\n=== INSTRUCTIONS FOR GITHUB SECRETS ===")
    print("Add the following secrets to your GitHub repository:")
    print(f"1. YOUTUBE_REFRESH_TOKEN: {creds.refresh_token}")
    print(f"2. YOUTUBE_CLIENT_ID: {creds.client_id}")
    print(f"3. YOUTUBE_CLIENT_SECRET: {creds.client_secret}")
    print("=======================================")

if __name__ == "__main__":
    main()
