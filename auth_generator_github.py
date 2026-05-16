from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json
import sys

SCOPES = ['https://www.googleapis.com/auth/contacts']

def main():
    # 1. Retrieve Google Credentials JSON string
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS')
    if not creds_json_str:
        raise ValueError("❌ Error: Environment variable GOOGLE_CREDENTIALS is empty")

    # 2. Parse the string into a Python dictionary
    client_config = json.loads(creds_json_str)

    # 3. Initialize the Flow
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # 4. Read the authorization code environment variable passed from GitHub Actions
    auth_code = os.environ.get('INPUT_AUTH_CODE')

    # If an authorization code exists, execute [Step 2]: Exchange the code for a Token with Google
    if auth_code:
        auth_code = auth_code.strip()
        print(f"🔄 Exchanging code for Token with Google, auth code length: {len(auth_code)}...")
        
        try:
            # Explicitly omit or disable verifier because PKCE was disabled in Step 1
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            print("\n" + "="*60)
            print("🎉 Token generated successfully! Copy the entire content below into GitHub Secrets:")
            print("="*60 + "\n")
            print(creds.to_json())
            print("\n" + "="*60)
        except Exception as e:
            print(f"❌ Failed to exchange Token: {e}")
            
    # If no authorization code exists, execute [Step 1]: Generate and print the authorization URL
    else:
        # 💡 [CRITICAL MODIFICATION]: Explicitly set code_challenge=None to disable PKCE verification
        # This prevents Google from demanding a code_verifier across different execution environments (e.g., subsequent GitHub Action runs)
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline',
            code_challenge=None 
        )
        
        print("\n" + "="*60)
        print("👉 Step 1: Open the following link in your browser to authorize:")
        print("-" * 60)
        print(auth_url)
        print("-" * 60)
        print("\n👉 Step 2: After authorization, Google will provide an Authorization Code.")
        print("Please trigger the GitHub Actions workflow again and paste the code into the input field.")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == '__main__':
    main()