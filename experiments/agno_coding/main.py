#!/usr/bin/env python3
"""
Agno Coding Agent - A Python coding assistant using the Agno framework
Similar to LangGraph coding agent but leveraging Agno's capabilities
"""

import os
import sys
import subprocess
import traceback
from typing import List, Optional
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.gemini import Gemini
from agno.tools.reasoning import ReasoningTools
from agno.memory import AgentMemory
from agno.storage.sqlalchemy import SqlAlchemyStorage
from agno.tools import tool

# Load environment variables
load_dotenv()

@tool
def python_repl(code: str) -> str:
    """
    Execute Python code and return the results.
    Use this function to run Python code and get the output.
    """
    try:
        print(f"🐍 Executing Python code:\n{code}")
        print("-" * 40)
        
        # Create a temporary file to execute the code
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Execute the code and capture output
        result = subprocess.run([
            sys.executable, temp_file
        ], capture_output=True, text=True, timeout=30)
        
        # Clean up temp file
        os.unlink(temp_file)
        
        # Format output
        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Exit code: {result.returncode}\n"
        
        print(f"📊 Result: {output}")
        return output if output else "Code executed successfully with no output"
        
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (30 seconds limit)"
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def save_code_to_file(filename: str, code: str) -> str:
    """
    Save code to a file.
    Args:
        filename: The name of the file to save to
        code: The code content to save
    """
    try:
        with open(filename, 'w') as f:
            f.write(code)
        return f"Code saved to {filename} successfully"
    except Exception as e:
        return f"Error saving code to file: {str(e)}"

@tool
def install_package(package_name: str) -> str:
    """
    Install a Python package using pip.
    Args:
        package_name: The name of the package to install
    """
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return f"Successfully installed {package_name}"
        else:
            return f"Failed to install {package_name}: {result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Installation of {package_name} timed out"
    except Exception as e:
        return f"Error installing {package_name}: {str(e)}"

