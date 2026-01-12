"""Get Organization URN from LinkedIn company page URL."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_org_urn_from_vanity_name(vanity_name):
    """Get organization URN from vanity name (company page URL)."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in .env file")
        return
    
    print("=" * 60)
    print("Getting Organization URN from Company Page")
    print("=" * 60)
    print()
    
    print(f"Looking up company page: {vanity_name}")
    print()
    
    # Try to get organization by vanity name
    url = f"https://api.linkedin.com/v2/organizations"
    params = {
        "q": "vanityName",
        "vanityName": vanity_name
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        elements = data.get('elements', [])
        
        if not elements:
            print(f"❌ No company page found with vanity name: {vanity_name}")
            print()
            print("Make sure you're using the correct vanity name from the URL:")
            print("https://www.linkedin.com/company/YOUR-VANITY-NAME/")
            return
        
        org = elements[0]
        org_id = org.get('id', '')
        org_name = org.get('localizedName', 'Unknown')
        org_urn = f"urn:li:organization:{org_id}"
        
        print("✅ Found company page!")
        print()
        print(f"Name: {org_name}")
        print(f"ID: {org_id}")
        print(f"Organization URN: {org_urn}")
        print()
        print("=" * 60)
        print("✅ Update Your .env File:")
        print("=" * 60)
        print()
        print("Replace this line:")
        print("LINKEDIN_PERSON_URN=urn:li:person:ORoarea9uO")
        print()
        print("With this line:")
        print(f"# LINKEDIN_PERSON_URN=urn:li:person:ORoarea9uO")
        print(f"LINKEDIN_ORGANIZATION_URN={org_urn}")
        print()
        print("⚠️ IMPORTANT:")
        print("To post to company pages, you need:")
        print("1. 'Marketing Developer Platform' product approved in your LinkedIn app")
        print("2. Admin access to the company page")
        print("3. New access token with w_organization_social permission")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    print()
    print("Enter your LinkedIn company page vanity name")
    print("(from URL: https://www.linkedin.com/company/YOUR-VANITY-NAME/)")
    print()
    vanity_name = input("Vanity name: ").strip()
    
    if vanity_name:
        print()
        get_org_urn_from_vanity_name(vanity_name)
    else:
        print("❌ No vanity name provided")
