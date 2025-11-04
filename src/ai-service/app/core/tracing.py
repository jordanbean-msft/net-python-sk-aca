"""OpenTelemetry tracing configuration."""

import os

from .config import settings


def setup_tracing():
    """Configure OpenTelemetry tracing if enabled."""
    if not settings.enable_tracing:
        return

    os.environ["AZURE_SDK_TRACING_IMPLEMENTATION"] = "opentelemetry"

    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
        OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource(attributes={"service.name": settings.app_name})
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint)
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
