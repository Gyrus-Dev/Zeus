from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...tsconfiguration.prompt import AGENT_NAME as _TSCFG_NAME, DESCRIPTION as _TSCFG_DESC
from ...tsdictionary.prompt import AGENT_NAME as _TSDICT_NAME, DESCRIPTION as _TSDICT_DESC
from ...tsparser.prompt import AGENT_NAME as _TSPRS_NAME, DESCRIPTION as _TSPRS_DESC
from ...tstemplate.prompt import AGENT_NAME as _TSTMPL_NAME, DESCRIPTION as _TSTMPL_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_text_search_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.tsconfiguration.agent", agent_attr="ag_pg_manage_ts_configuration", name=_TSCFG_NAME, description=_TSCFG_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.tsdictionary.agent", agent_attr="ag_pg_manage_ts_dictionary", name=_TSDICT_NAME, description=_TSDICT_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.tsparser.agent", agent_attr="ag_pg_manage_ts_parser", name=_TSPRS_NAME, description=_TSPRS_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.tstemplate.agent", agent_attr="ag_pg_manage_ts_template", name=_TSTMPL_NAME, description=_TSTMPL_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
