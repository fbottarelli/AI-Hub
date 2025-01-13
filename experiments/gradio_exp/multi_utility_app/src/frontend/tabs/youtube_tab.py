import gradio as gr
import logging
from ...backend.services.youtube_service import YouTubeService
from ...backend.utils.formatters import format_duration
from ...backend.utils.file_utils import sanitize_filename
from ...frontend.config.ui_settings import UIConfig
from ...backend.config.settings import DownloadConfig

logger = logging.getLogger(__name__)

def create_youtube_tab():
    """Create the YouTube utility interface"""
    youtube_service = YouTubeService()
    
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
                info, error = youtube_service.validate_url(url)
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
                    choices=list(DownloadConfig.SUPPORTED_LANGS.values()),
                    value=DownloadConfig.SUPPORTED_LANGS[DownloadConfig.DEFAULT_LANG],
                    label="Subtitle Language"
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
            
            def handle_download(url, format_type, subtitle_lang=None):
                info, error = youtube_service.validate_url(url)
                if error:
                    return None, error
                
                title = info['title']
                sanitized_title = sanitize_filename(title)
                
                if format_type == "Video (MP4)":
                    return youtube_service.download_video(url, sanitized_title, info)
                elif format_type == "Audio (MP3)":
                    return youtube_service.download_audio(url, sanitized_title, info)
                elif format_type == "Subtitles":
                    return youtube_service.download_subtitles(url, sanitized_title, info, subtitle_lang)
            
            download_button.click(
                handle_download,
                inputs=[url_input, format_choice, subtitle_lang],
                outputs=[output_message, error_message]
            )
            
        with gr.Tab("Summarize"):
            summarize_button = gr.Button("Generate Summary")
            summary_output = gr.Textbox(
                label="Video Summary",
                lines=UIConfig.SUMMARY_LINES
            )
            
            def handle_summary(url):
                info, error = youtube_service.validate_url(url)
                if error:
                    return error
                return youtube_service.generate_summary(
                    info['title'],
                    info.get('description', 'No description available')
                )
            
            summarize_button.click(
                handle_summary,
                inputs=[url_input],
                outputs=[summary_output]
            )
            
    return youtube_interface 