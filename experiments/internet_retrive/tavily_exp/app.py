from tavily import TavilyClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_with_tavily(query: str):
    # Initialize Tavily client with API key from environment variables
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    try:
        # Perform the search
        # Using basic search depth (costs 1 credit)
        response = tavily_client.search(
            query=query,
            search_depth="basic"
        )
        return response
    except Exception as e:
        print(f"Error performing search: {e}")
        return None

def main():
    # Example usage
    query = "What is Tavily Search API?"
    results = search_with_tavily(query)
    
    if results:
        print("Search Results:")
        print(results)

if __name__ == "__main__":
    main()
