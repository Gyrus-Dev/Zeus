"""
OpenTelemetry instrumentation for ZeusAI.

Controlled by OTEL_ENABLED in .env (default: false).
Setup runs at import time so tracer/meter objects are live by the time
any instrumented module uses them.
"""

import os
import urllib.parse
import logging
import warnings

# opentelemetry-instrumentation-logging uses the pre-1.35.0 LogRecord API.
# Suppress the resulting DeprecationWarning — it's a third-party package issue
# and the functionality is unaffected.
warnings.filterwarnings(
    "ignore",
    message="LogRecord init with.*is deprecated",
)

logger = logging.getLogger(__name__)

OTEL_ENABLED = os.getenv("OTEL_ENABLED", "false").lower() == "true"

try:
    from opentelemetry import trace as _trace_api, metrics as _metrics_api
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False
    OTEL_ENABLED = False
    logger.debug("[telemetry] opentelemetry packages not installed — telemetry disabled")


def _parse_headers(raw: str) -> dict:
    """Parse 'Key=Value,Key2=Value2' header string (URL-encoded values supported)."""
    headers: dict = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            headers[k.strip()] = urllib.parse.unquote(v.strip())
    return headers


def _setup_providers() -> None:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.resources import Resource

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").rstrip("/")
    headers  = _parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""))
    service  = os.getenv("OTEL_SERVICE_NAME", "zeusai")
    resource = Resource.create({"service.name": service})

    # Traces → Grafana Tempo
    tp = TracerProvider(resource=resource)
    tp.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers)
    ))
    trace.set_tracer_provider(tp)

    # Metrics → Grafana Mimir
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics", headers=headers)
    )
    metrics.set_meter_provider(MeterProvider(metric_readers=[reader], resource=resource))

    logger.info("[telemetry] OpenTelemetry enabled — exporting to %s as service '%s'", endpoint, service)


# Run setup at import time if enabled so tracer/meter are live before use.
if OTEL_ENABLED and _OTEL_AVAILABLE:
    try:
        _setup_providers()
    except Exception as exc:
        logger.warning("[telemetry] Setup failed, falling back to no-ops: %s", exc)
        OTEL_ENABLED = False


# --- Public API ---
# Always importable. No-ops when OTEL_ENABLED=false (OTel API returns no-op objects
# when no provider is registered, so there is zero overhead in the disabled path).

if _OTEL_AVAILABLE:
    tracer = _trace_api.get_tracer("zeusai")
    _meter  = _metrics_api.get_meter("zeusai")
    query_counter     = _meter.create_counter("zeusai.queries.total",       description="SQL Server queries executed")
    query_errors      = _meter.create_counter("zeusai.queries.errors",      description="Failed SQL Server queries")
    agent_invocations = _meter.create_counter("zeusai.agent.invocations",   description="Agent model calls")
    query_latency     = _meter.create_histogram("zeusai.query.duration_ms", description="Query execution time in ms")
else:
    # Stub objects so imports never break even if the package is absent.
    class _Noop:
        def start_as_current_span(self, *a, **kw):
            from contextlib import contextmanager
            @contextmanager
            def _noop(*_, **__): yield self
            return _noop()
        def add(self, *a, **kw): pass
        def record(self, *a, **kw): pass

    tracer = _Noop()
    query_counter = query_errors = agent_invocations = query_latency = _Noop()


def shutdown() -> None:
    """Flush all pending spans/metrics before process exit. Call on graceful shutdown."""
    if not OTEL_ENABLED or not _OTEL_AVAILABLE:
        return
    try:
        from opentelemetry import trace, metrics
        tp = trace.get_tracer_provider()
        if hasattr(tp, "shutdown"):
            tp.shutdown()
        mp = metrics.get_meter_provider()
        if hasattr(mp, "shutdown"):
            mp.shutdown()
    except Exception as exc:
        logger.debug("[telemetry] shutdown error: %s", exc)
