# backend/app/services/telemetry/__init__.py

"""
Telemetry module for ORKO.
Provides unified cross-system observability:
parser → mapper → trigger → workflow.
"""

from .telemetry_collector import TelemetryCollector

__all__ = ["TelemetryCollector"]
