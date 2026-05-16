import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from sync_contacts import main as push_to_gmails
from get_contact_info import main as get_contact


def get_service_from_env(env_var_name):
    """Retrieve Google People service using credentials from file or environment"""
    # Get token from GitHub Secrets/Environment Variables
    token_str = os.environ.get(env_var_name)
    if not token_str:
        raise ValueError(f"❌ Cannot find env variable: {env_var_name}")
        
    token_data = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(token_data, ['https://www.googleapis.com/auth/contacts'])
    return build('people', 'v1', credentials=creds)


def main():
    # 1. Fetch the parsed contact list
    contact_list = get_contact()

    if not contact_list:
        print("💡 No contacts need to sync, process end.")
        return

    # 2. Initialize API Services for both Gmail accounts (Done once outside the loop to save resources)
    try:
        service_a = get_service_from_env('GMAIL_TOKEN_A')
        service_b = get_service_from_env('GMAIL_TOKEN_B')
    except Exception as e:
        print(f"❌ Failed to initialize Google service tokens: {e}")
        return

    # 3. Iterate through the list and push each contact to Gmail one by one
    success_count = 0
    for person_payload in contact_list:
        name = f"{person_payload.get('fname', '')} {person_payload.get('lname', '')}".strip() or "Unnamed"
        print(f"🔄 Syncing: {name}...")
        
        try:
            # Call your pre-configured synchronization logic
            push_to_gmails(person_payload, service_a, service_b)
            print(f"✅ {name} synced successfully!")
            success_count += 1
        except Exception as e:
            # Catch errors for an individual contact to allow the loop to continue
            print(f"❌ Failed to sync {name}. Error: {e}")

    print(f"\n📊 Sync Report: Successfully synced {success_count}/{len(contact_list)}")


if __name__ == "__main__":
    main()