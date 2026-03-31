from __future__ import annotations

import importlib
from typing import Any, Optional

from google.adk.features import FeatureName, is_feature_enabled
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


class LazyAgentTool(BaseTool):
    """A tool that defers agent module import until first invocation.

    Instead of importing the agent at startup (which triggers the entire
    sub-agent tree to load), the module is only imported when run_async()
    is first called — i.e., when the LLM actually routes a request to it.

    _get_declaration() is built from the stored name/description without
    needing the agent instance, since all pillar agents use the simple
    request: str input schema (no input_schema / output_schema set).
    """

    def __init__(
        self,
        *,
        module_path: str,
        agent_attr: str,
        name: str,
        description: str,
        skip_summarization: bool = False,
    ):
        super().__init__(name=name, description=description)
        self._module_path = module_path
        self._agent_attr = agent_attr
        self._skip_summarization = skip_summarization
        self._agent_tool: Optional[Any] = None  # AgentTool, resolved on first use

    def _resolve(self) -> Any:
        """Import the module and build the real AgentTool on first call."""
        if self._agent_tool is None:
            from google.adk.tools import AgentTool
            mod = importlib.import_module(self._module_path)
            agent = getattr(mod, self._agent_attr)
            self._agent_tool = AgentTool(
                agent=agent,
                skip_summarization=self._skip_summarization,
            )
        return self._agent_tool

    def warm_up(self) -> None:
        """Pre-import this tool's agent module (non-recursive).

        Safe to call from a background thread — importlib's import lock serialises
        concurrent imports, and writing self._agent_tool is idempotent.
        """
        self._resolve()

    def get_sub_tools(self) -> "list[LazyAgentTool]":
        """Return unresolved LazyAgentTool children of this tool's agent.

        Only valid after warm_up() has been called.
        """
        agent = getattr(self._agent_tool, "agent", None)
        if agent is None:
            return []
        return [
            t for t in (getattr(agent, "tools", None) or [])
            if isinstance(t, LazyAgentTool) and t._agent_tool is None
        ]

    def _get_declaration(self) -> types.FunctionDeclaration:
        """Build the function declaration from stored name/description.

        All pillar agents use the default request: str schema (no input_schema),
        so we can construct the declaration without importing the agent.
        """
        if is_feature_enabled(FeatureName.JSON_SCHEMA_FOR_FUNC_DECL):
            return types.FunctionDeclaration(
                name=self.name,
                description=self.description,
                parameters_json_schema={
                    "type": "object",
                    "properties": {"request": {"type": "string"}},
                    "required": ["request"],
                },
            )
        return types.FunctionDeclaration(
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={"request": types.Schema(type=types.Type.STRING)},
                required=["request"],
            ),
            description=self.description,
            name=self.name,
        )

    async def run_async(
        self,
        *,
        args: dict[str, Any],
        tool_context: ToolContext,
    ) -> Any:
        """Lazily import the agent module and delegate execution."""
        if self._agent_tool is None:
            from ._spinner import spinner
            spinner.println(
                f"Loading {self.name} for the first time in this session, may take some time..."
            )
        return await self._resolve().run_async(args=args, tool_context=tool_context)
