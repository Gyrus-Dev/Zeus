from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...foreigndatawrapper.prompt import AGENT_NAME as _FDW_NAME, DESCRIPTION as _FDW_DESC
from ...foreignserver.prompt import AGENT_NAME as _FSRV_NAME, DESCRIPTION as _FSRV_DESC
from ...usermapping.prompt import AGENT_NAME as _UM_NAME, DESCRIPTION as _UM_DESC
from ...foreigntable.prompt import AGENT_NAME as _FT_NAME, DESCRIPTION as _FT_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_foreign_data_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.foreigndatawrapper.agent", agent_attr="ag_pg_manage_foreign_data_wrapper", name=_FDW_NAME, description=_FDW_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.foreignserver.agent", agent_attr="ag_pg_manage_foreign_server", name=_FSRV_NAME, description=_FSRV_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.usermapping.agent", agent_attr="ag_pg_manage_user_mapping", name=_UM_NAME, description=_UM_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.foreigntable.agent", agent_attr="ag_pg_manage_foreign_table", name=_FT_NAME, description=_FT_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
