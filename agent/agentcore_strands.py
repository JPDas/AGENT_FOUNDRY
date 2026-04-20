import json
from pyexpat.errors import messages
from strands import Agent, tool, HookProvider, HookRegistry, MessageAddedEvent, AgentInitializedEvent
from bedrock_agentcore.memory.client import MemoryClient    

from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext

app = BedrockAgentCoreApp()

# class ShortTermMemoryHookProvider(HookProvider):
#     def __init__(self, memory_client: MemoryClient, memory_id: str):
#         self.memory_client = memory_client
#         self.memory_id = memory_id

#     def register_hooks(self, registry: HookRegistry):
#         # Register memory hooks
#         registry.add_callback(MessageAddedEvent, self.on_message_added)
#         registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)

#     def on_message_added(self, event: MessageAddedEvent):
#         messages = event.agent.messages
#         actor_id = event.agent.state.get("actor_id")
#         session_id = event.agent.state.get("session_id")

#         if messages[-1]["content"][0].get("text"):
#             self.memory_client.create_event(
#                 memory_id=self.memory_id,
#                 actor_id=actor_id,
#                 session_id=session_id,
#                 messages=[(messages[-1]["content"][0]["text"], messages[-1]["role"])])
            

#     def on_agent_initialized(self, event: AgentInitializedEvent):
 
#         actor_id = event.agent.state.get("actor_id")
#         session_id = event.agent.state.get("session_id")

#         # Load the last 5 conversation turns from memory
#         recent_turns = self.memory_client.get_last_k_turns(
#                 memory_id=self.memory_id,
#                 actor_id=actor_id,
#                 session_id=session_id,
#                 k=5
#             )

#         if recent_turns:
#             # Format conversation history for context
#             context_messages = []
#             for turn in recent_turns:
#                 for message in turn:
#                         role = message['role']
#                         content = message['content']['text']
#                         context_messages.append(f"{role}: {content}")

#             context = "\n".join(context_messages)
#             # Add context to agent's system prompt.
#             event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"

@tool 
def get_weather(location: str) -> str:
    """Get weather data for a city as location using browser automation"""
    # This is a mock implementation. In a real implementation, you would call a weather API.
    return f"The current weather in {location} is sunny with a temperature of 25°C."

model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# ACTOR_ID = "order_statistics_user_123" # It can be any unique identifier (AgentID, User ID, etc.)
# SESSION_ID = "order_statistics_session_001" # Unique session identifier
# client = MemoryClient(region_name="us-east-1")
# memory_id="{YOUR_MEMORY_ID}"

model = BedrockModel(model_id=model_id)

agent = Agent(model=model, 
              tools=[get_weather],
            #   hooks=[ShortTermMemoryHookProvider(client, memory_id)],
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