"""Logging callbacks for pillar sub-agents.

When pillar agents are invoked via ``AgentTool``, the ADK creates an
internal Runner that consumes all sub-agent events — they never surface
to the parent runner's event stream.  These callbacks are attached to
each pillar agent so that their activity is reflected in the shared
terminal spinner rather than flooding the console with raw LLM output.
"""

import logging
from src.sql_server_ai.objagents._spinner import spinner
from src.sql_server_ai.telemetry import tracer, agent_invocations

logger = logging.getLogger(__name__)

# Stores in-flight spans keyed by agent name.
# Safe without locks — postgresai enforces sequential (non-parallel) agent execution.
_active_agent_spans: dict = {}


def before_model_callback(callback_context, llm_request):
    """Update the spinner to show which agent is now processing a request."""
    agent_name = getattr(
        getattr(callback_context, "_invocation_context", None),
        "agent",
        None,
    )
    agent_name = getattr(agent_name, "name", "unknown_agent")

    if llm_request.contents:
        last_content = llm_request.contents[-1]
        if last_content.role == "user" and last_content.parts:
            request_text = " ".join(
                p.text for p in last_content.parts if p.text
            )
            if request_text:
                logger.info(
                    "[%s] Received request: %s",
                    agent_name,
                    request_text[:500],
                )

    agent_invocations.add(1, {"agent": agent_name})
    span = tracer.start_span(f"agent.{agent_name}")
    span.set_attribute("agent.name", agent_name)
    _active_agent_spans[agent_name] = span

    if spinner.is_running:
        spinner.set_label(f"[{agent_name}]")
    else:
        spinner.start(f"[{agent_name}]")

    return None


def after_model_callback(callback_context, llm_response):
    """Log the pillar agent's model response; suppress terminal noise."""
    agent_name = getattr(
        getattr(callback_context, "_invocation_context", None),
        "agent",
        None,
    )
    agent_name = getattr(agent_name, "name", "unknown_agent")

    if not llm_response or not llm_response.content:
        return None

    content = llm_response.content
    if not content.parts:
        return None

    for part in content.parts:
        if part.thought and part.text:
            logger.info("[%s] Thinking: %s", agent_name, part.text[:500])
        elif part.text:
            logger.info("[%s] Response: %s", agent_name, part.text)
        if part.function_call:
            logger.info(
                "[%s] Tool call: %s args=%s",
                agent_name,
                part.function_call.name,
                str(part.function_call.args)[:200],
            )

    span = _active_agent_spans.pop(agent_name, None)
    if span is not None:
        if llm_response.error_message:
            from opentelemetry import trace as _t
            span.set_status(_t.StatusCode.ERROR, llm_response.error_message)
        span.end()

    return None


def before_tool_callback(tool, args, tool_context):
    """Update the spinner to show the tool being called."""
    agent_name = getattr(
        getattr(tool_context, "_invocation_context", None),
        "agent",
        None,
    )
    agent_name = getattr(agent_name, "name", "unknown_agent")
    tool_name = getattr(tool, "name", str(tool))

    logger.info(
        "[%s] Before tool: %s args=%s",
        agent_name,
        tool_name,
        str(args)[:500],
    )
    spinner.set_label(f"[{agent_name} → {tool_name}]")
    return None
