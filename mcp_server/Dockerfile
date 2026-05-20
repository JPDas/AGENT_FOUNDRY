FROM python:3.12-slim
WORKDIR /app

# Configure UV for container environment
ENV UV_SYSTEM_PYTHON=1 UV_COMPILE_BYTECODE=1

COPY requirements.txt requirements.txt
# Install from requirements file
RUN pip install -r requirements.txt

# Set AWS region environment variable
ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1

# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 8080
EXPOSE 8000

# Copy only the agent folder
COPY . ./mcp_server

# Use the full module path directly (no opentelemetry wrapper)
CMD ["python", "-m", "mcp_server.server"]
