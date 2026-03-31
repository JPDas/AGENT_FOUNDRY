import boto3
import json
import traceback
from botocore.exceptions import ClientError

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