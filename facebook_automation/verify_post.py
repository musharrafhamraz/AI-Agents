"""Verify if the latest post has an image attached."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
page_id = os.getenv("FACEBOOK_PAGE_ID")

# Get the latest post
url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
params = {
    "fields": "id,message,full_picture,attachments,created_time",
    "limit": 1,
    "access_token": page_access_token
}

response = requests.get(url, params=params)
data = response.json()

if "data" in data and len(data["data"]) > 0:
    post = data["data"][0]
    print("Latest Post Details:")
    print(f"Post ID: {post.get('id')}")
    print(f"Message: {post.get('message', 'No message')[:100]}...")
    print(f"Created: {post.get('created_time')}")
    print(f"\nHas full_picture: {'Yes' if post.get('full_picture') else 'No'}")
    if post.get('full_picture'):
        print(f"Image URL: {post.get('full_picture')}")
    print(f"\nHas attachments: {'Yes' if post.get('attachments') else 'No'}")
    if post.get('attachments'):
        print(f"Attachments: {post.get('attachments')}")
else:
    print("No posts found or error:", data)
