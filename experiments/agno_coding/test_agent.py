#!/usr/bin/env python3
"""
Test script for the Agno Coding Agent
Quick verification that the agent works as expected
"""

import os
import sys
from dotenv import load_dotenv
from main import create_coding_agent

# Load environment variables
load_dotenv()

def test_agent_creation():
    """Test that the agent can be created successfully"""
    print("🧪 Testing Agent Creation")
    print("-" * 30)
    
    # Check for available API keys
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GOOGLE_API_KEY")
    }
    
    available_providers = [k for k, v in api_keys.items() if v]
    
    if not available_providers:
        print("❌ No API keys found. Please set up your .env file.")
        return False
    
    # Test creating agent with each available provider
    for provider in available_providers:
        try:
            print(f"Testing {provider} agent...")
            agent = create_coding_agent(model_provider=provider, use_memory=False)
            print(f"✅ {provider} agent created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating {provider} agent: {e}")
    
    return False

def test_simple_task():
    """Test the agent with a simple coding task"""
    print("\n🧪 Testing Simple Task")
    print("-" * 30)
    
    # Use the first available provider
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GOOGLE_API_KEY")
    }
    
    available_providers = [k for k, v in api_keys.items() if v]
    
    if not available_providers:
        print("❌ No API keys available for testing")
        return False
    
    provider = available_providers[0]
    
    try:
        agent = create_coding_agent(model_provider=provider, use_memory=False)
        
        # Simple test task
        task = "Create a function that adds two numbers and test it"
        
        print(f"Task: {task}")
        print("Processing...")
        
        response = agent.run(task)
        
        print("✅ Task completed successfully!")
        print(f"Response length: {len(response.content)} characters")
        
        # Check if the response contains expected elements
        if "def" in response.content.lower() and "+" in response.content:
            print("✅ Response contains function definition and addition")
        else:
            print("⚠️  Response might not contain expected code structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running task: {e}")
        return False

def test_tools():
    """Test that the custom tools work"""
    print("\n🧪 Testing Custom Tools")
    print("-" * 30)
    
    # Test python_repl tool
    from main import python_repl
    
    try:
        result = python_repl("print('Hello from Agno Coding Agent!')")
        print("✅ python_repl tool works")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error testing python_repl: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Agno Coding Agent - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Agent Creation", test_agent_creation),
        ("Custom Tools", test_tools),
        ("Simple Task", test_simple_task),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running test: {test_name}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("-" * 30)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The agent is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check your setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 