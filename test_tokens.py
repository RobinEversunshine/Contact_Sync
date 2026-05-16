import os
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts']

def test_google_service(env_var_name):
    print(f"=========================================")
    print(f"🔍 Testing environment variable: {env_var_name} ...")
    print(f"=========================================")
    
    token_json_str = os.environ.get(env_var_name)
    
    if not token_json_str:
        print(f"❌ Error: No data found for {env_var_name} in the environment. Please check your GitHub Secrets configuration!")
        return False

    try:
        token_data = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        service = build('people', 'v1', credentials=creds)
        
        # Make a highly lightweight request: fetch the contact groups list with a max results limit of 1
        # As long as this request doesn't throw a 401/403 exception, it means the token is fully valid
        response = service.contactGroups().list(pageSize=1).execute()
        
        print(f"✅ [SUCCESS] {env_var_name} is valid! Google API connection test passed.")
        
        # Verify if a refresh_token is included for automatic token renewal
        if 'refresh_token' in token_data:
            print("💡 Check: contains refresh_token. This credential can auto-refresh in the cloud.")
        else:
            print("⚠️ Warning: refresh_token not found. This Token might expire after 1 hour; regenerating it is highly recommended!")
        return True
        
    except json.JSONDecodeError:
        print(f"❌ Error: The content of {env_var_name} is not a valid JSON format.")
        return False
    except Exception as e:
        print(f"❌ Error: {env_var_name} verification failed. Google error message:\n   {e}")
        return False

def main():
    success_a = test_google_service('GMAIL_TOKEN_A')
    success_b = test_google_service('GMAIL_TOKEN_B')
    
    # If either Token test fails, force the workflow to exit with an error state, triggering GitHub's red cross alert
    if not (success_a and success_b):
        print("\n🚨 Result: Partial or full Token verification failed. Please troubleshoot the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 Result: Congratulations! Tokens for both accounts are successfully verified and in a healthy, active state.")

if __name__ == '__main__':
    main()