from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...database.prompt import AGENT_NAME as _DB_NAME, DESCRIPTION as _DB_DESC
from ...schema.prompt import AGENT_NAME as _SCH_NAME, DESCRIPTION as _SCH_DESC
from ...extension.prompt import AGENT_NAME as _EXT_NAME, DESCRIPTION as _EXT_DESC
from ...tablespace.prompt import AGENT_NAME as _TS_NAME, DESCRIPTION as _TS_DESC
from ...collation.prompt import AGENT_NAME as _COL_NAME, DESCRIPTION as _COL_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_infrastructure_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.database.agent", agent_attr="ag_pg_manage_database", name=_DB_NAME, description=_DB_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.schema.agent", agent_attr="ag_pg_manage_schema", name=_SCH_NAME, description=_SCH_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.extension.agent", agent_attr="ag_pg_manage_extension", name=_EXT_NAME, description=_EXT_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.tablespace.agent", agent_attr="ag_pg_manage_tablespace", name=_TS_NAME, description=_TS_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.collation.agent", agent_attr="ag_pg_manage_collation", name=_COL_NAME, description=_COL_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
