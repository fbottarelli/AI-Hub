import gradio as gr
import logging
from typing import List, Dict
from ..lib.common import call_llm, handle_error

logger = logging.getLogger(__name__)

# Mock data for demonstration
MOCK_TWEETS = [
    {"id": "1", "text": "Just launched a new AI project! #AI #Tech", "likes": 42, "retweets": 12},
    {"id": "2", "text": "The future of coding is here. Check out our latest developments in ML", "likes": 89, "retweets": 34},
    {"id": "3", "text": "Excited to announce our partnership with @OpenAI! 🚀", "likes": 156, "retweets": 67}
]

def analyze_sentiment(tweet_text: str) -> str:
    """Analyze sentiment of a tweet using LLM"""
    prompt = f"""
    Analyze the sentiment of this tweet and explain why:
    
    Tweet: {tweet_text}
    
    Please provide:
    1. Overall sentiment (Positive/Negative/Neutral)
    2. Brief explanation
    3. Key emotional triggers
    """
    return call_llm(prompt, temperature=0.3)

def generate_thread(topic: str, num_tweets: int = 3) -> str:
    """Generate a Twitter thread on a topic"""
    prompt = f"""
    Create a compelling Twitter thread about: {topic}
    
    Rules:
    1. Create {num_tweets} tweets
    2. Each tweet should be under 280 characters
    3. Make it engaging and informative
    4. Use appropriate hashtags
    5. Number each tweet
    
    Format each tweet as: "Tweet 1: [content]"
    """
    return call_llm(prompt, temperature=0.7)

def suggest_hashtags(content: str) -> str:
    """Suggest relevant hashtags for content"""
    prompt = f"""
    Suggest 5-7 relevant hashtags for this content:
    
    Content: {content}
    
    Rules:
    1. Mix of popular and specific hashtags
    2. Keep them relevant to the topic
    3. Include 1-2 trending hashtags if applicable
    4. Format as space-separated hashtags
    """
    return call_llm(prompt, temperature=0.5)

def search_tweets(query: str) -> List[Dict]:
    """Mock function to search tweets"""
    # In a real app, this would call Twitter's API
    return [tweet for tweet in MOCK_TWEETS if query.lower() in tweet["text"].lower()]

def create_twitter_tab():
    """Create the Twitter/X utility interface"""
    with gr.Blocks() as twitter_interface:
        gr.Markdown("""
        # 🐦 Twitter/X Utility Hub
        
        Analyze, generate, and optimize your Twitter content:
        - Analyze tweet sentiment
        - Generate tweet threads
        - Get hashtag suggestions
        - Search tweets (demo mode)
        """)
        
        with gr.Tab("Sentiment Analysis"):
            tweet_input = gr.Textbox(
                label="Enter tweet text",
                placeholder="Enter the tweet you want to analyze...",
                lines=3
            )
            analyze_button = gr.Button("Analyze Sentiment")
            sentiment_output = gr.Textbox(
                label="Sentiment Analysis",
                lines=5
            )
            
            analyze_button.click(
                analyze_sentiment,
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
                lines=8
            )
            
            generate_button.click(
                generate_thread,
                inputs=[topic_input, num_tweets],
                outputs=[thread_output]
            )
            
        with gr.Tab("Hashtag Suggestions"):
            content_input = gr.Textbox(
                label="Content",
                placeholder="Enter your tweet content to get hashtag suggestions...",
                lines=3
            )
            suggest_button = gr.Button("Suggest Hashtags")
            hashtags_output = gr.Textbox(
                label="Suggested Hashtags",
                lines=2
            )
            
            suggest_button.click(
                suggest_hashtags,
                inputs=[content_input],
                outputs=[hashtags_output]
            )
            
        with gr.Tab("Search Tweets (Demo)"):
            search_input = gr.Textbox(
                label="Search Query",
                placeholder="Enter search terms..."
            )
            search_button = gr.Button("Search")
            
            def format_search_results(tweets):
                if not tweets:
                    return "No tweets found."
                return "\n\n".join([
                    f"Tweet {i+1}:\n{t['text']}\n❤️ {t['likes']} | 🔄 {t['retweets']}"
                    for i, t in enumerate(tweets)
                ])
            
            search_results = gr.Textbox(
                label="Search Results",
                lines=10
            )
            
            search_button.click(
                lambda q: format_search_results(search_tweets(q)),
                inputs=[search_input],
                outputs=[search_results]
            )
            
    return twitter_interface 