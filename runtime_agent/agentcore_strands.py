import json
from strands import Agent
from runtime_agent.memory_hook import ShortTermMemoryHookProvider
from runtime_agent.guardrail_hook import NotifyOnlyGuardrailsHook

from bedrock_agentcore.memory.client import MemoryClient

from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
import urllib.parse

app = BedrockAgentCoreApp()
region = "us-east-1"
mcp_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/mcp_server-JD6RpiCGiG"
encoded_arn = urllib.parse.quote(mcp_runtime_arn, safe="")
mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

print(f"Constructed MCP URL: {mcp_url}")


mcp_server = MCPClient(lambda: aws_iam_streamablehttp_client(endpoint=mcp_url,
                                                             aws_region=region,
                                                             aws_service="bedrock-agentcore"))

        
model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

client = MemoryClient(region_name="us-east-1")
memory_id="my_agent_memory-SkOM8s2Uk6"
guardrail_id = "5286eay7oaez"
guardrail_version = "1"

model = BedrockModel(model_id=model_id)
mcp_tools = []

try:
    with mcp_server:
        mcp_tools = (mcp_server.list_tools_sync())
        app.logger.info(f"Available MCP tools: {[tool.tool_name for tool in mcp_tools]}")

except Exception as e:
        if "404" not in str(e):
            raise

agent = Agent(model=model,
              hooks=[ShortTermMemoryHookProvider(client, memory_id),
                     NotifyOnlyGuardrailsHook(guardrail_id, guardrail_version)],
              tools = mcp_tools,
              system_prompt="You are a helpful assistant. Use the available tools to answer user queries when relevant.")
        

@app.entrypoint
def invoke(payload: dict, context: RequestContext) -> str:
    app.logger.info("Received user input: %s", json.dumps(payload))
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

    agent.state.set("actor_id", actor_id)
    agent.state.set("session_id", session_id)
    
    # Now invoke the agent with enriched state
    response = agent(user_input)

    app.logger.info("Agent response: %s", response)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()