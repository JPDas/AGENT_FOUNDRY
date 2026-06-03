from strands.hooks import (
    HookProvider, 
    HookRegistry, 
    MessageAddedEvent, 
    AgentInitializedEvent,
    AfterInvocationEvent
)

from bedrock_agentcore.memory.client import MemoryClient

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


#supports both memory type short-term and long-term memory
class MemoryHookProvider(HookProvider):
    def __init__(self, memory_id:str, memory_client:MemoryClient):
        self.memory_id = memory_id
        self.memory_client = memory_client

    def register_hooks(self, registry: HookRegistry) -> None:
        """Register memory hooks"""
        registry.add_callback(MessageAddedEvent, self.retrieve_memories)
        registry.add_callback(AfterInvocationEvent, self.save_memories)
        print("Memory hooks registered") 

    def retrieve_memory(self, event: MessageAddedEvent):
        messages = event.agent.messages

        if messages[-1]["role"] == "user" and "toolResult" not in messages[-1]["content"][0]:
            user_message = messages[-1]["content"][0].get("text", "")
            
            try:
                # Get actor_id from agent state
                actor_id = event.agent.state.get("actor_id")
                if not actor_id:
                    print("Missing actor_id in agent state")
                    return
                
                namespace = f"/users/{actor_id}/facts"

                 # Retrieve relevant memories
                memories = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace,
                    query=user_message
                )

                # Extract memory content
                memory_context = []
                for memory in memories:
                    if isinstance(memory, dict):
                        content = memory.get('content', {})
                        if isinstance(content, dict):
                            text = content.get('text', '').strip()
                            if text:
                                memory_context.append(text)

                # Inject memories into user message
                if memory_context:
                    context_text = "\n".join(memory_context)
                    original_text = messages[-1]["content"][0].get("text", "")
                    messages[-1]["content"][0]["text"] = (
                        f"{original_text}\n\nPrevious context: {context_text}"
                    )
                    print(f"Retrieved {len(memory_context)} memories")
                    
            except Exception as e:
                print(f"Failed to retrieve memories: {e}")

    def save_memories(self, event: AfterInvocationEvent):

        try:
            messages = event.agent.messages
            if len(messages) >= 2 and messages[-1]["role"] == "assistant":
                # Get last user and assistant messages
                user_msg = None
                assistant_msg = None
                
                for msg in reversed(messages):
                    if msg["role"] == "assistant" and not assistant_msg:
                        assistant_msg = msg["content"][0]["text"]
                    elif msg["role"] == "user" and not user_msg and "toolResult" not in msg["content"][0]:
                        user_msg = msg["content"][0]["text"]
                        break
                
                if user_msg and assistant_msg:
                    # Get session info from agent state
                    actor_id = event.agent.state.get("actor_id")
                    session_id = event.agent.state.get("session_id")
                    
                    if not actor_id or not session_id:
                        print("Missing actor_id or session_id in agent state")
                        return
                    
                    # Save conversation
                    self.memory_client.create_event(
                        memory_id=self.memory_id,
                        actor_id=actor_id,
                        session_id=session_id,
                        messages=[(user_msg, "USER"), (assistant_msg, "ASSISTANT")]
                    )
                    print("Saved conversation to memory")
                    
        except Exception as e:
            print(f"Failed to save memories: {e}")

