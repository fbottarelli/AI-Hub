from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import os

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class EnvConfig:
    """Environment variables configuration"""
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # Add more environment variables here as needed

class DownloadConfig:
    # Directory settings
    DOWNLOAD_DIR = Path(__file__).parent.parent.parent.parent / "downloads"
    
    # Video download settings
    VIDEO_FORMAT = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    VIDEO_EXT = '.mp4'
    
    # Audio download settings
    AUDIO_FORMAT = 'bestaudio/best'
    AUDIO_CODEC = 'mp3'
    AUDIO_QUALITY = '192'
    AUDIO_EXT = '.mp3'
    
    # Subtitle settings
    SUPPORTED_LANGS: Dict[str, str] = {
        'en': 'English',
        'it': 'Italian'
    }
    DEFAULT_LANG = 'en'
    SUBTITLE_EXT = '.vtt'

class YTDLConfig:
    # Common yt-dlp options
    COMMON_OPTS = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'no_check_certificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
        'socket_timeout': 30,
    }
    
    # URL validation options
    VALIDATE_OPTS = {
        **COMMON_OPTS,
        'extract_flat': True
    }
    
    # Video download options template
    VIDEO_OPTS_TEMPLATE = {
        **COMMON_OPTS,
        'format': DownloadConfig.VIDEO_FORMAT,
        'progress_hooks': None,  # Set in runtime
    }
    
    # Audio download options template
    AUDIO_OPTS_TEMPLATE = {
        **COMMON_OPTS,
        'format': DownloadConfig.AUDIO_FORMAT,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': DownloadConfig.AUDIO_CODEC,
            'preferredquality': DownloadConfig.AUDIO_QUALITY,
        }],
        'progress_hooks': None,  # Set in runtime
    }
    
    # Subtitle options templates
    SUBTITLE_CHECK_OPTS = {
        **COMMON_OPTS,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'skip_download': True,
    }
    
    SUBTITLE_DOWNLOAD_OPTS_TEMPLATE = {
        **COMMON_OPTS,
        'skip_download': True,
        'writesubtitles': True,  # Will be set based on availability
        'writeautomaticsub': False,  # Will be set based on availability
        'subtitleslangs': None,  # Set in runtime
    }

class LLMConfig:
    # Default settings
    DEFAULT_TEMPERATURE = 0.7
    
    # Temperature presets
    CREATIVE_TEMP = 0.7  # For creative tasks like thread generation
    ANALYTICAL_TEMP = 0.3  # For analytical tasks like sentiment analysis
    BALANCED_TEMP = 0.5  # For balanced tasks like hashtag suggestions 