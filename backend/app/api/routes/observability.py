from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List

from app.services.observability.tracker import observability_tracker

router = APIRouter()

@router.get("/trace/{workspace_id}")
async def get_workspace_trace(workspace_id: str):
    """
    Returns OpenTelemetry / Langfuse-compatible trace for a budget workspace.
    Includes agent latency waterfall, prompt/completion tokens, cost in USD, and reconciliation audits.
    """
    trace = observability_tracker.get_latest_trace_for_workspace(workspace_id)
    if not trace:
        trace = observability_tracker.generate_default_demo_trace(workspace_id)
    return trace

@router.get("/metrics")
async def get_system_observability_metrics():
    """Returns global system performance, aggregate token usage, and latency statistics."""
    return observability_tracker.get_system_summary()

@router.get("/traces")
async def list_all_traces():
    """Returns all recorded execution traces for performance evaluation and auditability."""
    traces = observability_tracker.get_all_traces()
    if not traces:
        traces = [observability_tracker.generate_default_demo_trace()]
    return {"traces": traces, "total": len(traces)}
