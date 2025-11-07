# Backend API (.NET 8 C# MVC)

This is the backend REST API that serves as a gateway between the React frontend and the Python Semantic Kernel AI service.

## Features

- **Chat API**: Proxies chat requests to the Python API with streaming support
- **Health Check**: `/health` endpoint for monitoring
- **Static File Serving**: Serves the React frontend from `wwwroot`
- **CORS Support**: Configured for cross-origin requests
- **Swagger**: API documentation available in development mode

## Project Structure

```
src/backend/
├── Controllers/
│   ├── ChatController.cs      # Chat endpoint with streaming
│   └── HealthController.cs    # Health check endpoint
├── Models/
│   ├── ChatMessage.cs         # Individual chat message
│   ├── ChatHistoryModel.cs    # Chat history container
│   ├── ChatRequest.cs         # Request model
│   ├── ChatResponse.cs        # Response model
│   └── MessageRole.cs         # Message role enum
├── wwwroot/                   # Static files (React app)
│   └── index.html            # Entry point for React app
├── Backend.csproj            # Project file
├── Program.cs                # Application entry point
├── appsettings.json          # Configuration
└── Dockerfile                # Container image definition
```

## Running Locally

### Prerequisites

- .NET 8 SDK
- Python AI service running on `http://localhost:8000`

### Run the API

```bash
cd src/backend
dotnet restore
dotnet run
```

The API will be available at:

- HTTP: `http://localhost:5000`
- HTTPS: `https://localhost:5001`

### Configuration

Configure the Python API URL in `appsettings.json` or via environment variable:

```json
{
  "PythonApiUrl": "http://localhost:8000"
}
```

Or set environment variable:

```bash
export PythonApiUrl="http://localhost:8000"
```

## API Endpoints

### Chat

- **POST** `/api/chat`
- Streams responses from the Python AI service
- Request body:
  ```json
  {
    "message": "Hello!",
    "history": {
      "messages": []
    },
    "stream": true
  }
  ```

### Health Check

- **GET** `/api/health`
- Returns service health status

## Docker

Build and run the container:

```bash
docker build -t backend-api .
docker run -p 8080:8080 -e PythonApiUrl=http://ai-service:8000 backend-api
```

## Development

### Add React Build Output

When you build the React app in `/src/frontend`, copy the build output to `wwwroot/`:

```bash
# After building React app
cp -r ../frontend/build/* wwwroot/
```

The backend will serve the React app at the root URL and handle API requests at `/api/*`.
