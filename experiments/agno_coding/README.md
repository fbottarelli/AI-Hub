# 🐍 Agno Coding Agent

A powerful Python coding assistant built with the Agno framework. This agent can generate, execute, debug, and explain Python code with advanced reasoning capabilities.

## Features

- **Multi-Model Support**: Works with OpenAI GPT, Anthropic Claude, or Google Gemini models
- **Code Generation**: Creates Python code based on natural language descriptions
- **Code Execution**: Runs Python code safely and provides output/error feedback
- **Error Debugging**: Automatically detects and fixes code errors
- **Package Management**: Installs required Python packages automatically
- **Code Persistence**: Saves important code to files
- **Memory & Context**: Remembers previous conversations for better context
- **Advanced Reasoning**: Uses reasoning tools for complex problem-solving
- **Interactive & Batch Modes**: Supports both interactive sessions and batch processing

## Prerequisites

- Python 3.9+
- UV package manager (recommended)
- At least one API key from:
  - OpenAI API key
  - Anthropic API key
  - Google Gemini API key

## Setup

1. **Navigate to the project directory**:
   ```bash
   cd experiments/agno_coding
   ```

2. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root with your API keys:
   ```env
   # OpenAI API Key (for GPT models)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Anthropic API Key (for Claude models)
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Google Gemini API Key
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. **Get API Keys**:
   - **OpenAI**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic**: Get your API key from [Anthropic Console](https://console.anthropic.com/)
   - **Google Gemini**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Interactive Mode

Run the coding agent in interactive mode:

```bash
uv run main.py
```

The agent will:
1. Let you choose a model provider (OpenAI, Anthropic, or Gemini)
2. Start an interactive session where you can ask coding questions
3. Execute and debug code in real-time
4. Remember context from previous interactions

### Example Tasks

Try these example tasks with the agent:

```
- "Create a function to calculate fibonacci numbers"
- "Write a script to analyze CSV data with pandas"
- "Help me debug this code: [paste your code]"
- "Create a simple web scraper using requests"
- "Generate sample data and create a matplotlib visualization"
- "Write a class for a basic calculator"
- "Create a script to process JSON files"
- "Build a simple REST API with Flask"
```

### Batch Mode

For processing multiple tasks at once:

```python
from main import batch_coding_tasks

tasks = [
    "Create a function to sort a list",
    "Write a script to count word frequencies",
    "Generate a simple data visualization"
]

batch_coding_tasks(tasks, model_provider="openai")
```

### Single Task Mode

For one-off coding tasks:

```python
from main import create_coding_agent

agent = create_coding_agent(model_provider="openai")
response = agent.run("Create a function to reverse a string")
print(response.content)
```

## How It Works

### Agent Architecture

The Agno Coding Agent consists of:

1. **Core Agent**: Built on Agno framework with chosen LLM
2. **Custom Tools**:
   - `python_repl`: Executes Python code safely
   - `save_code_to_file`: Saves code to files
   - `install_package`: Installs Python packages
   - `ReasoningTools`: Provides advanced reasoning capabilities

3. **Memory System**: Stores conversation history and context
4. **Error Handling**: Automatically catches and debugs errors

### Process Flow

```
User Query → Reasoning → Code Generation → Execution → Debugging → Response
```

1. **User Input**: Natural language description of coding task
2. **Reasoning**: Agent analyzes the problem and plans solution
3. **Code Generation**: Creates Python code based on requirements
4. **Execution**: Runs code using safe Python REPL
5. **Error Handling**: Debugs and fixes errors if they occur
6. **Response**: Provides working code with explanations

## Advanced Features

### Memory & Context

The agent maintains conversation history and can:
- Reference previous code snippets
- Build upon earlier solutions
- Maintain context across sessions

### Reasoning Capabilities

Uses Agno's ReasoningTools for:
- Problem decomposition
- Step-by-step solution planning
- Error analysis and debugging
- Code optimization suggestions

### Multi-Model Support

Choose the best model for your needs:
- **OpenAI GPT-4o-mini**: Fast, reliable, good for most tasks
- **Anthropic Claude**: Excellent reasoning, careful code generation
- **Google Gemini**: Good performance, cost-effective

## Configuration

### Model Settings

Customize model behavior by modifying the agent creation:

```python
agent = Agent(
    model=OpenAIChat(
        id="gpt-4o-mini",
        temperature=0.1,  # Lower for more deterministic code
        max_tokens=2048
    ),
    # ... other settings
)
```

### Tool Configuration

Add or modify tools:

```python
@tool
def custom_tool(param: str) -> str:
    """Your custom tool description"""
    # Implementation
    return result

# Add to agent tools list
```

## Safety & Security

- Code execution is sandboxed using subprocess
- 30-second timeout for code execution
- Package installation requires explicit permission
- No access to sensitive system resources

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are correctly set in `.env`
2. **Import Errors**: Install missing packages using `uv sync`
3. **Code Execution Timeout**: Optimize code or increase timeout limit
4. **Memory Issues**: Restart agent to clear memory

### Debug Mode

Enable debug mode for detailed logging:

```python
agent = create_coding_agent(debug_mode=True)
```

## Examples

### Basic Function Creation

```
User: "Create a function to calculate the area of a circle"

Agent: I'll create a function to calculate the area of a circle using the formula A = π × r².

[Code execution and testing]

Final working function with explanations and test cases.
```

### Data Analysis

```
User: "Analyze a CSV file and show basic statistics"

Agent: I'll create a script to read CSV data and provide statistical analysis.

[Installs pandas if needed, generates code, tests execution]

Complete analysis script with visualizations.
```

### Error Debugging

```
User: "This code has an error: [buggy code]"

Agent: I'll analyze the error and provide a corrected version.

[Identifies issue, explains problem, provides fix]

Corrected code with explanation of the fix.
```

## Contributing

Feel free to contribute by:
- Adding new tools and capabilities
- Improving error handling
- Extending model support
- Adding more examples

## License

This project is part of the AI-Hub repository and follows the same license terms. 