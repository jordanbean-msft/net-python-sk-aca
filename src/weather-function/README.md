# Weather Function

Azure Function that provides hardcoded weather data for the AI agent to use as a tool.

## Local Development

### Using Docker Compose

The function runs automatically as part of the docker-compose stack:

```bash
docker-compose up -d
```

The function will be available at: `http://localhost:7071`

### Manual Testing

Test the weather endpoint:

```bash
curl "http://localhost:7071/api/weather?location=Seattle"
```

Expected response:

```json
{
  "location": "Seattle",
  "temperature": 72,
  "temperature_unit": "F",
  "conditions": "Partly Cloudy",
  "humidity": 65,
  "wind_speed": 8,
  "wind_unit": "mph",
  "forecast": "Clear skies expected for the rest of the day"
}
```

## How It Works

1. The Azure Function exposes an HTTP endpoint at `/api/weather`
2. The Semantic Kernel AI agent registers this as a tool/function
3. When users ask about weather, the AI agent can call this function
4. The function returns hardcoded weather data in JSON format

## Deployment

The function is deployed to Azure Functions (containerized) as part of the infrastructure.
The Dockerfile uses the official Azure Functions Python base image: `mcr.microsoft.com/azure-functions/python:4-python3.12`
