# Use the official Azure Functions Python 3.12 base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.12

# Install curl for health checks
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl && \
  rm -rf /var/lib/apt/lists/*

# Set default port (Azure Functions default is 80)
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
  AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Copy function code to the function app directory
COPY . /home/site/wwwroot

# Install dependencies using pip (Azure Functions images don't include uv by default)
RUN cd /home/site/wwwroot && \
  pip install --no-cache-dir -r requirements.txt
