# Generate token.json from each of your gmail account
# Since you have 2 gmail accounts we need to run this script twice with different names like token_a.json and token_b.json
# this code is used to run locally with Python and Visual Studio Code installed

from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ['https://www.googleapis.com/auth/contacts']

def generate_token(filename):
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    # select your account
    creds = flow.run_local_server(port=0, prompt='select_account', access_type='offline')
    with open(filename, 'w') as f:
        f.write(creds.to_json())

if __name__ == '__main__':
    # generate_token('token_a.json')
    generate_token('token_b.json')