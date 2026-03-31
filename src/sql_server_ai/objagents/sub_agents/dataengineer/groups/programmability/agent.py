from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...function.prompt import AGENT_NAME as _FN_NAME, DESCRIPTION as _FN_DESC
from ...trigger.prompt import AGENT_NAME as _TRG_NAME, DESCRIPTION as _TRG_DESC
from ...procedure.prompt import AGENT_NAME as _PRC_NAME, DESCRIPTION as _PRC_DESC
from ...eventtrigger.prompt import AGENT_NAME as _EVTTRG_NAME, DESCRIPTION as _EVTTRG_DESC
from ...aggregate.prompt import AGENT_NAME as _AGG_NAME, DESCRIPTION as _AGG_DESC
from ...cast.prompt import AGENT_NAME as _CAST_NAME, DESCRIPTION as _CAST_DESC
from ...language.prompt import AGENT_NAME as _LANG_NAME, DESCRIPTION as _LANG_DESC
from ...operator.prompt import AGENT_NAME as _OPR_NAME, DESCRIPTION as _OPR_DESC
from ...operatorclass.prompt import AGENT_NAME as _OPRCLS_NAME, DESCRIPTION as _OPRCLS_DESC
from ...operatorfamily.prompt import AGENT_NAME as _OPRFAM_NAME, DESCRIPTION as _OPRFAM_DESC
from ...conversion.prompt import AGENT_NAME as _CONV_NAME, DESCRIPTION as _CONV_DESC
from ...transform.prompt import AGENT_NAME as _XFORM_NAME, DESCRIPTION as _XFORM_DESC
from ...accessmethod.prompt import AGENT_NAME as _AM_NAME, DESCRIPTION as _AM_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_programmability_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.function.agent", agent_attr="ag_pg_manage_function", name=_FN_NAME, description=_FN_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.procedure.agent", agent_attr="ag_pg_manage_procedure", name=_PRC_NAME, description=_PRC_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.trigger.agent", agent_attr="ag_pg_manage_trigger", name=_TRG_NAME, description=_TRG_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.eventtrigger.agent", agent_attr="ag_pg_manage_event_trigger", name=_EVTTRG_NAME, description=_EVTTRG_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.aggregate.agent", agent_attr="ag_pg_manage_aggregate", name=_AGG_NAME, description=_AGG_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.cast.agent", agent_attr="ag_pg_manage_cast", name=_CAST_NAME, description=_CAST_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.language.agent", agent_attr="ag_pg_manage_language", name=_LANG_NAME, description=_LANG_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.operator.agent", agent_attr="ag_pg_manage_operator", name=_OPR_NAME, description=_OPR_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.operatorclass.agent", agent_attr="ag_pg_manage_operator_class", name=_OPRCLS_NAME, description=_OPRCLS_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.operatorfamily.agent", agent_attr="ag_pg_manage_operator_family", name=_OPRFAM_NAME, description=_OPRFAM_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.conversion.agent", agent_attr="ag_pg_manage_conversion", name=_CONV_NAME, description=_CONV_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.transform.agent", agent_attr="ag_pg_manage_transform", name=_XFORM_NAME, description=_XFORM_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.accessmethod.agent", agent_attr="ag_pg_manage_access_method", name=_AM_NAME, description=_AM_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
