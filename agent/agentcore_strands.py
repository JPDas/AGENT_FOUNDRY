import json
import boto3
from requests_aws4auth import AWS4Auth
from strands import Agent
from strands.hooks import (
    HookProvider, 
    HookRegistry, 
    MessageAddedEvent, 
    AgentInitializedEvent
)

from bedrock_agentcore.memory.client import MemoryClient

from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
import urllib.parse

app = BedrockAgentCoreApp()
region = "us-east-1"
mcp_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/mcp_server-f74IoQ7wS0"
encoded_arn = urllib.parse.quote(mcp_runtime_arn, safe="")
mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

print(f"Constructed MCP URL: {mcp_url}")


mcp_server = MCPClient(lambda: aws_iam_streamablehttp_client(endpoint=mcp_url,
                                                             aws_region=region,
                                                             aws_service="bedrock-agentcore"))


class ShortTermMemoryHookProvider(HookProvider):
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.memory_client = memory_client
        self.memory_id = memory_id

    def register_hooks(self, registry: HookRegistry):
        # Register memory hooks
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)

    def on_message_added(self, event: MessageAddedEvent):
        messages = event.agent.messages
        actor_id = event.agent.state.get("actor_id")
        session_id = event.agent.state.get("session_id")

        if messages[-1]["content"][0].get("text"):
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                messages=[(messages[-1]["content"][0]["text"], messages[-1]["role"])])
            

    def on_agent_initialized(self, event: AgentInitializedEvent):
 
        actor_id = event.agent.state.get("actor_id")
        session_id = event.agent.state.get("session_id")

        if not actor_id or not session_id:
            return

        # Load the last 5 conversation turns from memory
        recent_turns = self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                k=10
            )

        if recent_turns:
            # Format conversation history for context
            context_messages = []
            for turn in recent_turns:
                for message in turn:
                        role = message['role']
                        content = message['content']['text']
                        context_messages.append(f"{role}: {content}")

            context = "\n".join(context_messages)
            # Add context to agent's system prompt.
            event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"


model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

client = MemoryClient(region_name="us-east-1")
memory_id="my_agent_memory-8UGctI2OWk"

model = BedrockModel(model_id=model_id)

with mcp_server:
    mcp_tools = (mcp_server.list_tools_sync())
    print(f"Available MCP tools: {[tool.tool_name for tool in mcp_tools]}")


    agent = Agent(model=model,
                  hooks=[ShortTermMemoryHookProvider(client, memory_id)],
                  tools = mcp_tools,
                  system_prompt="You are a helpful assistant. Use the available tools to answer user queries when relevant.")
            

@app.entrypoint
def invoke(payload: dict, context: RequestContext) -> str:
    user_input = payload.get("prompt")

    app.logger.info("Received user input: %s", user_input)

    actor_id = payload.get("actor_id", "unknown_actor")
    app.logger.info("Extracted actor_id from payload: %s", actor_id)

    # Access request headers here
    request_headers = context.request_headers
    app.logger.info("Headers: %s", json.dumps(request_headers))

    # Extract session_id from context.
    session_id = context.session_id
    app.logger.info("Extracted actor_id: %s, session_id: %s", actor_id, session_id)

    # # Inject into agent state so hooks can use them
    agent.state["actor_id"] = actor_id
    agent.state["session_id"] = session_id

    # Now invoke the agent with enriched state
    response = agent(user_input)

    app.logger.info("Agent response: %s", response)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()