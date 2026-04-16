import json
from strands import Agent, tool    

from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext

app = BedrockAgentCoreApp()

@tool 
def get_weather(location: str) -> str:
    """Get weather data for a city as location using browser automation"""
    # This is a mock implementation. In a real implementation, you would call a weather API.
    return f"The current weather in {location} is sunny with a temperature of 25°C."

model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

model = BedrockModel(model_id=model_id)

agent = Agent(model=model, 
              tools=[get_weather],
              system_prompt="You are a helpful assistant that can provide weather information from the location name.")


@app.entrypoint
def invoke(payload: dict, context: RequestContext) -> str:
    user_input = payload.get("prompt")

    app.logger.info("Received user input: %s", user_input)

    # access request headers here
    request_headers = context.request_headers
    app.logger.info("Headers: %s", json.dumps(request_headers))

    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()