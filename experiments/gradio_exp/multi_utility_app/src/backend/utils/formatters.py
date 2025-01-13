def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS format"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def format_tweet_results(tweets: list) -> str:
    """Format tweet search results for display"""
    if not tweets:
        return "No tweets found."
    return "\n\n".join([
        f"Tweet {i+1}:\n{t['text']}\n❤️ {t['likes']} | 🔄 {t['retweets']}"
        for i, t in enumerate(tweets)
    ]) 