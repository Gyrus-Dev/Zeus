from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from .user.prompt import AGENT_NAME as _USR_NAME, DESCRIPTION as _USR_DESC
from .role.prompt import AGENT_NAME as _ROLE_NAME, DESCRIPTION as _ROLE_DESC
from .grant.prompt import AGENT_NAME as _GRANT_NAME, DESCRIPTION as _GRANT_DESC

_BASE = "src.sql_server_ai.objagents.sub_agents.administrator"

ag_pg_administrator = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    planner=cfg.get_planner(512),
    tools=[
        LazyAgentTool(module_path=f"{_BASE}.user.agent", agent_attr="ag_pg_manage_user", name=_USR_NAME, description=_USR_DESC),
        LazyAgentTool(module_path=f"{_BASE}.role.agent", agent_attr="ag_pg_manage_role", name=_ROLE_NAME, description=_ROLE_DESC),
        LazyAgentTool(module_path=f"{_BASE}.grant.agent", agent_attr="ag_pg_manage_grant", name=_GRANT_NAME, description=_GRANT_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
