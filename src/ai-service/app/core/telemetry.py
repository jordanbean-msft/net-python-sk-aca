"""Telemetry configuration for Application Insights."""

import logging

from azure.monitor.opentelemetry.exporter import (AzureMonitorLogExporter,
                                                  AzureMonitorMetricExporter,
                                                  AzureMonitorTraceExporter)
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider

from .config import settings


def setup_telemetry():
    """Configure Application Insights telemetry."""
    if not settings.applicationinsights_connection_string:
        logging.info(
            "Application Insights not configured, skipping telemetry setup"
        )
        return

    connection_string = settings.applicationinsights_connection_string

    # Create resource
    resource = Resource.create(
        {ResourceAttributes.SERVICE_NAME: settings.app_name}
    )

    # Setup logging
    log_exporter = AzureMonitorLogExporter(
        connection_string=connection_string
    )
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter)
    )
    set_logger_provider(logger_provider)

    handler = LoggingHandler()
    handler.addFilter(logging.Filter("semantic_kernel"))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Setup tracing
    trace_exporter = AzureMonitorTraceExporter(
        connection_string=connection_string
    )
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(trace_exporter)
    )
    set_tracer_provider(tracer_provider)

    # Setup metrics
    metric_exporter = AzureMonitorMetricExporter(
        connection_string=connection_string
    )
    meter_provider = MeterProvider(
        metric_readers=[
            PeriodicExportingMetricReader(
                metric_exporter, export_interval_millis=5000
            )
        ],
        resource=resource,
        views=[
            View(instrument_name="*", aggregation=DropAggregation()),
            View(instrument_name="semantic_kernel*"),
        ],
    )
    set_meter_provider(meter_provider)

    logging.info(
        "Application Insights telemetry configured successfully"
    )
