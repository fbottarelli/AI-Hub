from pathlib import Path
from typing import Dict, Any

class DownloadConfig:
    # Directory settings
    DOWNLOAD_DIR = Path("downloads")
    
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
    }
    
    # URL validation options
    VALIDATE_OPTS = {
        **COMMON_OPTS,
        'extract_flat': True
    }
    
    # Video download options template
    VIDEO_OPTS_TEMPLATE = {
        'format': DownloadConfig.VIDEO_FORMAT,
        'progress_hooks': None,  # Set in runtime
    }
    
    # Audio download options template
    AUDIO_OPTS_TEMPLATE = {
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
        'skip_download': True,
        'writesubtitles': True,  # Will be set based on availability
        'writeautomaticsub': False,  # Will be set based on availability
        'subtitleslangs': None,  # Set in runtime
    }

class UIConfig:
    # App title and description
    APP_TITLE = "🚀 Personal Multi-Utility Hub"
    YT_TAB_TITLE = "🎥 YouTube Utility Hub"
    
    YT_TAB_DESCRIPTION = """
    Enter a YouTube URL to:
    - Download video (MP4)
    - Extract audio (MP3)
    - Download subtitles (English or Italian)
    - Generate AI summary
    
    All files will be saved in the `downloads` folder.
    """
    
    # Download formats
    FORMATS = ["Video (MP4)", "Audio (MP3)", "Subtitles"]
    DEFAULT_FORMAT = "Video (MP4)"
    
    # UI Components settings
    URL_PLACEHOLDER = "Enter YouTube video URL..."
    STATUS_LINES = 3
    SUMMARY_LINES = 10

class SummaryConfig:
    # OpenAI settings
    TEMPERATURE = 0.7
    
    # Summary prompt template
    PROMPT_TEMPLATE = """
    Please provide a concise summary of this YouTube video based on its title and description:
    
    Title: {title}
    Description: {description}
    
    Please structure the summary with:
    1. Main topic/theme
    2. Key points
    3. Target audience
    """ 