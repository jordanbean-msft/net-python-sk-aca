---
description: Architecture and development guidelines for the multi-container chat application
applyTo: '**'
---

# Project Architecture

This is a multi-tier chat application with the following architecture:

## Technology Stack

- **Frontend**: Simple React application served from the C# API
- **Backend API**: C# .NET 8 MVC API
- **AI Service**: Python FastAPI with Semantic Kernel
- **Infrastructure**: Terraform (Azure Container Apps)
- **Hosting**: Azure Container Apps (separate containers for C# and Python)

## Component Interactions

1. JavaScript frontend → C# .NET API
2. C# .NET API → Python Semantic Kernel API
3. Python API uses Azure AI Foundry Chat Completion Agent
4. Responses stream back: Python → C# → JavaScript

## Development Guidelines

### Frontend (React/JavaScript)

- Keep the React frontend simple and lightweight
- Static files are served from the C# API
- Implement streaming response handling for chat messages
- Use fetch API or similar for HTTP requests to C# backend

### C# .NET 8 MVC API

- ASP.NET Core MVC pattern
- Serve static React files from wwwroot or similar
- Act as a proxy/gateway to the Python Semantic Kernel API
- Handle streaming responses from Python and forward to frontend
- Use HttpClient for Python API communication
- **No unit tests required**

### Python FastAPI + Semantic Kernel

- FastAPI framework for the web API
- Semantic Kernel for AI orchestration
- Create a single Azure AI Foundry Chat Completion Agent
- Implement streaming responses using Server-Sent Events (SSE) or similar
- Handle chat completion requests and stream responses
- **Always use `uv` for package management and running Python**
- **Use `pyproject.toml` for dependency management (not requirements.txt)**
- **No unit tests required**

### Docker Containerization

- Separate Dockerfile for C# API
- Separate Dockerfile for Python API
- C# container includes built React frontend
- Python container uses `uv` for fast dependency installation
- Python container includes FastAPI and Semantic Kernel dependencies
- Use multi-stage builds for optimization

### Infrastructure as Code (Terraform)

- Use Terraform for all Azure infrastructure
- Deploy to Azure Container Apps
- Provision separate container apps for C# and Python services
- Configure Azure AI Foundry resources for the agent
- Set up networking, environment variables, and secrets
- Include container registry configuration

### Azure Resources

- Azure Container Apps for C# API
- Azure Container Apps for Python API
- Azure AI Foundry for Chat Completion Agent
- Azure Container Registry for Docker images
- Appropriate networking and security configurations

## Code Organization

- `/src/frontend` - React application
- `/src/backend` - C# .NET 8 API
- `/src/ai-service` - Python Semantic Kernel API
- `/infra` - Terraform configurations

## Important Notes

- **No unit tests** are needed for this project
- **Always use `uv` for Python** package management and execution
- Focus on streaming capabilities throughout the stack
- Ensure proper error handling in the request chain
- Configure CORS appropriately between services
- Use environment variables for configuration (API endpoints, Azure credentials)
