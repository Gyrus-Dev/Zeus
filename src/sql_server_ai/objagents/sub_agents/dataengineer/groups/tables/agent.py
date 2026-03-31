from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...table.prompt import AGENT_NAME as _TBL_NAME, DESCRIPTION as _TBL_DESC
from ...index.prompt import AGENT_NAME as _IDX_NAME, DESCRIPTION as _IDX_DESC
from ...view.prompt import AGENT_NAME as _VW_NAME, DESCRIPTION as _VW_DESC
from ...materializedview.prompt import AGENT_NAME as _MV_NAME, DESCRIPTION as _MV_DESC
from ...sequence.prompt import AGENT_NAME as _SEQ_NAME, DESCRIPTION as _SEQ_DESC
from ...type.prompt import AGENT_NAME as _TYPE_NAME, DESCRIPTION as _TYPE_DESC
from ...domain.prompt import AGENT_NAME as _DOM_NAME, DESCRIPTION as _DOM_DESC
from ...statistics.prompt import AGENT_NAME as _STATS_NAME, DESCRIPTION as _STATS_DESC
from ...rule.prompt import AGENT_NAME as _RULE_NAME, DESCRIPTION as _RULE_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_table_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.table.agent", agent_attr="ag_pg_manage_table", name=_TBL_NAME, description=_TBL_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.index.agent", agent_attr="ag_pg_manage_index", name=_IDX_NAME, description=_IDX_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.view.agent", agent_attr="ag_pg_manage_view", name=_VW_NAME, description=_VW_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.materializedview.agent", agent_attr="ag_pg_manage_materialized_view", name=_MV_NAME, description=_MV_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.sequence.agent", agent_attr="ag_pg_manage_sequence", name=_SEQ_NAME, description=_SEQ_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.type.agent", agent_attr="ag_pg_manage_type", name=_TYPE_NAME, description=_TYPE_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.domain.agent", agent_attr="ag_pg_manage_domain", name=_DOM_NAME, description=_DOM_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.statistics.agent", agent_attr="ag_pg_manage_statistics", name=_STATS_NAME, description=_STATS_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.rule.agent", agent_attr="ag_pg_manage_rule", name=_RULE_NAME, description=_RULE_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
