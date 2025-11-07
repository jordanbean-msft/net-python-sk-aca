"""Weather plugin for Semantic Kernel - calls Azure Function."""

import logging
import os
from typing import Annotated

import httpx
from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class WeatherPlugin:
    """Plugin to get weather information from Azure Function."""

    def __init__(self):
        """Initialize the weather plugin."""
        # Get the Azure Function URL from environment variable
        self.weather_function_url = os.getenv(
            "WeatherFunctionUrl", "http://localhost:7071"
        )
        self.weather_endpoint = f"{self.weather_function_url}/api/weather"

    @kernel_function(
        name="get_weather",
        description="Get the current weather for a given location",
    )
    async def get_weather(
        self,
        location: Annotated[
            str, "The location to get weather for"
        ] = "Seattle",
    ) -> Annotated[str, "Weather information in JSON format"]:
        """
        Get weather information for a location by calling Azure Function.

        Args:
            location: The location to get weather for

        Returns:
            JSON string with weather data
        """
        logger.info(
            "Weather plugin called: fetching weather for location='%s'",
            location
        )
        logger.debug("Calling Azure Function at: %s", self.weather_endpoint)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.weather_endpoint,
                params={"location": location},
                timeout=10.0,
            )
            response.raise_for_status()

            logger.info(
                "Weather function responded: status=%d, location='%s'",
                response.status_code,
                location
            )
            logger.debug("Weather response: %s", response.text)

            return response.text
