#!/usr/bin/env python3
"""
Example usage of the Agno Coding Agent
Demonstrates various capabilities and use cases
"""

import os
from dotenv import load_dotenv
from main import create_coding_agent, batch_coding_tasks

# Load environment variables
load_dotenv()

def simple_example():
    """Simple example of using the coding agent"""
    print("🚀 Simple Coding Agent Example")
    print("=" * 40)
    
    # Check if API keys are available
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ Please set at least one API key in your .env file")
        return
    
    # Create agent (will use the first available API key)
    model_provider = "openai" if os.getenv("OPENAI_API_KEY") else \
                     "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "gemini"
    
    agent = create_coding_agent(model_provider=model_provider, use_memory=False)
    
    # Example task
    task = "Create a function to calculate the factorial of a number and test it with a few values"
    
    print(f"\n📝 Task: {task}")
    print("-" * 60)
    
    try:
        response = agent.run(task)
        print(f"🤖 Agent Response:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def data_analysis_example():
    """Example of data analysis with the coding agent"""
    print("\n📊 Data Analysis Example")
    print("=" * 40)
    
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ Please set at least one API key in your .env file")
        return
    
    model_provider = "openai" if os.getenv("OPENAI_API_KEY") else \
                     "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "gemini"
    
    agent = create_coding_agent(model_provider=model_provider, use_memory=False)
    
    task = """
    Create a data analysis script that:
    1. Generates sample data (100 rows with columns: name, age, salary, department)
    2. Calculates basic statistics (mean, median, standard deviation for numeric columns)
    3. Creates a simple visualization showing salary distribution by department
    4. Saves the data to a CSV file
    """
    
    print(f"\n📝 Task: {task}")
    print("-" * 60)
    
    try:
        response = agent.run(task)
        print(f"🤖 Agent Response:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def debug_example():
    """Example of debugging code with the agent"""
    print("\n🐛 Code Debugging Example")
    print("=" * 40)
    
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ Please set at least one API key in your .env file")
        return
    
    model_provider = "openai" if os.getenv("OPENAI_API_KEY") else \
                     "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "gemini"
    
    agent = create_coding_agent(model_provider=model_provider, use_memory=False)
    
    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Test the function
numbers = [1, 2, 3, 4, 5, 0]
result = calculate_average(numbers)
print(f"Average: {result}")

# This will cause an error
empty_list = []
result2 = calculate_average(empty_list)
print(f"Average of empty list: {result2}")
"""
    
    task = f"""
    Debug and fix this code that has an error:
    
    {buggy_code}
    
    The code should handle edge cases properly and not crash.
    """
    
    print(f"\n📝 Task: Debug the following code")
    print("Buggy code:")
    print(buggy_code)
    print("-" * 60)
    
    try:
        response = agent.run(task)
        print(f"🤖 Agent Response:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def batch_tasks_example():
    """Example of running multiple tasks in batch"""
    print("\n📋 Batch Tasks Example")
    print("=" * 40)
    
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ Please set at least one API key in your .env file")
        return
    
    model_provider = "openai" if os.getenv("OPENAI_API_KEY") else \
                     "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "gemini"
    
    tasks = [
        "Create a function to check if a number is prime",
        "Write a script to count word frequencies in a text",
        "Create a simple class for a bank account with deposit and withdraw methods",
        "Generate a list of random numbers and find the min, max, and average"
    ]
    
    print(f"Running {len(tasks)} tasks in batch mode...")
    batch_coding_tasks(tasks, model_provider=model_provider)

def advanced_example():
    """Advanced example showing reasoning capabilities"""
    print("\n🧠 Advanced Reasoning Example")
    print("=" * 40)
    
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        print("❌ Please set at least one API key in your .env file")
        return
    
    model_provider = "openai" if os.getenv("OPENAI_API_KEY") else \
                     "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "gemini"
    
    agent = create_coding_agent(model_provider=model_provider, use_memory=False)
    
    task = """
    Create a program that implements a simple recommendation system:
    
    1. Define a dataset of users and their movie ratings
    2. Implement a function to calculate similarity between users
    3. Create a function to recommend movies to a user based on similar users
    4. Test the system with sample data
    5. Explain how the algorithm works
    
    Use collaborative filtering approach and provide clear documentation.
    """
    
    print(f"\n📝 Task: {task}")
    print("-" * 60)
    
    try:
        response = agent.run(task)
        print(f"🤖 Agent Response:")
        print(response.content)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function to run examples"""
    print("🔍 Agno Coding Agent - Examples")
    print("=" * 50)
    
    examples = [
        ("1", "Simple Function Creation", simple_example),
        ("2", "Data Analysis", data_analysis_example),
        ("3", "Code Debugging", debug_example),
        ("4", "Batch Tasks", batch_tasks_example),
        ("5", "Advanced Reasoning", advanced_example),
        ("6", "All Examples", lambda: [ex[2]() for ex in examples[:-1]])
    ]
    
    print("Available examples:")
    for key, name, _ in examples:
        print(f"{key}. {name}")
    
    choice = input("\nChoose an example (1-6): ")
    
    # Find and run the chosen example
    for key, name, func in examples:
        if choice == key:
            print(f"\n🚀 Running: {name}")
            func()
            break
    else:
        print("Invalid choice. Running simple example...")
        simple_example()

if __name__ == "__main__":
    main() 