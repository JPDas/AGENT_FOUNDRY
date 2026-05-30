import logging
import os
import urllib.parse
from strands import Agent
from strands.multiagent.a2a.executor import StrandsA2AExecutor
from bedrock_agentcore.runtime import serve_a2a
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

import uvicorn
from fastapi import FastAPI


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

region = "us-east-1"
mcp_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/mcp_server-UnYR9z9mm9"
encoded_arn = urllib.parse.quote(mcp_runtime_arn, safe="")
mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
# mcp_url = "http://localhost:8000/mcp"

print(f"Constructed MCP URL: {mcp_url}")


mcp_server = MCPClient(lambda: aws_iam_streamablehttp_client(endpoint=mcp_url,
                                                             aws_region=region,
                                                             aws_service="bedrock-agentcore"))


model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

def main():

    with mcp_server:
        mcp_tools = (mcp_server.list_tools_sync())
        print(f"Available MCP tools: {[tool.tool_name for tool in mcp_tools]}")


        strands_agent = Agent(model=model_id,
                    tools = mcp_tools,
                    system_prompt="You are a helpful assistant. Use the available tools to answer user queries when relevant.",
                    name="A2A Agent",
                    description="An agent that uses tools from an MCP server to answer user queries.")
        


        serve_a2a(StrandsA2AExecutor(strands_agent, enable_a2a_compliant_streaming=True))

if __name__ == "__main__":
    main()