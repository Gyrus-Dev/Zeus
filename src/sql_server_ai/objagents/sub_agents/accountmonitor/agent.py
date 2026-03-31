from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from .querystats.prompt import AGENT_NAME as _QS_NAME, DESCRIPTION as _QS_DESC
from .tablestats.prompt import AGENT_NAME as _TS_NAME, DESCRIPTION as _TS_DESC
from .connectionmonitor.prompt import AGENT_NAME as _CM_NAME, DESCRIPTION as _CM_DESC

_BASE = "src.sql_server_ai.objagents.sub_agents.accountmonitor"

ag_pg_account_monitor = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    planner=cfg.get_planner(512),
    tools=[
        LazyAgentTool(module_path=f"{_BASE}.querystats.agent", agent_attr="ag_pg_query_stats", name=_QS_NAME, description=_QS_DESC),
        LazyAgentTool(module_path=f"{_BASE}.tablestats.agent", agent_attr="ag_pg_table_stats", name=_TS_NAME, description=_TS_DESC),
        LazyAgentTool(module_path=f"{_BASE}.connectionmonitor.agent", agent_attr="ag_pg_connection_monitor", name=_CM_NAME, description=_CM_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
