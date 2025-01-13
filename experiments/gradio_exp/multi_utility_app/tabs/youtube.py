import gradio as gr
import yt_dlp
import logging
from pathlib import Path

from ..config import DownloadConfig, YTDLConfig, UIConfig, SummaryConfig
from ..lib.common import call_llm, sanitize_filename, format_duration, handle_error

logger = logging.getLogger(__name__)

def validate_url(url: str):
    """Validate YouTube URL and return video info"""
    try:
        with yt_dlp.YoutubeDL(YTDLConfig.VALIDATE_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            logger.info(f"Video found: {info['title']} (Duration: {info['duration']} seconds)")
            return info, None
    except Exception as e:
        return handle_error(e, "URL validation")

def download_video(url: str, format_type: str, subtitle_lang: str = None):
    try:
        # First validate the URL
        info, error = validate_url(url)
        if error:
            return None, error

        title = info['title']
        sanitized_title = sanitize_filename(title)
        
        if format_type == "Video (MP4)":
            return handle_video_download(url, sanitized_title, info)
        elif format_type == "Audio (MP3)":
            return handle_audio_download(url, sanitized_title, info)
        elif format_type == "Subtitles":
            return handle_subtitle_download(url, sanitized_title, info, subtitle_lang)
            
    except Exception as e:
        return handle_error(e, "download")

def handle_video_download(url: str, sanitized_title: str, info: dict):
    """Handle video download in MP4 format"""
    logger.info(f"Attempting to download video: {info['title']}")
    output_template = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}%(ext)s")
    
    ydl_opts = {
        **YTDLConfig.VIDEO_OPTS_TEMPLATE,
        'outtmpl': output_template,
        'progress_hooks': [lambda d: logger.info(f"Download progress: {d.get('status', 'unknown')}")],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info("Starting video download")
        ydl.download([url])
        
    output_file = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}{DownloadConfig.VIDEO_EXT}")
    logger.info(f"Video downloaded to: {output_file}")
    return f"Video downloaded successfully:\nFile: {output_file}", None

def handle_audio_download(url: str, sanitized_title: str, info: dict):
    """Handle audio download in MP3 format"""
    logger.info(f"Attempting to download audio for: {info['title']}")
    output_template = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}%(ext)s")
    
    ydl_opts = {
        **YTDLConfig.AUDIO_OPTS_TEMPLATE,
        'outtmpl': output_template,
        'progress_hooks': [lambda d: logger.info(f"Download progress: {d.get('status', 'unknown')}")],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logger.info("Starting audio download")
        ydl.download([url])
        
    output_file = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}{DownloadConfig.AUDIO_EXT}")
    logger.info(f"Audio downloaded to: {output_file}")
    return f"Audio downloaded successfully:\nQuality: {DownloadConfig.AUDIO_QUALITY}kbps\nFile: {output_file}", None

def handle_subtitle_download(url: str, sanitized_title: str, info: dict, subtitle_lang: str = None):
    """Handle subtitle download"""
    if not subtitle_lang or subtitle_lang not in DownloadConfig.SUPPORTED_LANGS:
        subtitle_lang = DownloadConfig.DEFAULT_LANG
        
    logger.info(f"Attempting to fetch {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles for: {info['title']}")
    output_template = str(DownloadConfig.DOWNLOAD_DIR / f"{sanitized_title}%(ext)s")
    
    # First, check both manual and auto-generated subtitles
    with yt_dlp.YoutubeDL(YTDLConfig.SUBTITLE_CHECK_OPTS) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Check both manual and auto-generated subtitles for the selected language
        has_manual = subtitle_lang in info.get('subtitles', {})
        has_auto = subtitle_lang in info.get('automatic_captions', {})
        
        if not has_manual and not has_auto:
            msg = f"No {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles or captions available"
            logger.warning(msg)
            return None, msg
        
        # Prefer manual subtitles over auto-generated
        is_auto = not has_manual and has_auto
        logger.info(f"Found {'auto-generated' if is_auto else 'manual'} {DownloadConfig.SUPPORTED_LANGS[subtitle_lang]} subtitles")
        
        # Download the subtitles
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

def summarize_video(url: str):
    """Generate an AI summary of the video"""
    try:
        # First validate the URL
        info, error = validate_url(url)
        if error:
            return error
            
        title = info['title']
        description = info.get('description', 'No description available')
        
        logger.info(f"Generating summary for: {title}")
        
        # Create prompt for summarization
        prompt = SummaryConfig.PROMPT_TEMPLATE.format(
            title=title,
            description=description
        )
        
        # Get summary from LLM
        return call_llm(prompt, SummaryConfig.TEMPERATURE)
        
    except Exception as e:
        return handle_error(e, "summarization")[1]

def create_youtube_tab():
    """Create the YouTube utility interface"""
    with gr.Blocks() as youtube_interface:
        gr.Markdown(UIConfig.YT_TAB_DESCRIPTION)
        
        with gr.Row():
            url_input = gr.Textbox(
                label="YouTube URL",
                placeholder=UIConfig.URL_PLACEHOLDER,
                scale=4
            )
            
            # Add video info display
            video_info = gr.Markdown(visible=False)
            
            # Update video info when URL changes
            def update_video_info(url):
                if not url:
                    return gr.update(visible=False)
                info, error = validate_url(url)
                if error:
                    return gr.update(visible=True, value=f"❌ {error}")
                return gr.update(
                    visible=True,
                    value=f"✅ Video found:\n- Title: {info['title']}\n- Duration: {format_duration(info['duration'])}"
                )
            
            url_input.change(
                update_video_info,
                inputs=[url_input],
                outputs=[video_info]
            )
        
        with gr.Tab("Download"):
            with gr.Row():
                format_choice = gr.Radio(
                    choices=UIConfig.FORMATS,
                    label="Select Format",
                    value=UIConfig.DEFAULT_FORMAT
                )
                subtitle_lang = gr.Radio(
                    choices=list(DownloadConfig.SUPPORTED_LANGS.items()),
                    label="Subtitle Language",
                    value=DownloadConfig.DEFAULT_LANG,
                    visible=False,
                    type="value"
                )
            
            # Show/hide subtitle language choice based on format selection
            def update_subtitle_visibility(format):
                return gr.update(visible=format == "Subtitles")
            
            format_choice.change(
                update_subtitle_visibility,
                inputs=[format_choice],
                outputs=[subtitle_lang]
            )
            
            download_button = gr.Button("Download")
            output_message = gr.Textbox(label="Status", lines=UIConfig.STATUS_LINES)
            error_message = gr.Textbox(label="Error", visible=False)
            
            download_button.click(
                download_video,
                inputs=[url_input, format_choice, subtitle_lang],
                outputs=[output_message, error_message]
            )
            
        with gr.Tab("Summarize"):
            summarize_button = gr.Button("Generate Summary")
            summary_output = gr.Textbox(
                label="Video Summary",
                lines=UIConfig.SUMMARY_LINES
            )
            
            summarize_button.click(
                summarize_video,
                inputs=[url_input],
                outputs=[summary_output]
            )
            
    return youtube_interface 