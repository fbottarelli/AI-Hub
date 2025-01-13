import logging
from typing import Tuple, Optional
from gitingest import ingest
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class GitHubService:
    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if the URL is a valid GitHub repository URL"""
        github_pattern = r'^https?://(?:www\.)?github\.com/[\w-]+/[\w.-]+/?.*$'
        return bool(re.match(github_pattern, url))

    @staticmethod
    def extract_repo_name(url: str) -> str:
        """Extract repository name from GitHub URL"""
        # Remove trailing slashes and .git extension
        clean_url = url.rstrip('/').rstrip('.git')
        
        # Handle different URL formats (including tree/branch paths)
        parts = clean_url.split('/')
        
        # Find the repo name (it comes after the username)
        try:
            github_index = parts.index('github.com')
            if len(parts) > github_index + 2:
                repo_name = parts[github_index + 2]
                return repo_name
        except ValueError:
            pass
            
        # Fallback to a default name if we can't parse the URL
        return "repository"

    @staticmethod
    def generate_markdown(summary: str, tree: str, content: str, repo_url: str) -> str:
        """Generate a markdown file from the analysis results"""
        repo_name = GitHubService.extract_repo_name(repo_url)
        markdown = f"""# Repository Analysis: {repo_name}

## Repository URL
{repo_url}

## Summary
{summary}

## Directory Structure
```
{tree}
```

## Content Digest
{content}
"""
        return markdown

    @staticmethod
    def save_markdown(markdown: str, repo_url: str) -> str:
        """Save the markdown content to a file"""
        try:
            # Extract repo name from URL
            repo_name = GitHubService.extract_repo_name(repo_url)
            # Create filename
            filename = f"{repo_name}_analysis.md"
            
            # Save to downloads directory
            output_path = Path("downloads") / filename
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving markdown: {str(e)}")
            return ""

    @staticmethod
    def analyze_repository(url: str, output_format: str = "all") -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Analyze a GitHub repository using gitingest
        
        Args:
            url: GitHub repository URL
            output_format: What information to include in the output
            
        Returns:
            Tuple of (summary, tree, content, markdown_path)
        """
        try:
            # Check if it's a GitHub URL
            is_github = GitHubService.is_github_url(url)
            if not is_github:
                return (
                    "Please enter a valid GitHub repository URL",
                    None,
                    None,
                    None
                )

            logger.info(f"Analyzing repository: {url}")
            
            # Use gitingest to analyze the repository
            summary, tree, content = ingest(url)
            
            # Generate markdown content
            markdown = GitHubService.generate_markdown(summary, tree, content, url)
            markdown_path = GitHubService.save_markdown(markdown, url)
            
            # Return based on requested format
            if output_format == "summary":
                return summary, None, None, markdown_path
            elif output_format == "tree":
                return None, tree, None, markdown_path
            elif output_format == "content":
                return None, None, content, markdown_path
            else:  # "all"
                return summary, tree, content, markdown_path
                
        except Exception as e:
            error_msg = f"Error analyzing repository: {str(e)}"
            logger.error(error_msg)
            return error_msg, error_msg, error_msg, None 

    @staticmethod
    def format_clipboard_content(summary: str, tree: str, content: str) -> str:
        """Format the content for clipboard copying"""
        sections = []
        
        if summary:
            sections.extend(["Summary:", summary])
        
        if tree:
            sections.extend(["\nDirectory Structure:", tree])
        
        if content:
            sections.extend(["\nContent Analysis:", content])
        
        return "\n".join(sections) 

    @staticmethod
    def get_raw_content(url: str) -> str:
        """Get raw content of the repository"""
        try:
            logger.info(f"Getting raw content for repository: {url}")
            
            # Check if it's a GitHub URL
            is_github = GitHubService.is_github_url(url)
            if not is_github:
                return "Please enter a valid GitHub repository URL"

            # Use gitingest to get repository content
            _, _, content = ingest(url)
            
            # Return the raw content
            return content
        except Exception as e:
            error_msg = f"Error getting repository content: {str(e)}"
            logger.error(error_msg)
            return error_msg 