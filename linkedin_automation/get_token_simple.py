"""
Simplified LinkedIn OAuth Token Generator
This version provides step-by-step instructions
"""

import os
import webbrowser
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = ["openid", "profile", "w_member_social", "r_basicprofile"]

def main():
    print("=" * 70)
    print("LinkedIn OAuth 2.0 Token Generator - Simple Version")
    print("=" * 70)
    print()
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET not found in .env")
        print()
        print("Please add them to your .env file:")
        print("LINKEDIN_CLIENT_ID=your_client_id")
        print("LINKEDIN_CLIENT_SECRET=your_client_secret")
        return
    
    print("✅ Credentials found in .env file")
    print()
    print("=" * 70)
    print("STEP 1: Authorize the Application")
    print("=" * 70)
    print()
    
    # Generate authorization URL
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    print("I will open this URL in your browser:")
    print()
    print(auth_url)
    print()
    input("Press ENTER to open the browser...")
    
    # Open browser
    webbrowser.open(auth_url)
    
    print()
    print("=" * 70)
    print("STEP 2: After Authorization")
    print("=" * 70)
    print()
    print("After you authorize:")
    print("1. You'll be redirected to: http://localhost:8000/callback?code=...")
    print("2. The page will show an error (that's normal - we just need the code)")
    print("3. Copy the ENTIRE URL from your browser's address bar")
    print()
    print("Example URL:")
    print("http://localhost:8000/callback?code=AQTxxx...&state=xxx")
    print()
    
    callback_url = input("Paste the full callback URL here: ").strip()
    
    if not callback_url or 'code=' not in callback_url:
        print()
        print("❌ Error: Invalid URL. Please make sure you copied the full URL.")
        return
    
    # Extract code
    try:
        code = callback_url.split('code=')[1].split('&')[0]
        print()
        print(f"✅ Authorization code extracted: {code[:20]}...")
        print()
    except:
        print()
        print("❌ Error: Could not extract code from URL")
        return
    
    print("=" * 70)
    print("STEP 3: Exchange Code for Access Token")
    print("=" * 70)
    print()
    
    import requests
    
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')
        
        print("✅ Access token obtained successfully!")
        print()
        print(f"Access Token: {access_token}")
        print(f"Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
        print()
        
        # Get Person URN
        print("=" * 70)
        print("STEP 4: Getting Your Person URN")
        print("=" * 70)
        print()
        
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
        
        person_id = userinfo.get('sub')
        person_urn = f"urn:li:person:{person_id}"
        
        print(f"✅ Person URN: {person_urn}")
        print()
        
        # Display final instructions
        print("=" * 70)
        print("STEP 5: Update Your .env File")
        print("=" * 70)
        print()
        print("Add these lines to your .env file:")
        print()
        print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
        print(f"LINKEDIN_PERSON_URN={person_urn}")
        print()
        print("=" * 70)
        print("✅ Setup Complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Copy the lines above to your .env file")
        print("2. Run: python test_linkedin_post.py")
        print("3. Run: crewai run")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()
