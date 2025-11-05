# Node build stage for React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /frontend

# Build argument to control optimization
ARG BUILD_ENV=production

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

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
  apt-get install -y --no-install-recommends curl && \
  rm -rf /var/lib/apt/lists/*

# Copy pre-built backend app
COPY backend/publish/ .

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
