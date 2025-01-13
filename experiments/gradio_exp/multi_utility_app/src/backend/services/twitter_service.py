import logging
from typing import List, Dict
import json
import os
from ..utils.llm import call_llm

logger = logging.getLogger(__name__)

# Mock data for demonstration
MOCK_TWEETS = [
    {"id": "1", "text": "Just launched a new AI project! #AI #Tech", "likes": 42, "retweets": 12},
    {"id": "2", "text": "The future of coding is here. Check out our latest developments in ML", "likes": 89, "retweets": 34},
    {"id": "3", "text": "Excited to announce our partnership with @OpenAI! 🚀", "likes": 156, "retweets": 67}
]

class TwitterService:
    @staticmethod
    def analyze_sentiment(tweet_text: str) -> str:
        """Analyze sentiment of a tweet using LLM"""
        try:
            prompt = f"""
            Analyze the sentiment of this tweet and explain why:
            
            Tweet: {tweet_text}
            
            Please provide:
            1. Overall sentiment (Positive/Negative/Neutral)
            2. Brief explanation
            3. Key emotional triggers
            """
            return call_llm(prompt, temperature=0.3)
        except Exception as e:
            error_msg = f"Error analyzing sentiment: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def generate_thread(topic: str, num_tweets: int = 3) -> str:
        """Generate a Twitter thread on a topic"""
        try:
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
        except Exception as e:
            error_msg = f"Error generating thread: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def suggest_hashtags(content: str) -> str:
        """Suggest relevant hashtags for content"""
        try:
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
        except Exception as e:
            error_msg = f"Error suggesting hashtags: {str(e)}"
            logger.error(error_msg)
            return error_msg

    @staticmethod
    def search_tweets(query: str) -> List[Dict]:
        """Mock function to search tweets"""
        try:
            # In a real app, this would call Twitter's API
            return [tweet for tweet in MOCK_TWEETS if query.lower() in tweet["text"].lower()]
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            return [] 

    @staticmethod
    def process_tweet_json(input_json: List[Dict], output_path: str) -> str:
        """Process tweet JSON data and create a filtered version with selected fields.
        
        Args:
            input_json: List of tweet dictionaries
            output_path: Path to save the filtered JSON
            
        Returns:
            str: Status message indicating success or failure
        """
        try:
            filtered_tweets = []
            for tweet in input_json:
                filtered_tweet = {
                    "id": tweet.get("id"),
                    "text": tweet.get("full_text") or tweet.get("text"),
                    "url": tweet.get("url"),
                    "media": tweet.get("media", [])
                }
                filtered_tweets.append(filtered_tweet)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save filtered JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_tweets, f, ensure_ascii=False, indent=2)
            
            return f"Successfully processed {len(filtered_tweets)} tweets and saved to {output_path}"
        except Exception as e:
            error_msg = f"Error processing tweet JSON: {str(e)}"
            logger.error(error_msg)
            return error_msg 