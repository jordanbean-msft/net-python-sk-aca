# Testing the AI Service

## Prerequisites

1. **VS Code REST Client Extension**: Install the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension
2. **Environment File**: Ensure `.env` file is configured with Azure AI credentials:

```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_AI_MODEL_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_KEY=your-api-key-here  # Required for local testing
```

3. **Docker**: Docker must be installed and running

## Running the Service

### Build the Docker Image

```bash
cd src/ai-service
docker build -t ai-service:latest .
```

### Start the Container

```bash
docker run -d --name ai-service -p 8000:8000 --env-file .env ai-service:latest
```

### Check Container Status

```bash
docker ps | grep ai-service
docker logs ai-service
```

### Stop the Container

```bash
docker stop ai-service
docker rm ai-service
```

## Using test.http

1. Open `test.http` in VS Code
2. Click "Send Request" above any request (or use `Ctrl+Alt+R` / `Cmd+Alt+R`)
3. The response will appear in a new panel

## Available Test Requests

- **Health Check**: GET /health - Verify service is running
- **Root Endpoint**: GET / - View available endpoints
- **Simple Chat**: POST /chat - Non-streaming chat without history
- **Chat with History**: POST /chat - Continue a conversation
- **Streaming Chat**: POST /chat/stream - Real-time streaming responses
- **Streaming with History**: POST /chat/stream - Stream with conversation context

## Example Request/Response

### Request (Non-streaming with history)

```http
POST http://localhost:8000/chat
Content-Type: application/json

{
  "message": "What did I just ask you?",
  "history": {
    "messages": [
      {
        "role": "user",
        "content": "What is the capital of France?"
      },
      {
        "role": "assistant",
        "content": "The capital of France is Paris."
      }
    ]
  },
  "stream": false
}
```

### Response

```json
{
  "response": "You just asked me 'What is the capital of France?'",
  "history": {
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI assistant..."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      },
      {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      {
        "role": "user",
        "content": "What did I just ask you?"
      },
      {
        "role": "assistant",
        "content": "You just asked me 'What is the capital of France?'"
      }
    ]
  }
}
```

## Tips

- Use the **history** field to maintain conversation context across requests
- Set **stream: true** for real-time responses (useful for long answers)
- The **history** in the response includes the updated conversation for the next request
- System messages are automatically added if not present in history
