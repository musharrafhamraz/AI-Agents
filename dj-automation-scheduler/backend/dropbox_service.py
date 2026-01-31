import dropbox
from dropbox.exceptions import ApiError
import os
from dotenv import load_dotenv
from typing import Optional, Tuple
import mimetypes

load_dotenv()

class DropboxService:
    def __init__(self):
        self.access_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("DROPBOX_ACCESS_TOKEN not found in environment")
        
        print(f"Initializing Dropbox with token (first 20 chars): {self.access_token[:20]}...")
        
        try:
            self.dbx = dropbox.Dropbox(self.access_token)
            # Test the connection
            self.dbx.users_get_current_account()
            print("Dropbox connection successful!")
        except Exception as e:
            print(f"Dropbox initialization failed: {str(e)}")
            raise ValueError(f"Failed to initialize Dropbox: {str(e)}")
    
    def upload_file(self, file_path: str, file_content: bytes, folder: str = "/dj-assets") -> Tuple[bool, str, Optional[str]]:
        """
        Upload a file to Dropbox
        Returns: (success, dropbox_path, error_message)
        """
        try:
            # Ensure folder path starts with /
            if not folder.startswith("/"):
                folder = f"/{folder}"
            
            # Create full path
            full_path = f"{folder}/{file_path}"
            
            # Upload file
            self.dbx.files_upload(
                file_content,
                full_path,
                mode=dropbox.files.WriteMode.overwrite
            )
            
            return True, full_path, None
        except ApiError as e:
            return False, "", str(e)
        except Exception as e:
            return False, "", str(e)
    
    def create_shared_link(self, dropbox_path: str) -> Optional[str]:
        """
        Create a shared link for a file
        Returns the direct streaming URL
        """
        try:
            # Check if shared link already exists
            try:
                links = self.dbx.sharing_list_shared_links(path=dropbox_path)
                if links.links:
                    url = links.links[0].url
                    # Convert to streaming link (raw=1 for streaming, not download)
                    if '?dl=0' in url:
                        url = url.replace('?dl=0', '?raw=1')
                    elif '&dl=0' in url:
                        url = url.replace('&dl=0', '&raw=1')
                    elif '&dl=1' in url:
                        url = url.replace('&dl=1', '&raw=1')
                    elif 'www.dropbox.com' in url:
                        url = url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                        if '?' not in url:
                            url = url + '?raw=1'
                    elif not 'raw=1' in url:
                        url = url + ('&' if '?' in url else '?') + 'raw=1'
                    print(f"Using existing shared link: {url}")
                    return url
            except:
                pass
            
            # Create new shared link
            shared_link = self.dbx.sharing_create_shared_link_with_settings(dropbox_path)
            url = shared_link.url
            
            # Convert to streaming link
            if '?dl=0' in url:
                url = url.replace('?dl=0', '?raw=1')
            elif '&dl=0' in url:
                url = url.replace('&dl=0', '&raw=1')
            elif 'www.dropbox.com' in url:
                url = url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
                if '?' not in url:
                    url = url + '?raw=1'
            elif not 'raw=1' in url:
                url = url + ('&' if '?' in url else '?') + 'raw=1'
            
            print(f"Created new shared link: {url}")
            return url
        except ApiError as e:
            print(f"Error creating shared link: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def list_files(self, folder: str = "/dj-assets") -> list:
        """
        List all files in a folder with detailed metadata
        """
        try:
            result = self.dbx.files_list_folder(folder)
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Get or create shared link
                    shared_url = self.create_shared_link(entry.path_display)
                    
                    files.append({
                        "name": entry.name,
                        "path": entry.path_display,
                        "size": entry.size,
                        "modified": str(entry.client_modified),
                        "shared_url": shared_url,
                        "is_audio": self._is_audio_file(entry.name)
                    })
            return files
        except ApiError as e:
            print(f"Error listing files: {e}")
            return []
    
    def _is_audio_file(self, filename: str) -> bool:
        """Check if file is an audio file"""
        audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma']
        return any(filename.lower().endswith(ext) for ext in audio_extensions)
    
    def delete_file(self, dropbox_path: str) -> bool:
        """
        Delete a file from Dropbox
        """
        try:
            self.dbx.files_delete_v2(dropbox_path)
            return True
        except ApiError:
            return False

# Singleton instance
dropbox_service = DropboxService()
