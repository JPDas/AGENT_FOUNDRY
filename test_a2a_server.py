import asyncio
import logging
import os
from uuid import uuid4
import urllib.parse

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart

from requests_aws4auth import AWS4Auth
from botocore.session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # set request timeout to 5 minutes

# Get runtime URL from environment variable
runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/a2a_agent-aA0Arx5EK4"
region = "us-east-1"
encoded_arn = urllib.parse.quote(runtime_arn, safe="")
runtime_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations/"

def create_message(*, role: Role = Role.user, text: str) -> Message:
    return Message(
        kind="message",
        role=role,
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid4().hex,
    )

async def send_sync_message(message: str):
    
    # Generate a unique session ID
    session_id = str(uuid4())
    print(f"Generated session ID: {session_id}")

    credentials = Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        "us-east-1",
        "bedrock-agentcore",
        session_token=credentials.token
    )
    # Add authentication headers for Amazon Bedrock AgentCore
    headers = {'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': session_id, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, auth= aws_auth, headers=headers) as httpx_client:
        # Get agent card from the runtime URL
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=runtime_url)
        agent_card = await resolver.get_agent_card()

        print(f"Retrieved agent card: {agent_card.model_dump_json(exclude_none=True, indent=2)}")   

        # Agent card contains the correct URL (same as runtime_url in this case)
        # No manual override needed - this is the path-based mounting pattern

        # Create client using factory
        config = ClientConfig(
            httpx_client=httpx_client,
            streaming=False,  # Use non-streaming mode for sync response
        )
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        # Create and send message
        msg = create_message(text=message)

        # With streaming=False, this will yield exactly one result
        async for event in client.send_message(msg):
            if isinstance(event, Message):
                logger.info(event.model_dump_json(exclude_none=True, indent=2))
                return event
            elif isinstance(event, tuple) and len(event) == 2:
                # (Task, UpdateEvent) tuple
                task, update_event = event
                logger.info(f"Task: {task.model_dump_json(exclude_none=True, indent=2)}")
                if update_event:
                    logger.info(f"Update: {update_event.model_dump_json(exclude_none=True, indent=2)}")
                return task
            else:
                # Fallback for other response types
                logger.info(f"Response: {str(event)}")
                return event

# Usage - Uses AGENTCORE_RUNTIME_URL environment variable

while True:
    user_input = input("Enter your prompt (type 'q' to quit): ")
    if user_input.lower() == "q":
        print("Exiting program...")
        break
    asyncio.run(send_sync_message(user_input))
