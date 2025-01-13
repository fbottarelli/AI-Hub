import gradio as gr
import logging
from pathlib import Path
import sys

from src.backend.config.settings import DownloadConfig, EnvConfig
from src.frontend.config.ui_settings import UIConfig
from src.frontend.tabs.youtube_tab import create_youtube_tab
from src.frontend.tabs.twitter_tab import create_twitter_tab
from src.frontend.tabs.github_tab import create_github_tab

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    if not EnvConfig.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found in environment variables")
        sys.exit(1)
    logger.info("Environment variables loaded successfully")

# Create downloads directory if it doesn't exist
DownloadConfig.DOWNLOAD_DIR.mkdir(exist_ok=True)

# Create the main app with multiple pages
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Check environment variables before starting
    check_environment()
    
    gr.Markdown(UIConfig.APP_TITLE)
    
    with gr.Tabs():
        with gr.Tab("GitHub Utilities"):
            create_github_tab()
            
        with gr.Tab("YouTube Utilities"):
            create_youtube_tab()
        
        with gr.Tab("Twitter/X Utilities"):
            create_twitter_tab()
        
        # Add more tabs here for future utilities
        with gr.Tab("Coming Soon"):
            gr.Markdown("More utilities coming soon!")

if __name__ == "__main__":
    demo.launch() 