class UIConfig:
    # App title and description
    APP_TITLE = "🚀 Personal Multi-Utility Hub"
    
    # Layout settings
    FILL_HEIGHT = True  # Make app take full height
    FILL_WIDTH = True   # Make app take full width
    SCALE_FULL = 4     # For full-width elements
    SCALE_HALF = 2     # For half-width elements
    
    # Sidebar settings
    SIDEBAR_POSITION = "left"  # or "right"
    SIDEBAR_WIDTH = "300px"
    SIDEBAR_COLLAPSED = False  # Initial state
    
    # Theme settings
    THEME = "soft"  # gradio theme
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#FFC107"
    
    # Tab settings
    TABS = [
        {"name": "🎥 YouTube", "id": "youtube"},
        {"name": "🐦 Twitter/X", "id": "twitter"},
        {"name": "📊 Analytics", "id": "analytics"},
        {"name": "⚙️ Settings", "id": "settings"}
    ]
    
    # YouTube tab settings
    YT_TAB_TITLE = "🎥 YouTube Utility Hub"
    YT_TAB_DESCRIPTION = """
    # 🎥 YouTube Utility Hub
    
    Enter a YouTube URL to:
    - Download video (MP4)
    - Extract audio (MP3)
    - Download subtitles (English or Italian)
    - Generate AI summary
    
    All files will be saved in the `downloads` folder.
    """
    
    # Twitter tab settings
    TWITTER_TAB_TITLE = "🐦 Twitter/X Utility Hub"
    TWITTER_TAB_DESCRIPTION = """
    # 🐦 Twitter/X Utility Hub
    
    Analyze, generate, and optimize your Twitter content:
    - Analyze tweet sentiment
    - Generate tweet threads
    - Get hashtag suggestions
    - Search tweets (demo mode)
    """
    
    # Download formats
    FORMATS = ["Video (MP4)", "Audio (MP3)", "Subtitles"]
    DEFAULT_FORMAT = "Video (MP4)"
    
    # UI Components settings
    URL_PLACEHOLDER = "Enter YouTube video URL..."
    TWEET_PLACEHOLDER = "Enter your tweet here..."
    THREAD_TOPIC_PLACEHOLDER = "Enter the topic for your thread..."
    HASHTAG_PLACEHOLDER = "Enter your content to get hashtag suggestions..."
    SEARCH_PLACEHOLDER = "Search tweets..."
    
    # Text input/output sizes
    STATUS_LINES = 3
    SUMMARY_LINES = 10
    TWEET_INPUT_LINES = 3
    THREAD_OUTPUT_LINES = 8
    HASHTAG_OUTPUT_LINES = 2
    SEARCH_RESULTS_LINES = 10
    SENTIMENT_OUTPUT_LINES = 5
    
    # Button labels
    DOWNLOAD_BUTTON = "Download"
    SUMMARIZE_BUTTON = "Generate Summary"
    ANALYZE_BUTTON = "Analyze Sentiment"
    GENERATE_BUTTON = "Generate Thread"
    SUGGEST_BUTTON = "Suggest Hashtags"
    SEARCH_BUTTON = "Search"
    
    # Thread generator settings
    MIN_TWEETS = 2
    MAX_TWEETS = 5
    DEFAULT_TWEETS = 3
    TWEET_STEP = 1
    
    # Labels
    URL_LABEL = "YouTube URL"
    FORMAT_LABEL = "Select Format"
    LANG_LABEL = "Subtitle Language"
    STATUS_LABEL = "Status"
    ERROR_LABEL = "Error"
    SUMMARY_LABEL = "Video Summary"
    TWEET_LABEL = "Tweet Text"
    SENTIMENT_LABEL = "Sentiment Analysis"
    TOPIC_LABEL = "Topic"
    TWEETS_NUM_LABEL = "Number of Tweets"
    THREAD_LABEL = "Generated Thread"
    CONTENT_LABEL = "Content"
    HASHTAGS_LABEL = "Suggested Hashtags"
    SEARCH_LABEL = "Search Query"
    RESULTS_LABEL = "Search Results"
    
    # Messages
    VIDEO_FOUND = "✅ Video found:"
    VIDEO_ERROR = "❌ Error:"
    NO_RESULTS = "No results found."
    LOADING_MSG = "Processing..."
