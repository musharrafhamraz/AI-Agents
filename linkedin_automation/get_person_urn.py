"""Get LinkedIn Person URN from existing access token."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_person_urn():
    """Get the person URN using the existing access token."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in .env file")
        return
    
    print("=" * 60)
    print("Getting Your LinkedIn Person URN")
    print("=" * 60)
    print()
    
    print("✅ Access token found in .env file")
    print()
    
    # Get user info
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        print("Fetching your LinkedIn profile information...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        print("✅ Successfully retrieved profile information!")
        print()
        print("Profile Details:")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Email: {data.get('email', 'N/A')}")
        print(f"  Sub (Person ID): {data.get('sub', 'N/A')}")
        print()
        
        # Generate Person URN
        person_id = data.get('sub')
        if person_id:
            person_urn = f"urn:li:person:{person_id}"
            
            print("=" * 60)
            print("✅ Your Person URN:")
            print("=" * 60)
            print()
            print(f"LINKEDIN_PERSON_URN={person_urn}")
            print()
            print("=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print()
            print("1. Copy the line above")
            print("2. Open your .env file")
            print("3. Replace this line:")
            print("   LINKEDIN_PERSON_URN=urn:li:person:YOUR_PERSON_ID")
            print("   with:")
            print(f"   LINKEDIN_PERSON_URN={person_urn}")
            print()
            print("4. Save the .env file")
            print("5. Run: python test_linkedin_post.py")
            print()
        else:
            print("❌ Error: Could not extract person ID from response")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            print()
            if e.response.status_code == 401:
                print("Your access token may have expired.")
                print("LinkedIn tokens expire after 60 days.")
                print()
                print("To get a new token:")
                print("1. Run: python get_token_simple.py")
                print("2. Follow the instructions")

if __name__ == "__main__":
    get_person_urn()