def create_coding_agent(model_provider: str = "openai", use_memory: bool = True) -> Agent:
    """
    Create a coding agent with the specified model provider
    
    Args:
        model_provider: The model provider to use ('openai', 'anthropic', 'gemini')
        use_memory: Whether to use memory for the agent
    """
    
    # Initialize storage for memory (optional)
    storage = None
    memory = None
    if use_memory:
        storage = SqlAlchemyStorage(
            db_url="sqlite:///agno_coding_agent.db",
            table_name="coding_sessions"
        )
        memory = AgentMemory(
            storage=storage,
            create_user_memories=True,
            create_session_summary=True
        )
    
    # Choose model based on provider
    if model_provider == "openai":
        model = OpenAIChat(
            id="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
            max_tokens=2048
        )
    elif model_provider == "anthropic":
        model = Claude(
            id="claude-3-sonnet-20240229",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.1,
            max_tokens=2048
        )
    elif model_provider == "gemini":
        model = Gemini(
            id="gemini-1.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
            max_tokens=2048
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")
    
    # Create the coding agent
    coding_agent = Agent(
        model=model,
        tools=[
            python_repl,
            save_code_to_file,
            install_package,
            ReasoningTools(
                add_instructions=True,
                max_iterations=5
            )
        ],
        instructions=[
            "You are an expert Python coding assistant with reasoning capabilities.",
            "Your primary job is to help users write, debug, and execute Python code.",
            "When users ask coding questions or request solutions:",
            "1. First use your reasoning tools to understand the problem",
            "2. Break down complex problems into smaller, manageable steps",
            "3. Write clean, well-documented Python code",
            "4. Test your code using the python_repl tool",
            "5. If there are errors, debug and fix them iteratively",
            "6. Provide explanations for your code and approach",
            "7. Use best practices and follow PEP 8 style guidelines",
            "8. Install required packages if needed using install_package",
            "9. Save important code to files when requested",
            "Always test your code before presenting the final solution.",
            "If code fails, analyze the error and provide a corrected version.",
            "Explain your reasoning process and code decisions clearly.",
            "Use markdown formatting for better readability in your responses."
        ],
        memory=memory,
        markdown=True,
        show_tool_calls=True,
        debug_mode=False
    )
    
    return coding_agent

def interactive_coding_session(model_provider: str = "openai"):
    """
    Run an interactive coding session with the agent
    """
    
    print("🚀 Agno Coding Agent - Interactive Python Assistant")
    print("=" * 60)
    print("Features:")
    print("• Python code generation and execution")
    print("• Error debugging and fixing")
    print("• Package installation")
    print("• Code saving to files")
    print("• Memory of previous conversations")
    print("• Advanced reasoning capabilities")
    print("=" * 60)
    print(f"Using model provider: {model_provider}")
    print("=" * 60)
    
    # Create the coding agent
    try:
        agent = create_coding_agent(model_provider=model_provider)
        print("✅ Agent created successfully!")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return
    
    # Interactive loop
    print("\n💡 Example tasks you can try:")
    print("- 'Create a function to calculate fibonacci numbers'")
    print("- 'Write a script to analyze CSV data'")
    print("- 'Help me debug this code: [paste your code]'")
    print("- 'Create a simple web scraper'")
    print("- 'Generate sample data and visualize it'")
    print()
    
    while True:
        try:
            user_query = input("\n📝 Enter your coding task (or 'quit' to exit): ")
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Happy coding! Goodbye!")
                break
                
            if not user_query.strip():
                print("Please enter a valid coding task.")
                continue
                
            print(f"\n🔍 Processing task: {user_query}")
            print("-" * 40)
            
            # Get response from agent
            response = agent.run(user_query)
            
            print(f"\n🤖 Agent Response:")
            print(response.content)
            
        except KeyboardInterrupt:
            print("\n👋 Happy coding! Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again or restart the agent.")

def batch_coding_tasks(tasks: List[str], model_provider: str = "openai"):
    """
    Run multiple coding tasks in batch mode
    """
    
    print("📋 Batch Coding Tasks")
    print("=" * 40)
    
    agent = create_coding_agent(model_provider=model_provider, use_memory=False)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n🔧 Task {i}/{len(tasks)}: {task}")
        print("-" * 60)
        
        try:
            response = agent.run(task)
            print(f"✅ Result:\n{response.content}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("=" * 60)

def main():
    """Main function to choose between different modes"""
    
    print("🔍 Agno Coding Agent")
    print("=" * 40)
    
    # Check for API keys
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GOOGLE_API_KEY")
    }
    
    available_providers = [k for k, v in api_keys.items() if v]
    
    if not available_providers:
        print("❌ No API keys found. Please set at least one of:")
        print("- OPENAI_API_KEY")
        print("- ANTHROPIC_API_KEY")
        print("- GOOGLE_API_KEY")
        return
    
    print("Available model providers:")
    for i, provider in enumerate(available_providers, 1):
        print(f"{i}. {provider.title()}")
    
    # Choose model provider
    try:
        choice = input(f"\nChoose model provider (1-{len(available_providers)}): ")
        provider_index = int(choice) - 1
        
        if 0 <= provider_index < len(available_providers):
            model_provider = available_providers[provider_index]
        else:
            print("Invalid choice. Using OpenAI as default.")
            model_provider = "openai"
    except ValueError:
        print("Invalid input. Using OpenAI as default.")
        model_provider = "openai"
    
    # Choose mode
    print("\nChoose mode:")
    print("1. Interactive Coding Session")
    print("2. Batch Tasks Demo")
    print("3. Single Task")
    
    mode_choice = input("\nEnter choice (1-3): ")
    
    if mode_choice == "1":
        interactive_coding_session(model_provider)
    elif mode_choice == "2":
        demo_tasks = [
            "Create a function to calculate the factorial of a number",
            "Write a script to read a CSV file and show basic statistics",
            "Generate a simple plot with matplotlib"
        ]
        batch_coding_tasks(demo_tasks, model_provider)
    elif mode_choice == "3":
        task = input("Enter your coding task: ")
        agent = create_coding_agent(model_provider=model_provider, use_memory=False)
        response = agent.run(task)
        print(f"\n🤖 Agent Response:\n{response.content}")
    else:
        print("Invalid choice. Starting interactive session...")
        interactive_coding_session(model_provider)

if __name__ == "__main__":
    main() 