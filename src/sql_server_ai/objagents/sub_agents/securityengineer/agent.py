from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from .rowlevelsecurity.prompt import AGENT_NAME as _RLS_NAME, DESCRIPTION as _RLS_DESC
from .columnpermission.prompt import AGENT_NAME as _COL_NAME, DESCRIPTION as _COL_DESC

_BASE = "src.sql_server_ai.objagents.sub_agents.securityengineer"

ag_pg_security_engineer = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    planner=cfg.get_planner(512),
    tools=[
        LazyAgentTool(module_path=f"{_BASE}.rowlevelsecurity.agent", agent_attr="ag_pg_manage_rls", name=_RLS_NAME, description=_RLS_DESC),
        LazyAgentTool(module_path=f"{_BASE}.columnpermission.agent", agent_attr="ag_pg_manage_column_permission", name=_COL_NAME, description=_COL_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
