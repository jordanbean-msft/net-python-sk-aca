# Node build stage for React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /frontend

# Copy package.json first for better caching
COPY frontend/package.json ./

# Install dependencies (will be cached if package.json hasn't changed)
RUN npm install react-scripts

# Copy frontend source (only invalidates cache if source changes)
COPY frontend/public ./public
COPY frontend/src ./src

# Build React app
RUN npm run build

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Copy pre-built backend app
COPY backend/publish/ .

# Copy React build from frontend stage
COPY --from=frontend-build /frontend/build ./wwwroot

# Expose port
EXPOSE 8080

# Set environment variables
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production

# Run the app
ENTRYPOINT ["dotnet", "Backend.dll"]
