import gradio as gr
import logging
import json
import os
from ...backend.services.twitter_service import TwitterService
from ...backend.utils.formatters import format_tweet_results
from ...frontend.config.ui_settings import UIConfig

logger = logging.getLogger(__name__)

def create_twitter_tab():
    """Create the Twitter/X utility interface"""
    twitter_service = TwitterService()
    
    with gr.Blocks() as twitter_interface:
        gr.Markdown("""
        # 🐦 Twitter/X Utilities
        Process your Twitter data and more features coming soon!
        """)
        
        with gr.Tab("Process JSON"):
            gr.Markdown("""
            ## Tweet JSON Processor
            Upload a JSON file containing tweets and create a filtered version with selected fields (id, text, url, media).
            """)
            
            with gr.Row():
                json_file = gr.File(
                    label="Upload Tweet JSON",
                    file_types=[".json"],
                    type="binary"
                )
                output_name = gr.Textbox(
                    label="Output Filename",
                    placeholder="filtered_tweets.json",
                    value="filtered_tweets.json"
                )
            
            process_button = gr.Button("Process JSON")
            status_output = gr.Textbox(
                label="Status",
                lines=2
            )
            
            def handle_json_processing(file, output_name):
                if not file:
                    return "Please upload a JSON file"
                
                try:
                    # Read and parse JSON
                    content = file.decode('utf-8')
                    tweets = json.loads(content)
                    
                    # Process JSON and save filtered version
                    output_path = os.path.join("downloads", output_name)
                    return twitter_service.process_tweet_json(tweets, output_path)
                except Exception as e:
                    error_msg = f"Error processing JSON: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            process_button.click(
                handle_json_processing,
                inputs=[json_file, output_name],
                outputs=[status_output]
            )

        with gr.Tab("Coming Soon"):
            gr.Markdown("""
            ## 🚧 More Features Coming Soon!
            
            Future features will include:
            - Sentiment Analysis
            - Thread Generation
            - Hashtag Suggestions
            - Tweet Search
            - And more!
            
            Stay tuned for updates!
            """)
            
    return twitter_interface 