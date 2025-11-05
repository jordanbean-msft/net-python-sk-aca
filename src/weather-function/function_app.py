import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for container readiness probes.
    """
    logging.info('Health check endpoint called')

    health_data = {
        "status": "healthy",
        "service": "Weather Function"
    }

    return func.HttpResponse(
        body=json.dumps(health_data),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="weather")
def get_weather(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that returns hardcoded weather data.
    This is called by the Semantic Kernel AI agent as a tool.

    Query parameters:
    - location: The location to get weather for (optional)
    """
    logging.info('Weather function triggered by request')

    # Get location from query parameters or use default
    location = req.params.get('location', 'Seattle')

    logging.info('Processing weather request for location: %s', location)

    # Hardcoded weather data
    weather_data = {
        "location": location,
        "temperature": 72,
        "temperature_unit": "F",
        "conditions": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 8,
        "wind_unit": "mph",
        "forecast": "Clear skies expected for the rest of the day"
    }

    logging.info('Returning weather data for location: %s', location)

    return func.HttpResponse(
        body=json.dumps(weather_data),
        status_code=200,
        mimetype="application/json"
    )
