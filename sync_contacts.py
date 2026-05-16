import datetime
# import json
# import os
import pycountry
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build

# SCOPES = ['https://www.googleapis.com/auth/contacts']


raw_payload = {
    'address': 'TestStreet1\nTestStreet2\nPOSTCODE TestCity\nAustria',
    'bday': 'Aug 14, 2006 at 00:00',
    'email': 'test@gmail.com\ntest2@gmail.com',
    'fname': 'Robin',
    'lname': 'Cai',
    'note': 'Test notes',
    'phone': '1001001000\n(200) 200-2000',
    'social': '',
    'url': 'http://test/url\nhttp://test2/url'
}


def parse_multiline_field(field_value):
    """Split \n to lists, removing spaces and empty values"""
    if not field_value: return []
    return [item.strip() for item in field_value.split('\n') if item.strip()]


def get_country_code(country_name):
    """Get ISO 3166-1 alpha-2 code based on country name"""
    if not country_name:
        return ""
    try:
        # Fuzzy search for country
        # For example, "Austria" returns the country object with alpha_2 property "AT"
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except (LookupError, AttributeError):
        # If no match is found, print a warning and return empty string
        print(f"⚠️ Could not find country code for: {country_name}")
        return ""


def parse_address(address_str):
    """Refined address parsing supporting multiline street and country recognition"""
    lines = [item.strip() for item in address_str.split('\n') if item.strip()]
    if not lines:
        return {}
    
    addr_obj = {
        "streetAddress": "",
        "extendedAddress": "",
        "city": "",
        "postalCode": "",
        "country": "",
        "countryCode": ""
    }
    
    # 1. Identify country (Last line)
    if len(lines) >= 1:
        country_name = lines[-1]
        addr_obj["country"] = country_name
        addr_obj["countryCode"] = get_country_code(country_name)
    
    # 2. Identify Postcode and City (Second to last line)
    # Format usually follows "POSTCODE City"
    if len(lines) >= 2:
        city_line = lines[-2]
        parts = city_line.split(' ', 1)
        if len(parts) == 2:
            addr_obj["postalCode"] = parts[0]
            addr_obj["city"] = parts[1]
        else:
            addr_obj["city"] = city_line
            
    # 3. Logic for Street and Extended Address allocation
    street_parts = lines[:-2] if len(lines) >= 2 else lines[:-1] if len(lines) == 1 else []
    if len(street_parts) == 1:
        # Only one line: write to streetAddress
        addr_obj["streetAddress"] = street_parts[0]
    elif len(street_parts) >= 2:
        # First line to streetAddress
        addr_obj["streetAddress"] = street_parts[0]
        # Second and subsequent lines combined into extendedAddress
        addr_obj["extendedAddress"] = "\n".join(street_parts[1:])
        
    return addr_obj


def find_existing_contact_by_name(service, fname, lname):
    """Search for contact based on name"""
    # Combine name for search, e.g., "Test Fname Test Lname"
    full_name = f"{fname} {lname}".strip()
    
    resource_name = None
    etag = None
    
    if full_name:
        try:
            results = service.people().searchContacts(
                query=full_name,
                # Must include 'names' to get etag and further info in results
                readMask="names,phoneNumbers" 
            ).execute()
            
            # searchContacts returns results wrapped in a 'results' list
            search_results = results.get('results', [])
            
            if search_results:
                # Get the person with the highest match score (first result)
                person = search_results[0].get('person')
                resource_name = person.get('resourceName')
                etag = person.get('etag')
                print(f"🔍 Found existing contact: {full_name} ({resource_name})")
        except Exception as e:
            print(f"Error searching for name: {e}")
            
    return resource_name, etag


def upsert_contact(service, data):
    # --- 1. Parse basic multi-value fields ---
    phones = parse_multiline_field(data.get('phone', ''))
    emails = [{"value": e} for e in parse_multiline_field(data.get('email', ''))]
    urls = [{"value": u} for u in parse_multiline_field(data.get('url', ''))]
    
    # --- 2. Parse address ---
    parsed_addr = parse_address(data.get('address', ''))
    
    # --- 3. Handle birthday and logic for year being 1 ---
    birthday_obj = None
    bday_str = data.get('bday', '')
    if bday_str and " at " in bday_str:
        try:
            # Extract date part: "May 12, 2001" or "May 12, 1"
            date_part = bday_str.split(' at ')[0]
            
            # Manually handle case where year is 1 to prevent strptime errors
            month_day, year_str = date_part.rsplit(', ', 1)
            year_val = int(year_str)
            
            # Parse month and day
            dt = datetime.datetime.strptime(month_day, "%b %d")
            
            date_data = {"month": dt.month, "day": dt.day}
            # If year is not 1, add the year
            if year_val > 1:
                date_data["year"] = year_val
            
            birthday_obj = [{"date": date_data}]
        except Exception as e:
            print(f"Birthday parsing failed: {e}")

    # --- 4. Build Request Body ---
    body = {
        "names": [{"givenName": data.get('fname', ''), "familyName": data.get('lname', '')}],
        "phoneNumbers": [{"value": p} for p in phones],
        "emailAddresses": emails,
        "urls": urls,
        "biographies": [{"value": data.get('note', '')}],
        "addresses": [parsed_addr]
    }
    if birthday_obj:
        body["birthdays"] = birthday_obj

    # Find existing contact by name to determine update vs create
    fname = data.get('fname', '')
    lname = data.get('lname', '')
    resource_name, etag = find_existing_contact_by_name(service, fname, lname)

    update_fields = "names,emailAddresses,phoneNumbers,urls,biographies,addresses,birthdays"

    try:
        if resource_name:
            body['etag'] = etag
            contact = service.people().updateContact(
                resourceName=resource_name,
                updatePersonFields=update_fields,
                body=body
            ).execute()
            print(f"🔄 Successfully updated contact: {contact.get('resourceName')}")
        else:
            contact = service.people().createContact(body=body).execute()
            print(f"✅ Successfully created contact: {contact.get('resourceName')}")
    except Exception as e:
        print(f"❌ Something went wrong: {e}")


# def get_service_from_env(env_var_name):
#     """Retrieve Google People service using credentials from file or environment"""
#     if __name__ == '__main__':
#         # Use local JSON file for testing
#         creds = Credentials.from_authorized_user_file(f'{env_var_name}.json', SCOPES)
#     else:
#         # Get token from GitHub Secrets/Environment Variables
#         token_data = json.loads(os.environ.get(env_var_name))
#         creds = Credentials.from_authorized_user_info(token_data)
#     return build('people', 'v1', credentials=creds)


def main(payload, service_a, service_b):
    # Initialize services
    # if __name__ == '__main__':
    #     service_a = get_service_from_env('token_a')
    #     service_b = get_service_from_env('token_b')
    # else:
    #     service_a = get_service_from_env('GMAIL_TOKEN_A')
    #     service_b = get_service_from_env('GMAIL_TOKEN_B')
    
    # Create or update contacts in both accounts
    upsert_contact(service_a, payload)
    upsert_contact(service_b, payload)


if __name__ == '__main__':
    main(raw_payload)