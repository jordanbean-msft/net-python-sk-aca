# AI Service - Python FastAPI with Semantic Kernel

This service provides an AI chat completion API using Azure AI Foundry and Semantic Kernel.

## Features

- **FastAPI Framework**: High-performance async API
- **Semantic Kernel Integration**: Azure AI Foundry Chat Completion Agent
- **Streaming Responses**: Server-Sent Events (SSE) for real-time streaming
- **Managed Identity Authentication**: Secure Azure credential handling
- **OpenTelemetry Tracing**: Built-in observability support
- **Docker Support**: Containerized deployment

## Environment Variables

Create a `.env` file with the following variables:

```env
AZURE_AI_PROJECT_ENDPOINT=https://your-project.cognitiveservices.azure.com/
AZURE_AI_MODEL_DEPLOYMENT=your-model-deployment-name
APP_NAME=AI Chat Service
LOG_LEVEL=INFO
ENABLE_TRACING=true
OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

## Local Development

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

1. Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:

```bash
uv sync
```

Or manually:

```bash
uv pip install .
```

3. Run the application:

```bash
uv run python main.py
```

Or run with uvicorn directly:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

```
GET /health
```

### Chat (Streaming)

```
POST /chat/stream
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "stream": true
}
```

Returns Server-Sent Events stream.

### Chat (Non-streaming)

```
POST /chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "stream": false
}
```

Returns complete JSON response.

## Docker Build

The Dockerfile uses `uv` for fast dependency installation.

Build the Docker image:

```bash
docker build -t ai-service:latest .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e AZURE_AI_PROJECT_ENDPOINT=your-endpoint \
  -e AZURE_AI_MODEL_DEPLOYMENT=your-deployment \
  ai-service:latest
```

## Architecture

- **main.py**: FastAPI application entry point and configuration
- **app/**: Application package with modular structure
  - **core/**: Core application infrastructure
    - **config.py**: Application settings and configuration management
    - **dependencies.py**: FastAPI dependency injection providers
    - **tracing.py**: OpenTelemetry tracing setup
    - **lifespan.py**: FastAPI application lifespan management
  - **services/**: Business logic and AI services
    - **agent.py**: Semantic Kernel chat agent service
  - **models/**: Domain models for API communication
    - **chat.py**: Chat message and history models (API DTOs)
    - **converters.py**: Converters between API models and Semantic Kernel types
  - **routers/**: API route handlers
    - **chat.py**: Chat completion endpoints (streaming and non-streaming)
    - **health.py**: Health check and root endpoints
- **pyproject.toml**: Project configuration and Python dependencies
- **Dockerfile**: Container image configuration

### Custom Chat Models

The application uses custom Pydantic models for API communication between C# and Python:

- **ChatMessage**: Individual message with role (system/user/assistant) and content
- **ChatHistoryModel**: Collection of chat messages for maintaining conversation context
- **ChatRequest**: Request model including message, optional history, and stream flag
- **ChatResponse**: Response model with assistant's reply and updated conversation history

These models are automatically converted to/from Semantic Kernel's `ChatHistory` using the converter utilities in `models/converters.py`.

### Dependency Injection

This application uses FastAPI's dependency injection system for managing services:

- **AgentServiceDep**: Type-annotated dependency for injecting `ChatAgentService` into route handlers
- Services are initialized once at startup and reused across requests
- Enables better testability by allowing easy mocking of dependencies

## Authentication

This service uses Azure Managed Identity (DefaultAzureCredential) for authentication, following Azure best practices. In development, it will use your Azure CLI credentials. In production (Azure Container Apps), it will use the managed identity assigned to the container.

## Why uv?

This project uses [uv](https://docs.astral.sh/uv/) because it's:

- **10-100x faster** than pip for installing packages
- **Written in Rust** for maximum performance
- **Drop-in replacement** for pip with the same commands
- **Optimized for Docker** with efficient caching and smaller layers
