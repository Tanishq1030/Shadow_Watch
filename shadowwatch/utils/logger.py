"""
Shadow Watch Structured Logger

Standardized logging for SIEM integration. 
Supports JSON output for production and colorized output for development.
"""
import logging
import sys
import os
import structlog

def setup_logger(name="shadowwatch"):
    """
    Configure structlog for SIEM-compatible JSON output.
    Toggle via SHADOWWATCH_LOG_FORMAT environment variable.
    """
    log_format = os.getenv("SHADOWWATCH_LOG_FORMAT", "text").lower()
    log_level = os.getenv("SHADOWWATCH_LOG_LEVEL", "INFO").upper()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(name)

# Default logger instance
logger = setup_logger()
