# Application Insights Integration

The AI service is configured to send telemetry (logs, metrics, and traces) to Azure Application Insights for observability.

## Configuration

To enable Application Insights telemetry, set the following environment variable in your `.env` file:

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.applicationinsights.azure.com/
```

You can find the connection string in your Application Insights resource in the Azure Portal.

## What Gets Tracked

With Application Insights enabled, the following telemetry is automatically collected:

### Logs

- Semantic Kernel logs and events
- AI connector logs
- Function execution logs

### Traces

- Distributed traces across the entire request flow
- AI model calls with request/response details
- Function invocations
- Plugin/tool executions

### Metrics

- `semantic_kernel.function.invocation.duration` - Function execution time
- `semantic_kernel.function.streaming.duration` - Streaming execution time
- Token consumption metrics
- Custom metrics from the application

## Viewing Telemetry

After running your application:

1. Navigate to your Application Insights resource in the Azure Portal
2. Go to **Transaction search** to view individual traces
3. Use **Logs** for querying telemetry data with KQL
4. Check **Metrics** for performance monitoring

## Local Development

If `APPLICATIONINSIGHTS_CONNECTION_STRING` is not set, the application will run normally without sending telemetry to Application Insights. This is useful for local development.

## Sensitive Data

The telemetry setup does NOT log sensitive data like prompts and completions by default. To enable sensitive data logging (for debugging only), you would need to modify the telemetry configuration in `app/core/telemetry.py`.

## Learn More

- [Semantic Kernel Observability](https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/observability/)
- [Azure Monitor Application Insights](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [OpenTelemetry in Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable)
