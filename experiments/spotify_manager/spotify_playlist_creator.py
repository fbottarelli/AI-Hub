import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional
import sys
from dotenv import load_dotenv

load_dotenv()

# Spotify API credentials - these should be set as environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Main folder name for all mood playlists
MAIN_FOLDER_NAME = "Mood Collection"

# List of mood categories (descriptions are in README.md)
MOODS = [
    "Joyful & Happy",
    "Melancholic & Wistful",
    "Energetic & Hyper",
    "Peaceful & Serene",
    "Romantic & Affectionate",
    "Nostalgic & Sentimental",
    "Motivated & Inspired",
    "Angry & Irritated",
    "Relaxed & Laid-back",
    "Dreamy & Ethereal",
    "Dark & Brooding",
    "Party & Festive",
    "Reflective & Pensive",
    "Lonely & Isolated",
    "Confident & Bold",
    "Adventurous & Exploratory",
    "Mysterious & Enigmatic",
    "Hopeful & Optimistic",
    "Euphoric & Ecstatic",
    "Anxious & Tense",
    "Playful & Whimsical",
    "Intense & Dramatic",
    "Surreal & Cosmic",
    "Sophisticated & Minimal",
    "Nature & Grandeur"
]

class SpotifyPlaylistCreator:
    def __init__(self, dry_run: bool = False):
        """
        Initialize Spotify client with necessary permissions.
        
        Args:
            dry_run (bool): If True, no actual changes will be made to Spotify
        """
        self.dry_run = dry_run
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="playlist-modify-public playlist-modify-private"
        ))
        self.user_id = self.sp.current_user()["id"]
        self.main_folder_id = None

    def get_existing_playlists(self) -> dict:
        """Get names and IDs of all existing playlists to avoid duplicates."""
        existing_playlists = {}
        results = self.sp.current_user_playlists()
        
        while results:
            for item in results['items']:
                existing_playlists[item['name']] = item['id']
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        return existing_playlists

    def create_or_get_main_folder(self, existing_playlists: dict) -> Optional[str]:
        """Create or get the main folder for mood playlists."""
        if MAIN_FOLDER_NAME in existing_playlists:
            print(f"Using existing folder: {MAIN_FOLDER_NAME}")
            return existing_playlists[MAIN_FOLDER_NAME]
        
        if self.dry_run:
            print(f"[DRY RUN] Would create main folder: {MAIN_FOLDER_NAME}")
            return "dry-run-folder-id"
            
        try:
            folder = self.sp.user_playlist_create(
                user=self.user_id,
                name=MAIN_FOLDER_NAME,
                public=True,
                description="A curated collection of mood-based playlists, organized by emotional themes."
            )
            print(f"Created main folder: {MAIN_FOLDER_NAME}")
            return folder["id"]
        except Exception as e:
            print(f"Error creating main folder: {str(e)}")
            return None

    def create_mood_playlist(self, mood: str, existing_playlists: dict) -> str:
        """
        Create a new playlist for a specific mood if it doesn't already exist.
        
        Args:
            mood (str): The mood/theme for the playlist
            existing_playlists (dict): Dictionary of existing playlist names and IDs
            
        Returns:
            str: The ID of the created playlist or None if not created
        """
        playlist_name = f"Mood: {mood}"
        
        # Check if playlist already exists
        if playlist_name in existing_playlists:
            print(f"Skipping '{playlist_name}' - Already exists")
            return None
        
        description = f"A curated playlist for {mood.lower()} moments. Part of {MAIN_FOLDER_NAME}."
        
        if self.dry_run:
            print(f"[DRY RUN] Would create playlist: {playlist_name}")
            return "dry-run-id"
            
        try:
            # Create the playlist
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=playlist_name,
                public=True,
                description=description
            )
            print(f"Created playlist: {playlist_name}")
            return playlist["id"]
        except Exception as e:
            print(f"Error creating playlist {playlist_name}: {str(e)}")
            return None

    def create_all_mood_playlists(self) -> List[str]:
        """
        Create main folder and all mood playlists within it.
        
        Returns:
            List[str]: List of created playlist IDs
        """
        # Get existing playlists first
        existing_playlists = self.get_existing_playlists()
        
        # Create or get main folder
        self.main_folder_id = self.create_or_get_main_folder(existing_playlists)
        if not self.main_folder_id:
            print("Failed to create/get main folder. Aborting.")
            return []
        
        playlist_ids = []
        for mood in MOODS:
            playlist_id = self.create_mood_playlist(mood, existing_playlists)
            if playlist_id:
                playlist_ids.append(playlist_id)
        return playlist_ids

def get_user_confirmation(num_playlists: int) -> bool:
    """Get user confirmation before proceeding with playlist creation."""
    print(f"\nThis will create a main folder '{MAIN_FOLDER_NAME}' (if it doesn't exist)")
    print(f"and up to {num_playlists} mood playlists inside it.")
    print("Existing playlists with the same names will be skipped.")
    response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
    return response in ['yes', 'y']

def main():
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("Running in DRY RUN mode - No changes will be made to your Spotify account")
    
    # Check if environment variables are set
    required_env_vars = ['SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET', 'SPOTIPY_REDIRECT_URI']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these environment variables before running the script.")
        return

    # Create playlist creator instance
    creator = SpotifyPlaylistCreator(dry_run=dry_run)
    
    # Get user confirmation before proceeding
    if not dry_run and not get_user_confirmation(len(MOODS)):
        print("Operation cancelled by user.")
        return
    
    # Create all mood playlists
    print("\nStarting to create mood playlists...")
    playlist_ids = creator.create_all_mood_playlists()
    
    if dry_run:
        print(f"\n[DRY RUN] Would have created main folder and {len(playlist_ids)} new playlists")
    else:
        print(f"\nCreated main folder and {len(playlist_ids)} new playlists successfully!")

if __name__ == "__main__":
    main() 