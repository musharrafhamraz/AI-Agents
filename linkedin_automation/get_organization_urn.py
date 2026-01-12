"""Get LinkedIn Organization URN for company pages you manage."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_organization_urn():
    """Get the organization URN for company pages you manage."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in .env file")
        return
    
    print("=" * 60)
    print("Getting Your LinkedIn Organization/Company Pages")
    print("=" * 60)
    print()
    
    print("✅ Access token found in .env file")
    print()
    
    # Get organizations/pages you manage
    url = "https://api.linkedin.com/v2/organizationAcls"
    params = {
        "q": "roleAssignee",
        "projection": "(elements*(organization~(localizedName,vanityName),roleAssignee,state))"
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    try:
        print("Fetching your company pages...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        elements = data.get('elements', [])
        
        if not elements:
            print("❌ No company pages found.")
            print()
            print("This could mean:")
            print("1. You don't have admin access to any LinkedIn company pages")
            print("2. Your access token doesn't have the required permissions")
            print()
            print("Required permissions:")
            print("- w_organization_social (to post to company page)")
            print("- r_organization_social (to read company page info)")
            print()
            print("To get these permissions:")
            print("1. Go to your LinkedIn App settings")
            print("2. Request 'Marketing Developer Platform' product")
            print("3. Wait for approval (can take 1-2 days)")
            return
        
        print(f"✅ Found {len(elements)} company page(s)!")
        print()
        print("=" * 60)
        print("Your Company Pages:")
        print("=" * 60)
        print()
        
        for i, element in enumerate(elements, 1):
            org_info = element.get('organization~', {})
            org_urn = element.get('organization', '')
            org_name = org_info.get('localizedName', 'Unknown')
            vanity_name = org_info.get('vanityName', 'N/A')
            state = element.get('state', 'Unknown')
            
            print(f"{i}. {org_name}")
            print(f"   Vanity Name: {vanity_name}")
            print(f"   Organization URN: {org_urn}")
            print(f"   Status: {state}")
            print()
        
        # If only one page, show instructions
        if len(elements) == 1:
            org_urn = elements[0].get('organization', '')
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
            print("(Comment out PERSON_URN and add ORGANIZATION_URN)")
            print()
        else:
            print("=" * 60)
            print("Multiple Pages Found")
            print("=" * 60)
            print()
            print("Choose which page you want to post to and add to .env:")
            print()
            print("# LINKEDIN_PERSON_URN=urn:li:person:ORoarea9uO")
            print("LINKEDIN_ORGANIZATION_URN=<your_chosen_urn>")
            print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            print()
            
            if e.response.status_code == 403:
                print("Permission Error!")
                print()
                print("Your access token doesn't have permission to access company pages.")
                print()
                print("To fix this:")
                print("1. Go to https://www.linkedin.com/developers/apps")
                print("2. Select your app")
                print("3. Go to 'Products' tab")
                print("4. Request 'Marketing Developer Platform'")
                print("5. Wait for approval (1-2 days)")
                print("6. Run get_token_simple.py again to get new token with permissions")

if __name__ == "__main__":
    get_organization_urn()
