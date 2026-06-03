# Using Strands Agents SDK for this example

import asyncio

import json
import urllib

from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# Set your MCP server details from Step 4
RUNTIME_ID = "mcp_server-bu2pjnAF95"
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


def main():
    region = "us-east-1"
    
    mcp_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/mcp_server-3sse3aErt1"
    encoded_arn = urllib.parse.quote(mcp_runtime_arn, safe="")
    mcp_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"

    mcp_server = MCPClient(lambda: aws_iam_streamablehttp_client(
        endpoint=mcp_url,
        aws_region=region,
        aws_service="bedrock-agentcore"
    ))

    try:
        with mcp_server:
            mcp_tools = mcp_server.list_tools_sync()
            print(f"Available MCP tools: {[tool.tool_name for tool in mcp_tools]}")
    except Exception as e:
        if "404" not in str(e):
            raise




if __name__ == "__main__":
    main()