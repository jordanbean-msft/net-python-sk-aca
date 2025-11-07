# Build Notes

## Local Development (ARM64)

For local testing on ARM64 machines, build images for native architecture:

```bash
docker-compose up --build
```

## Azure Deployment (AMD64)

Azure Container Apps runs on AMD64 architecture. Build images in Azure Container Registry using ACR Tasks:

```bash
# Build backend for AMD64
az acr build --registry <your-acr-name> \
  --platform linux/amd64 \
  --image backend:latest \
  ./src/backend

# Build ai-service for AMD64
az acr build --registry <your-acr-name> \
  --platform linux/amd64 \
  --image ai-service:latest \
  ./src/ai-service
```

**Do not** add `--platform=linux/amd64` to Dockerfiles - this causes QEMU emulation issues on ARM64 development machines. Instead, specify the platform during the build command in CI/CD or ACR tasks.
