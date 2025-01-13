import yt_dlp
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

from ..utils.llm import call_llm
from ..utils.file_utils import sanitize_filename
from ..config.settings import DownloadConfig, YTDLConfig

logger = logging.getLogger(__name__)

class YouTubeService:
    @staticmethod
    def validate_url(url: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Validate YouTube URL and return video info"""
        try:
            with yt_dlp.YoutubeDL(YTDLConfig.VALIDATE_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)
                logger.info(f"Video found: {info['title']} (Duration: {info['duration']} seconds)")
                return info, None
        except Exception as e:
            error_msg = f"Error in URL validation: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def download_video(url: str, sanitized_title: str, info: dict) -> Tuple[Optional[str], Optional[str]]:
        """Download video in MP4 format"""
        try:
            logger.info(f"Attempting to download video: {info['title']}")
            
            # Get current working directory and target directory
            current_dir = Path.cwd()
            download_dir = DownloadConfig.DOWNLOAD_DIR.resolve()
            
            logger.info(f"Current working directory: {current_dir}")
            logger.info(f"Target download directory: {download_dir}")
            
            # Create downloads directory if it doesn't exist
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Create absolute output path
            output_path = download_dir / sanitized_title
            logger.info(f"Output path: {output_path}")
            
            ydl_opts = {
                **YTDLConfig.VIDEO_OPTS_TEMPLATE,
                'paths': {'home': str(download_dir)},  # Set the base download directory
                'outtmpl': {
                    'default': str(output_path) + '.%(ext)s'
                },
                'progress_hooks': [lambda d: logger.info(f"Download progress: {d.get('status', 'unknown')}")],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Starting video download")
                logger.info(f"Using options: {ydl_opts}")
                ydl.download([url])
                
            output_file = str(download_dir / f"{sanitized_title}{DownloadConfig.VIDEO_EXT}")
            logger.info(f"Video downloaded to: {output_file}")
            return f"Video downloaded successfully:\nFile: {output_file}", None
        except Exception as e:
            error_msg = f"Error downloading video: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def download_audio(url: str, sanitized_title: str, info: dict) -> Tuple[Optional[str], Optional[str]]:
        """Download audio in MP3 format"""
        try:
            logger.info(f"Attempting to download audio for: {info['title']}")
            # Create downloads directory if it doesn't exist
            DownloadConfig.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
            # Use absolute path for output template with explicit directory prefix
            output_template = str(DownloadConfig.DOWNLOAD_DIR.absolute() / sanitized_title)
            
            ydl_opts = {
                **YTDLConfig.AUDIO_OPTS_TEMPLATE,
                'outtmpl': f'{output_template}.%(ext)s',
                'progress_hooks': [lambda d: logger.info(f"Download progress: {d.get('status', 'unknown')}")],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("Starting audio download")
                ydl.download([url])
                
            output_file = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}{DownloadConfig.AUDIO_EXT}")
            logger.info(f"Audio downloaded to: {output_file}")
            return f"Audio downloaded successfully:\nQuality: {DownloadConfig.AUDIO_QUALITY}kbps\nFile: {output_file}", None
        except Exception as e:
            error_msg = f"Error downloading audio: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def download_subtitles(url: str, sanitized_title: str, info: dict, subtitle_lang: str) -> Tuple[Optional[str], Optional[str]]:
        """Download video subtitles"""
        try:
            # Convert display name to language code
            lang_code_map = {v: k for k, v in DownloadConfig.SUPPORTED_LANGS.items()}
            subtitle_lang = lang_code_map.get(subtitle_lang, DownloadConfig.DEFAULT_LANG)
                
            logger.info(f"Attempting to fetch {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles for: {info['title']}")
            output_template = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}%(ext)s")
            
            # Check subtitle availability
            with yt_dlp.YoutubeDL(YTDLConfig.SUBTITLE_CHECK_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)
                
                has_manual = subtitle_lang in info.get('subtitles', {})
                has_auto = subtitle_lang in info.get('automatic_captions', {})
                
                if not has_manual and not has_auto:
                    msg = f"No {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles or captions available"
                    logger.warning(msg)
                    return None, msg
                
                # Prefer manual subtitles over auto-generated
                is_auto = not has_manual and has_auto
                logger.info(f"Found {'auto-generated' if is_auto else 'manual'} {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles")
                
                # Download subtitles
                ydl_opts = {
                    **YTDLConfig.SUBTITLE_DOWNLOAD_OPTS_TEMPLATE,
                    'writesubtitles': not is_auto,
                    'writeautomaticsub': is_auto,
                    'subtitleslangs': [subtitle_lang],
                    'outtmpl': output_template,
                }
                
                ydl.download([url])
                
                output_file = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}.{subtitle_lang}{DownloadConfig.SUBTITLE_EXT}")
                logger.info(f"Subtitles downloaded to: {output_file}")
                return f"{DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} {'auto-generated captions' if is_auto else 'subtitles'} downloaded successfully:\nFile: {output_file}", None
        except Exception as e:
            error_msg = f"Error downloading subtitles: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def generate_summary(title: str, description: str) -> str:
        """Generate summary of video using LLM"""
        try:
            logger.info(f"Generating summary for: {title}")
            
            prompt = f"""
            Please provide a concise summary of this YouTube video based on its title and description:
            
            Title: {title}
            Description: {description}
            
            Please structure the summary with:
            1. Main topic/theme
            2. Key points
            3. Target audience
            """
            
            return call_llm(prompt, temperature=0.7)
        except Exception as e:
            error_msg = f"Error generating summary: {str(e)}"
            logger.error(error_msg)
            return error_msg 