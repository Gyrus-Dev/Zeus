from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from .groups.infrastructure.prompt import AGENT_NAME as _INFRA_NAME, DESCRIPTION as _INFRA_DESC
from .groups.tables.prompt import AGENT_NAME as _TBL_GRP_NAME, DESCRIPTION as _TBL_GRP_DESC
from .groups.programmability.prompt import AGENT_NAME as _PROG_NAME, DESCRIPTION as _PROG_DESC
from .groups.replication.prompt import AGENT_NAME as _REPL_NAME, DESCRIPTION as _REPL_DESC
from .groups.foreigndata.prompt import AGENT_NAME as _FDW_GRP_NAME, DESCRIPTION as _FDW_GRP_DESC
from .groups.textsearch.prompt import AGENT_NAME as _TS_GRP_NAME, DESCRIPTION as _TS_GRP_DESC
from .groups.datagen.prompt import AGENT_NAME as _DG_GRP_NAME, DESCRIPTION as _DG_GRP_DESC

_GROUPS = "src.sql_server_ai.objagents.sub_agents.dataengineer.groups"

ag_pg_data_engineer = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    planner=cfg.get_planner(1024),
    tools=[
        LazyAgentTool(module_path=f"{_GROUPS}.infrastructure.agent", agent_attr="ag_pg_infrastructure_group", name=_INFRA_NAME, description=_INFRA_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.tables.agent", agent_attr="ag_pg_table_group", name=_TBL_GRP_NAME, description=_TBL_GRP_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.programmability.agent", agent_attr="ag_pg_programmability_group", name=_PROG_NAME, description=_PROG_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.foreigndata.agent", agent_attr="ag_pg_foreign_data_group", name=_FDW_GRP_NAME, description=_FDW_GRP_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.replication.agent", agent_attr="ag_pg_replication_group", name=_REPL_NAME, description=_REPL_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.textsearch.agent", agent_attr="ag_pg_text_search_group", name=_TS_GRP_NAME, description=_TS_GRP_DESC),
        LazyAgentTool(module_path=f"{_GROUPS}.datagen.agent", agent_attr="ag_pg_datagen_group", name=_DG_GRP_NAME, description=_DG_GRP_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
