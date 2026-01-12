"""
LinkedIn OAuth 2.0 Token Generator

This script helps you obtain a LinkedIn access token using OAuth 2.0 flow.

Steps:
1. Create a LinkedIn App at https://www.linkedin.com/developers/apps
2. Add redirect URL: http://localhost:8000/callback
3. Request permissions: w_member_social, r_basicprofile (for personal profile)
   OR w_organization_social, r_organization_social (for company page)
4. Run this script and follow the instructions
"""

import os
import requests
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

# LinkedIn OAuth Configuration
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "https://www.linkedin.com/developers/tools/oauth/redirect"

# Scopes for personal profile
# SCOPES = ["openid", "profile", "w_member_social", "r_basicprofile"]

# For organization/company page, use these scopes instead:
SCOPES = ["openid", "profile", "w_organization_social", "r_organization_social", "rw_organization_admin"]

# Global variable to store the authorization code
auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""
    
    def do_GET(self):
        global auth_code
        
        # Parse the callback URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = query_params.get('error', ['Unknown error'])[0]
            self.wfile.write(f"""
                <html>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
            """.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


def get_authorization_url():
    """Generate LinkedIn authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    return auth_url


def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    
    return response.json()


def get_person_urn(access_token):
    """Get the person URN for the authenticated user"""
    url = "https://api.linkedin.com/v2/userinfo"
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    person_id = data.get('sub')
    
    if person_id:
        return f"urn:li:person:{person_id}"
    return None


def get_organization_urns(access_token):
    """Get organization URNs for pages you manage"""
    url = "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        elements = data.get('elements', [])
        
        orgs = []
        for elem in elements:
            org_urn = elem.get('organization', '')
            if org_urn:
                orgs.append(org_urn)
        
        return orgs
    except Exception as e:
        print(f"Note: Could not fetch organizations: {e}")
        return []


def main():
    """Main function to run the OAuth flow"""
    global auth_code
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env file")
        print("\nSteps to get credentials:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Create a new app or select existing app")
        print("3. Copy Client ID and Client Secret")
        print("4. Add them to your .env file")
        return
    
    print("=" * 60)
    print("LinkedIn OAuth 2.0 Token Generator")
    print("=" * 60)
    print()
    
    # Step 1: Generate authorization URL
    auth_url = get_authorization_url()
    print("Step 1: Authorize the application")
    print("-" * 60)
    print("Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("After authorization, you'll be redirected to a page showing the authorization code.")
    print()
    
    # Step 2: Get authorization code manually
    print("Step 2: Enter the authorization code")
    print("-" * 60)
    auth_code = input("Paste the authorization code here: ").strip()
    print()
    
    if not auth_code:
        print("❌ Error: No authorization code provided")
        return
    
    print("✅ Authorization code received!")
    print()
    
    # Step 3: Exchange code for access token
    print("Step 3: Exchanging code for access token...")
    print("-" * 60)
    
    try:
        token_data = exchange_code_for_token(auth_code)
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')
        
        print("✅ Access token obtained successfully!")
        print()
        print(f"Access Token: {access_token}")
        print(f"Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
        print()
        
        # Step 4: Get person URN
        print("Step 4: Getting your LinkedIn Person URN...")
        print("-" * 60)
        
        person_urn = get_person_urn(access_token)
        
        if person_urn:
            print(f"✅ Person URN: {person_urn}")
            print()
        
        # Step 4b: Get organization URNs
        print("Step 4b: Getting your Organization URNs...")
        print("-" * 60)
        
        org_urns = get_organization_urns(access_token)
        
        if org_urns:
            print(f"✅ Found {len(org_urns)} organization(s):")
            for org_urn in org_urns:
                print(f"   {org_urn}")
            print()
        else:
            print("⚠️  No organizations found or insufficient permissions")
            print()
        
        # Step 5: Update .env file
        print("Step 5: Update your .env file")
        print("-" * 60)
        print("Add these lines to your .env file:")
        print()
        print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
        if person_urn:
            print(f"# LINKEDIN_PERSON_URN={person_urn}")
        if org_urns:
            print(f"LINKEDIN_ORGANIZATION_URN={org_urns[0]}")
        print()
        print("=" * 60)
        print("✅ Setup complete! You can now use the LinkedIn automation.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
