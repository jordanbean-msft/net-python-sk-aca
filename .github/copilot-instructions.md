---
description: Architecture and development guidelines for the multi-container chat application
applyTo: "**"
---

# Project Architecture

This is a multi-tier chat application with the following architecture:

## Technology Stack

- **Frontend**: Simple React application served from the C# API
- **Backend API**: C# .NET 8 MVC API
- **AI Service**: Python FastAPI with Semantic Kernel
- **Weather Function**: Python Azure Function (tool for AI agent)
- **Infrastructure**: Terraform (Azure Container Apps)
- **Hosting**: Azure Container Apps (separate containers for C#, Python AI service) and and Azure Function for the Weather API

## Component Interactions

1. JavaScript frontend → C# .NET API
2. C# .NET API → Python Semantic Kernel API
3. Python API uses Azure AI Foundry Chat Completion Agent with registered tools
4. AI Agent can call Weather Function (Azure Function) via Semantic Kernel tool
5. Responses stream back: Python → C# → JavaScript

## Development Guidelines

### Frontend (React/JavaScript)

- Keep the React frontend simple and lightweight
- Static files are served from the C# API
- Implement streaming response handling for chat messages
- Use fetch API or similar for HTTP requests to C# backend
- **Use relative URLs** (e.g., `/api/chat`) instead of hardcoded localhost URLs for backend communication
- Render markdown responses using `react-markdown` library
- Include proper CSS styling in separate CSS files (not inline styles)
- Maintain input focus after bot responses
- Implement real-time UI updates for streaming with `await new Promise(resolve => setTimeout(resolve, 0))` after state updates

### C# .NET 8 MVC API

- ASP.NET Core MVC pattern
- Serve static React files from wwwroot or similar
- Act as a proxy/gateway to the Python Semantic Kernel API
- Handle streaming responses from Python and forward to frontend
- Use HttpClient for Python API communication
- **Use proper ASP.NET Core logging (ILogger)** - never use Console.WriteLine
- Support both streaming and non-streaming endpoints
- Maintain chat history across requests
- **Port and log level must be configurable via environment variables**
- **No unit tests required**

### Python FastAPI + Semantic Kernel

- FastAPI framework for the web API
- Semantic Kernel for AI orchestration
- Create a single Azure AI Foundry Chat Completion Agent
- Register Semantic Kernel function tools with the agent
- **Enable automatic function calling** in execution settings
- Implement streaming responses using Server-Sent Events (SSE) or similar
- Handle chat completion requests and stream responses
- **Always use Python `logging` module** - never use print() statements
- **Use module-level loggers** with appropriate log levels
- **Configure logging before app initialization** with proper format and level
- **Log LLM tool calls** when the AI agent invokes Semantic Kernel functions
- Check for function call content in streaming chunks and non-streaming responses
- **Always use `uv` for package management and running Python**
- **Use `pyproject.toml` for dependency management (not requirements.txt)**
- Organize plugins in separate files under `app/plugins/` directory
- **Port and log level must be configurable via environment variables**
- **No unit tests required**

### Python Azure Function (Weather Tool)

- Python Azure Functions v4 programming model
- HTTP trigger function that returns hardcoded weather data
- Returns JSON response with weather information (temperature, conditions, location)
- Runs as a separate Docker container locally via Docker Compose
- Called by Semantic Kernel AI agent as a registered tool/function
- **Use official Azure Functions base image**: `mcr.microsoft.com/azure-functions/python:4-python3.12`
- **Use `requirements.txt`** for Azure Functions (not pyproject.toml due to Azure Functions runtime requirements)
- **Use Python `logging` module** for all logging (not print() statements)
- Container listens on port 80 internally (mapped to 7071 externally in docker-compose)
- **Logging must be configurable via environment variables and host.json**
- **Enable console logging for containerized environments**
- **No unit tests required**
- Function should be registered in Semantic Kernel as a tool the AI agent can invoke

### Docker Containerization

- Separate Dockerfile for C# API
- Separate Dockerfile for Python AI service
- Separate Dockerfile for Python Azure Function
- C# container includes built React frontend
- Python AI service uses `uv` for fast dependency installation
- Python AI service container includes FastAPI and Semantic Kernel dependencies
- Azure Function uses official base image `mcr.microsoft.com/azure-functions/python:4-python3.12`
- Azure Function container includes Azure Functions runtime and dependencies
- Use multi-stage builds for optimization
- **Development vs Production builds**: Use `BUILD_ENV` arg to control optimizations
  - Development: `GENERATE_SOURCEMAP=false`, `INLINE_RUNTIME_CHUNK=false`, `IMAGE_INLINE_SIZE_LIMIT=0`
  - Production: Full optimizations enabled
- **Port Configuration**: Ports must be configurable via build args and environment variables
  - Backend and AI Service support custom ports
  - Weather Function port controlled by Azure Functions runtime
  - Use shell form in CMD when environment variable expansion needed at runtime
- **Log Level Configuration**: All services must support configurable log levels via environment variables
  - Backend: Standard ASP.NET Core logging configuration
  - AI Service: Application and uvicorn log levels
  - Weather Function: Azure Functions host logging configuration
- **Health Checks**: All containers must include health check endpoints
  - Install curl for health check support
  - Health endpoints at `/health` or `/api/health`
  - Docker Compose uses health check conditions for service dependencies
  - 10s interval, 5s timeout, 3 retries, 30s start period

### Infrastructure as Code (Terraform)

- Use Terraform for all Azure infrastructure
- Deploy to Azure Container Apps
- Provision separate container apps for C# and Python services
- Configure Azure AI Foundry resources for the agent
- Set up networking, environment variables, and secrets
- Include container registry configuration

### Azure Resources

- Azure Container Apps for C# API
- Azure Container Apps for Python AI service
- Azure Functions (containerized) for Python Weather Tool
- Azure AI Foundry for Chat Completion Agent
- Azure Container Registry for Docker images
- Appropriate networking and security configurations

## Code Organization

- `/src/frontend` - React application
- `/src/backend` - C# .NET 8 API
- `/src/ai-service` - Python Semantic Kernel API
  - `/app/plugins/` - Semantic Kernel plugins (one plugin per file)
  - `/app/core/` - Core functionality (config, dependencies, telemetry, lifespan)
  - `/app/routers/` - FastAPI route handlers
  - `/app/services/` - Business logic services
  - `/app/models/` - Data models and converters
- `/src/weather-function` - Python Azure Function (Weather Tool)
- `/infra` - Terraform configurations

## Observability & Telemetry

### Application Insights Integration

- AI service configured to send telemetry to Azure Application Insights
- Uses OpenTelemetry with Azure Monitor exporters
- Telemetry module in `app/core/telemetry.py` configures:
  - **LoggerProvider** with BatchLogRecordProcessor
  - **TracerProvider** with BatchSpanProcessor
  - **MeterProvider** with PeriodicExportingMetricReader
- Filter configured to only log `semantic_kernel` events
- Connection string configured via `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
- Telemetry automatically activates when connection string is provided

### Logging Best Practices

- **Python**: Always use `logging` module, never `print()` statements
  - Use module-level loggers with appropriate naming
  - Log LLM tool calls when AI agent invokes Semantic Kernel functions
  - Check for function call content in responses to detect tool calls
  - Use appropriate log levels: `debug`, `info`, `warning`, `error`, `exception`
- **C#**: Always use `ILogger`, never `Console.WriteLine`
  - Inject `ILogger<T>` via dependency injection
  - Use structured logging with message templates
- **Log what matters**:
  - AI agent tool/function calls with function name, plugin, and arguments
  - Streaming start and completion events
  - Error conditions with context and full stack traces

## Important Notes

- **No unit tests** are needed for this project
- **Always use `uv` for Python** package management and execution
- Focus on streaming capabilities throughout the stack
- Ensure proper error handling in the request chain
- Configure CORS appropriately between services
- Use environment variables for configuration (API endpoints, Azure credentials)
