import os, json


def main():
    # GitHub Actions stores the event payload data in this environment variable when triggered
    event_path = os.getenv('GITHUB_EVENT_PATH')
    
    if not event_path or not os.path.exists(event_path):
        print("⚠️ GITHUB_EVENT_PATH not found. Returning an empty list.")
        return []
        
    with open(event_path, 'r') as f:
        event_data = json.load(f)
    
    # 1. Extract the client_payload sent by the shortcut
    payload = event_data.get('client_payload', {})
    
    # 2. Extract the 'contacts' list packaged inside the payload from the shortcut
    # If the payload isn't in a batch format, wrap the single format into a list [payload] for backward compatibility
    contact_list = payload.get('contacts')
    print(contact_list)
    
    if not isinstance(contact_list, list):
        if payload:  # Support backward compatibility for legacy single-contact formats
            contact_list = [payload]
        else:
            contact_list = []

    fields = ['fname', 'lname', 'phone', 'email', 'address', 'note', 'bday', 'url', 'social']

    print(f"📦 --- Received batch sync request for {len(contact_list)} contacts ---")
    
    # 3. Loop through and print-check each contact's data
    for index, person in enumerate(contact_list, 1):
        print(f"\n👤 Contact #{index}:")
        for field in fields:
            value = person.get(field, 'N/A')
            print(f"  {field.capitalize()}: {value}")
            
    print("\n--------------------------------------")
    
    return contact_list  # 👈 Core Modification: Now returns a list of dicts [{}, {}, ...]


if __name__ == "__main__":
    main()