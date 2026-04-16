import boto3
import json
import traceback
from botocore.exceptions import ClientError
from bedrock_agentcore.memory.client import MemoryClient

def test_invoke_agent_runtime():

    # Initialize the Bedrock AgentCore client
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')

    runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:471112848798:runtime/myagent_runtime-jS4Cbi8a9M"

    # Prepare the payload (send bytes)
    payload = json.dumps({"prompt": "what is the temperature in Bangalore?"})
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            # runtimeSessionId=session_id, # for maintaining conversation context across multiple interactions
            qualifier="DEFAULT",
            payload=payload
        )

        print(f"Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        print("Content Type:", response.get('contentType', 'N/A'))

        # response['response'] is a StreamingBody; read and decode safely
        response_body = response['response'].read()
        try:
            response_data = json.loads(response_body)
        except Exception:
            response_data = response_body.decode("utf-8", errors="replace")
        print("Agent Response:", response_data)

    except ClientError as e:
        # Print useful debug info when the runtime returns a 500
        print("ClientError calling InvokeAgentRuntime:", str(e))
        if hasattr(e, "response"):
            try:
                print("Error response:", json.dumps(e.response, indent=2, default=str))
            except Exception:
                print("Error response (raw):", e.response)
        traceback.print_exc()
        print("\nRecommendation: check CloudWatch logs for the runtime ARN to see the runtime-side error:\n", runtime_arn)
    except Exception as e:
        print("Unexpected error:", str(e))
        traceback.print_exc()
        print("\nRecommendation: check CloudWatch logs for the runtime ARN:\n", runtime_arn)

def test_memory_operations(memory_id, region_name="us-east-1"):
    """Test basic memory operations."""
    try:
        print(f"🧪 Testing memory operations with memory ID: {memory_id}")
        
        # Initialize memory client
        memory_client = MemoryClient(region_name=region_name)
        
        # Test creating an event
        test_event = memory_client.create_event(
            memory_id=memory_id,
            actor_id="test-user",
            session_id="test-session",
            messages=[
                ("Hello, I'm testing the memory system", "USER"),
                ("Great! The memory system is working correctly", "ASSISTANT")
            ]
        )
        
        event_id = test_event.get("eventId")
        print(f"✅ Test event created: {event_id}")
        
        # Test retrieving the event
        retrieved_event = memory_client.get_event(
            memoryId=memory_id,
            actorId="test-user",
            sessionId="test-session",
            eventId=event_id
        )
        
        print(f"✅ Event retrieval successful: {retrieved_event}")
        
        # Clean up test event
        memory_client.delete_event(
            memoryId=memory_id,
            actorId="test-user",
            sessionId="test-session",
            eventId=event_id
        )
        
        print("✅ Test event cleaned up")
        print("✅ All memory operations working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory operations test failed: {e}")
        return False


if __name__ == "__main__":
    memory_id = "my_agent_memory-186HgM6PqD"  
    test_memory_operations(memory_id)

