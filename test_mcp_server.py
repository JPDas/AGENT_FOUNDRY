# Using Strands Agents SDK for this example

import asyncio

import json

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Set your MCP server details from Step 4
RUNTIME_ID = "mcp_server-fs9RHz4Gr0"
ACCOUNT_ID = "471112848798"
REGION = "us-east-1"

def get_headers(region, endpoint_url, method_name, params=None):
    # 1. Initialize AWS Credentials
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    
    # 2. Build the exact MCP body (SigV4 requires this to sign accurately)
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method_name,
        "params": params or {}
    })
    
    # 3. Create the botocore AWSRequest object
    request = AWSRequest(
        method='POST', 
        url=endpoint_url, 
        data=body,
        headers={'Content-Type': 'application/json'}
    )
    
    # 4. Sign the request (this injects Authorization and X-Amz-Date into request.headers)
    print(f"Signing request with AWS credentials for region: {region} and endpoint: {endpoint_url}")
    SigV4Auth(credentials, 'bedrock-agentcore', region).add_auth(request)
    
    # 5. Extract and return the final signed headers dictionary
    return dict(request.headers)


async def main():
    # Build the MCP server URL
    url = f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{RUNTIME_ID}/invocations?qualifier=DEFAULT&accountId={ACCOUNT_ID}"

    print(f"\nInitializing MCP client with IAM-based auth for:\n{url}")

    headers = get_headers(REGION, url, method_name="list_tools")
    print(f"Generated signed headers:\n{headers}\n")

    async with streamablehttp_client(url, headers, timeout=120, terminate_on_close=False) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            print(tool_result)

if __name__ == "__main__":
    asyncio.run(main())