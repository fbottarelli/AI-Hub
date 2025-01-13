import gradio as gr
import logging
from ...backend.services.twitter_service import TwitterService
from ...backend.utils.formatters import format_tweet_results
from ...frontend.config.ui_settings import UIConfig

logger = logging.getLogger(__name__)

def create_twitter_tab():
    """Create the Twitter/X utility interface"""
    twitter_service = TwitterService()
    
    with gr.Blocks() as twitter_interface:
        gr.Markdown(UIConfig.TWITTER_TAB_DESCRIPTION)
        
        with gr.Tab("Sentiment Analysis"):
            tweet_input = gr.Textbox(
                label="Enter tweet text",
                placeholder="Enter the tweet you want to analyze...",
                lines=UIConfig.TWEET_INPUT_LINES
            )
            analyze_button = gr.Button("Analyze Sentiment")
            sentiment_output = gr.Textbox(
                label="Sentiment Analysis",
                lines=5
            )
            
            analyze_button.click(
                twitter_service.analyze_sentiment,
                inputs=[tweet_input],
                outputs=[sentiment_output]
            )
            
        with gr.Tab("Thread Generator"):
            with gr.Row():
                topic_input = gr.Textbox(
                    label="Topic",
                    placeholder="Enter the topic for your thread..."
                )
                num_tweets = gr.Slider(
                    minimum=2,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Number of tweets"
                )
            
            generate_button = gr.Button("Generate Thread")
            thread_output = gr.Textbox(
                label="Generated Thread",
                lines=UIConfig.THREAD_OUTPUT_LINES
            )
            
            generate_button.click(
                twitter_service.generate_thread,
                inputs=[topic_input, num_tweets],
                outputs=[thread_output]
            )
            
        with gr.Tab("Hashtag Suggestions"):
            content_input = gr.Textbox(
                label="Content",
                placeholder="Enter your tweet content to get hashtag suggestions...",
                lines=UIConfig.TWEET_INPUT_LINES
            )
            suggest_button = gr.Button("Suggest Hashtags")
            hashtags_output = gr.Textbox(
                label="Suggested Hashtags",
                lines=UIConfig.HASHTAG_OUTPUT_LINES
            )
            
            suggest_button.click(
                twitter_service.suggest_hashtags,
                inputs=[content_input],
                outputs=[hashtags_output]
            )
            
        with gr.Tab("Search Tweets (Demo)"):
            search_input = gr.Textbox(
                label="Search Query",
                placeholder="Enter search terms..."
            )
            search_button = gr.Button("Search")
            search_results = gr.Textbox(
                label="Search Results",
                lines=UIConfig.SEARCH_RESULTS_LINES
            )
            
            def handle_search(query):
                tweets = twitter_service.search_tweets(query)
                return format_tweet_results(tweets)
            
            search_button.click(
                handle_search,
                inputs=[search_input],
                outputs=[search_results]
            )
            
    return twitter_interface 