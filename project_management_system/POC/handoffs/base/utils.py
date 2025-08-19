"""
Utility functions for the handoffs pattern.

This module contains common utility functions used across the handoffs system.
"""

import logging
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_logging():
    """
    Setup logging configuration for the handoffs pattern.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.parent
    log_file = script_dir / "handoff.log"
    
    # Remove existing log file to reset it at each run
    if log_file.exists():
        log_file.unlink()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=' - - - %(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            #logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized for handoffs pattern")
    return logger





def configure_oltp_tracing(endpoint: str = None) -> trace.TracerProvider:
    
    otel_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    span_processor = BatchSpanProcessor(otel_exporter)
    
    # Configure Tracing
    tracer_provider = TracerProvider(resource=Resource({"service.name": "autogen-handoffs"}))
    processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)
    
    # Instrument the OpenAI Python library
    OpenAIInstrumentor().instrument()   

    return tracer_provider