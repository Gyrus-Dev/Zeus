from google.adk.tools import ToolContext


def save_research_results(object_type: str, results: str, tool_context: ToolContext) -> dict:
    """Save research results to session state."""
    try:
        key = object_type.strip().upper()
        research = tool_context.state.get("app:RESEARCH_RESULTS") or {}
        research[key] = results
        tool_context.state["app:RESEARCH_RESULTS"] = research
        return {"success": True, "object_type": key, "message": f"Research results saved for {key}."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def web_search(query: str) -> dict:
    """Search DuckDuckGo for SQL Server / T-SQL information."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        formatted = "\n\n".join(
            f"**{r.get('title', '')}**\n{r.get('body', '')}\nURL: {r.get('href', '')}"
            for r in results
        )
        return {"success": True, "results": formatted}
    except Exception as e:
        return {"success": False, "results": "", "error": str(e)}
