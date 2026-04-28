from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time
import os
import sys
from io import StringIO
from contextlib import contextmanager
from strands.telemetry import StrandsTelemetry

from openinference.instrumentation.strands_agents import StrandsAgentsToOpenInferenceProcessor

from dotenv import load_dotenv

load_dotenv()

# Define a custom tool as a Python function using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())

# Configure OpenAI model
model = OpenAIModel(
    client_args={
        "api_key": os.getenv("OPENAI_API_KEY"),  # Set your API key in environment
    },
    model_id="gpt-4o-mini",  # Options: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

# Create an agent with OpenAI model and tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(model=model, 
              tools=[calculator, current_time, letter_counter], 
              callback_handler=None,
              trace_attributes={
                    "user.id": "user_12345",
                    "session.id": "session_67890",
                    "tags": ["Strands", "Observability"],
                },)

@contextmanager
def suppress_stdout():
    """Context manager to suppress stdout output."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield
    finally:
        sys.stdout = old_stdout

def print_response(response):
    """Parse and print the agent response in a clean, readable format."""
    if hasattr(response, 'content'):
        # Handle structured response object
        for content in response.content:
            if hasattr(content, 'text'):
                print(content.text)
            elif isinstance(content, dict) and 'text' in content:
                print(content['text'])
            else:
                print(content)
    elif isinstance(response, str):
        # Handle string response
        print(response)
    elif isinstance(response, list):
        # Handle list of responses
        for item in response:
            if hasattr(item, 'text'):
                print(item.text)
            elif isinstance(item, dict) and 'text' in item:
                print(item['text'])
            else:
                print(item)
    else:
        # Fallback - print as is
        print(response)


# Interactive mode - get prompt from user
if __name__ == "__main__":
    print("Strands Agent with OpenAI")
    print("=" * 50)
    print("Type your question or 'exit' to quit\n")

    # Setup Strands' native telemetry
    print("📡 Setting up telemetry...")
            
    telemetry = StrandsTelemetry()

    # Export to Phoenix (or other OTLP endpoint)
    telemetry.setup_otlp_exporter(endpoint="http://127.0.0.1:6006/v1/traces")

    # Optional: Also log to console for debugging
    # telemetry.setup_console_exporter()

    # Add OpenInference processor to transform spans
    telemetry.tracer_provider.add_span_processor(
        StrandsAgentsToOpenInferenceProcessor(debug=False)  # Set debug=True for verbose output
    )

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            # Get response from agent (suppress intermediate output)
            with suppress_stdout():

                response = agent(user_input)

            # Parse and print only the final response
            print("\nAgent: ")
            print_response(response)
            print()

        except Exception as e:
            print(f"\nError: {str(e)}\n")
