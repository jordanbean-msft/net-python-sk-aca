#!/bin/bash
set -e

# Deployment script for building and pushing container images to ACR
# Run this after deploying infrastructure with Terraform

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Container Image Build and Deploy Script${NC}"
echo "=========================================="

# Check if terraform has been applied
if [ ! -f "terraform.tfstate" ]; then
    echo -e "${RED}Error: terraform.tfstate not found. Please run 'terraform apply' first.${NC}"
    exit 1
fi

# Get ACR name and login server from Terraform outputs
echo -e "${YELLOW}Retrieving ACR details from Terraform...${NC}"
ACR_NAME=$(terraform output -raw acr_name 2>/dev/null)
ACR_LOGIN_SERVER=$(terraform output -raw acr_login_server 2>/dev/null)

if [ -z "$ACR_NAME" ] || [ -z "$ACR_LOGIN_SERVER" ]; then
    echo -e "${RED}Error: Could not retrieve ACR details from Terraform outputs.${NC}"
    exit 1
fi

echo "ACR Name: $ACR_NAME"
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Login to ACR
echo -e "${YELLOW}Logging in to ACR...${NC}"
az acr login --name "$ACR_NAME"

# Change to project root
cd ..

# Build and push Backend image
echo -e "${GREEN}Building Backend image...${NC}"
docker buildx build --platform linux/amd64 \
  -t "$ACR_LOGIN_SERVER/backend:latest" \
  -f src/backend/Dockerfile \
  --build-arg BUILD_ENV=production \
  --build-arg PORT=8080 \
  src

echo -e "${GREEN}Pushing Backend image...${NC}"
docker push "$ACR_LOGIN_SERVER/backend:latest"

# Build and push AI Service image
echo -e "${GREEN}Building AI Service image...${NC}"
docker buildx build --platform linux/amd64 \
  -t "$ACR_LOGIN_SERVER/ai-service:latest" \
  -f src/ai-service/Dockerfile \
  --build-arg PORT=8000 \
  src/ai-service

echo -e "${GREEN}Pushing AI Service image...${NC}"
docker push "$ACR_LOGIN_SERVER/ai-service:latest"

# Build and push Weather Function image
echo -e "${GREEN}Building Weather Function image...${NC}"
docker buildx build --platform linux/amd64 \
  -t "$ACR_LOGIN_SERVER/weather-function:latest" \
  -f src/weather-function/Dockerfile \
  src/weather-function

echo -e "${GREEN}Pushing Weather Function image...${NC}"
docker push "$ACR_LOGIN_SERVER/weather-function:latest"

echo ""
echo -e "${GREEN}All images built and pushed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Update terraform.tfvars with the following image names:"
echo "   backend_image          = \"$ACR_LOGIN_SERVER/backend:latest\""
echo "   ai_service_image       = \"$ACR_LOGIN_SERVER/ai-service:latest\""
echo "   weather_function_image = \"$ACR_LOGIN_SERVER/weather-function:latest\""
echo ""
echo "2. Run 'terraform apply' to update the container apps with the new images"
echo ""
echo "3. Get the application URL with:"
echo "   terraform output backend_url"
