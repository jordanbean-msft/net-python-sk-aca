# Build argument to control build strategy
ARG BUILD_ENV=production

# Node build stage for React frontend
FROM node:18-alpine AS frontend-build
ARG BUILD_ENV
WORKDIR /frontend

# Copy package.json first for better caching
COPY frontend/package.json ./

# Install dependencies (will be cached if package.json hasn't changed)
RUN npm install react-scripts

# Copy frontend source (only invalidates cache if source changes)
COPY frontend/public ./public
COPY frontend/src ./src

# Build React app with conditional optimization
RUN if [ "$BUILD_ENV" = "development" ]; then \
  export GENERATE_SOURCEMAP=false && \
  export INLINE_RUNTIME_CHUNK=false && \
  export CI=true && \
  npm run build; \
  else \
  npm run build; \
  fi

## Backend build stage (dotnet publish inside container) - only for production
# Multi-arch .NET SDK image (arm64/x64). Actual arch selected by Docker platform settings.
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS backend-build
ARG BUILD_ENV
WORKDIR /src
COPY backend/*.csproj ./
RUN if [ "$BUILD_ENV" = "production" ]; then \
  dotnet restore Backend.csproj; \
  fi
COPY backend/ ./
RUN if [ "$BUILD_ENV" = "production" ]; then \
  dotnet publish Backend.csproj -c Release -o /src/publish; \
  fi

# Development runtime stage - SDK for local development
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS development
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl && \
  rm -rf /var/lib/apt/lists/*

# Copy React build from frontend stage
COPY --from=frontend-build /frontend/build ./wwwroot

# Copy backend source (for development, we'll use dotnet run)
COPY backend/ ./

# Expose port (configurable via PORT environment variable)
ARG PORT=8080
EXPOSE ${PORT}

# Set environment variables
ENV ASPNETCORE_URLS=http://+:${PORT}
ENV PORT=${PORT}

# Run with dotnet run for development (watches for changes if configured)
CMD ["dotnet", "run", "--no-launch-profile"]

# Production runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS production
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl && \
  rm -rf /var/lib/apt/lists/*

# Copy published backend from build stage
COPY --from=backend-build /src/publish/ .

# Copy React build from frontend stage
COPY --from=frontend-build /frontend/build ./wwwroot

# Expose port (configurable via PORT environment variable)
ARG PORT=8080
EXPOSE ${PORT}

# Set environment variables
ENV ASPNETCORE_URLS=http://+:${PORT}
ENV ASPNETCORE_ENVIRONMENT=Production
ENV PORT=${PORT}

# Run the app
ENTRYPOINT ["dotnet", "Backend.dll"]
