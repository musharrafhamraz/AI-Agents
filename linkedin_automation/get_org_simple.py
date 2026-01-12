"""Simple script to get organization URN using different API endpoints."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_organizations():
    """Try multiple methods to get organization URN."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in .env file")
        return
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    print("=" * 60)
    print("Trying to Find Your Organization URN")
    print("=" * 60)
    print()
    
    # Method 1: Try to get user info first
    print("Method 1: Getting your profile info...")
    try:
        response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Profile: {data.get('name', 'N/A')}")
        print(f"   Sub: {data.get('sub', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Method 2: Try organizationAcls (might fail without permissions)
    print("Method 2: Trying organizationAcls endpoint...")
    try:
        url = "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        elements = data.get('elements', [])
        
        if elements:
            print(f"✅ Found {len(elements)} organization(s)!")
            for elem in elements:
                org_urn = elem.get('organization', '')
                print(f"   Organization URN: {org_urn}")
            print()
            return elements
        else:
            print("❌ No organizations found")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Method 3: Try to get organizations via me endpoint
    print("Method 3: Trying /v2/me endpoint...")
    try:
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Profile ID: {data.get('id', 'N/A')}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 60)
    print("Manual Method:")
    print("=" * 60)
    print()
    print("If the above methods didn't work, try this:")
    print()
    print("1. Go to your LinkedIn company page")
    print("2. Look at the URL, it should be:")
    print("   https://www.linkedin.com/company/YOUR-COMPANY-NAME/")
    print()
    print("3. Right-click on the page and 'View Page Source'")
    print("4. Search for 'organizationId' or look for a number after 'company/'")
    print()
    print("5. Once you have the organization ID (just the number), add to .env:")
    print("   LINKEDIN_ORGANIZATION_URN=urn:li:organization:YOUR_NUMBER")
    print()
    print("Example:")
    print("   If your company URL is: linkedin.com/company/12345678")
    print("   Then add: LINKEDIN_ORGANIZATION_URN=urn:li:organization:12345678")
    print()

if __name__ == "__main__":
    get_organizations()
