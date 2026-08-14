"""Shared observability utilities for tracing and logging in SCOF."""

import os
from typing import Dict, Any, Optional

def configure_langsmith(project_name: str = "scof-d7"):
    """Enable LangSmith tracing by setting environment variables."""
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if "LANGCHAIN_PROJECT" not in os.environ:
        os.environ["LANGCHAIN_PROJECT"] = project_name

def create_trace_tags(
    scenario_id: str,
    bundle_id: str,
    trace_id: str,
    profile_version: str,
    agent_id: Optional[str] = None,
    decision_id: Optional[str] = None
) -> list[str]:
    """
    Generate LangSmith tags for execution tracing to maintain provenance.
    """
    tags = [
        f"scenario_id:{scenario_id}",
        f"bundle_id:{bundle_id}",
        f"trace_id:{trace_id}",
        f"profile_version:{profile_version}"
    ]
    if agent_id:
        tags.append(f"agent_id:{agent_id}")
    if decision_id:
        tags.append(f"decision_id:{decision_id}")
    return tags

def create_runnable_config(
    scenario_id: str,
    bundle_id: str,
    trace_id: str,
    profile_version: str,
    agent_id: Optional[str] = None,
    decision_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a RunnableConfig dictionary for LangGraph/LangChain invocation
    with appropriate tags and metadata.
    """
    tags = create_trace_tags(
        scenario_id=scenario_id,
        bundle_id=bundle_id,
        trace_id=trace_id,
        profile_version=profile_version,
        agent_id=agent_id,
        decision_id=decision_id
    )
    config: Dict[str, Any] = {"tags": tags}
    if metadata:
        config["metadata"] = metadata
    return config
