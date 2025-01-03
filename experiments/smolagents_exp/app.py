from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, LiteLLMModel
import os
import dotenv

dotenv.load_dotenv()


model = LiteLLMModel(model_id="deepseek/deepseek-chat")

agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

agent.run("How many agent frameworks are used now?")
