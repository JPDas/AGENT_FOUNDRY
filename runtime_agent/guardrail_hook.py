import boto3
import json
from strands.hooks import HookProvider, HookRegistry, MessageAddedEvent, AfterInvocationEvent

class NotifyOnlyGuardrailsHook(HookProvider):
    def __init__(self, guardrail_id: str, guardrail_version: str):
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
        self.bedrock_client = boto3.client("bedrock-runtime", "us-east-1") # change to your AWS region
        print(f"Initialized Bedrock client for guardrail evaluation in region us-east-1 with guardrail ID {guardrail_id} and version {guardrail_version}")

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(MessageAddedEvent, self.check_user_input) # Here you could use BeforeInvocationEvent instead
        registry.add_callback(AfterInvocationEvent, self.check_assistant_response)

    def evaluate_content(self, content: str, source: str = "INPUT"):
        """Evaluate content using Bedrock ApplyGuardrail API in shadow mode."""
        try:
            response = self.bedrock_client.apply_guardrail(
                guardrailIdentifier=self.guardrail_id,
                guardrailVersion=self.guardrail_version,
                source=source,
                content=[{"text": {"text": content}}]
            )

            print(f"[GUARDRAIL] Evaluation response for {source}: {json.dumps(response, indent=2)}")
            if response.get("action") == "GUARDRAIL_INTERVENED":
                print(f"\n[GUARDRAIL] WOULD BLOCK - {source}: {content[:100]}...")
                # Show violation details from assessments
                for assessment in response.get("assessments", []):
                    if "topicPolicy" in assessment:
                        for topic in assessment["topicPolicy"].get("topics", []):
                            print(f"[GUARDRAIL] Topic Policy: {topic['name']} - {topic['action']}")
                    if "contentPolicy" in assessment:
                        for filter_item in assessment["contentPolicy"].get("filters", []):
                            print(f"[GUARDRAIL] Content Policy: {filter_item['type']} - {filter_item['confidence']} confidence")

        except Exception as e:
            print(f"[GUARDRAIL] Evaluation failed: {e}")

    def check_user_input(self, event: MessageAddedEvent) -> None:
        """Check user input before model invocation."""
        if event.message.get("role") == "user":
            content = "".join(block.get("text", "") for block in event.message.get("content", []))
            if content:
                self.evaluate_content(content, "INPUT")

    def check_assistant_response(self, event: AfterInvocationEvent) -> None:
        """Check assistant response after model invocation with delay to avoid interrupting output."""
        if event.agent.messages and event.agent.messages[-1].get("role") == "assistant":
            assistant_message = event.agent.messages[-1]
            content = "".join(block.get("text", "") for block in assistant_message.get("content", []))
            if content:
                self.evaluate_content(content, "OUTPUT")

