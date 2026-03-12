from strands import Agent, tool 
from strands_tools import calculator
from strands.models import BedrockModel

import argparse
import json

import time

@tool 
def get_weather(location: str) -> str:
    # This is a mock implementation. In a real implementation, you would call a weather API.
    return f"The current weather in {location} is sunny with a temperature of 25°C."

model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

model = BedrockModel(model_id=model_id)

agent = Agent(model=model, 
              tools=[calculator, get_weather])

def invoke_agent(payload: dict) -> str:
    user_input = payload.get("input")
    response = agent(user_input)
    return response.message['content'][0]['text']


if __name__ == "__main__":
    payload = {
        "input": "5+7 = ?"
    }
    response = invoke_agent(payload)
    print(response)