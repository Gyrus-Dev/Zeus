from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from .schemainspector.prompt import AGENT_NAME as _SCH_NAME, DESCRIPTION as _SCH_DESC
from .tableinspector.prompt import AGENT_NAME as _TBL_NAME, DESCRIPTION as _TBL_DESC
from .userinspector.prompt import AGENT_NAME as _USR_NAME, DESCRIPTION as _USR_DESC
from .routineinspector.prompt import AGENT_NAME as _RTN_NAME, DESCRIPTION as _RTN_DESC
from .typeinspector.prompt import AGENT_NAME as _TYP_NAME, DESCRIPTION as _TYP_DESC
from .extensioninspector.prompt import AGENT_NAME as _EXT_NAME, DESCRIPTION as _EXT_DESC
from .foreigndatainspector.prompt import AGENT_NAME as _FDW_NAME, DESCRIPTION as _FDW_DESC
from .replicationinspector.prompt import AGENT_NAME as _REP_NAME, DESCRIPTION as _REP_DESC
from .textsearchinspector.prompt import AGENT_NAME as _TSR_NAME, DESCRIPTION as _TSR_DESC
from .objectinspector.prompt import AGENT_NAME as _OBJ_NAME, DESCRIPTION as _OBJ_DESC

_BASE = "src.sql_server_ai.objagents.sub_agents.inspector"

ag_pg_inspector_pillar = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    planner=cfg.get_planner(512),
    tools=[
        LazyAgentTool(module_path=f"{_BASE}.schemainspector.agent", agent_attr="ag_pg_schema_inspector", name=_SCH_NAME, description=_SCH_DESC),
        LazyAgentTool(module_path=f"{_BASE}.tableinspector.agent", agent_attr="ag_pg_table_inspector", name=_TBL_NAME, description=_TBL_DESC),
        LazyAgentTool(module_path=f"{_BASE}.userinspector.agent", agent_attr="ag_pg_user_inspector", name=_USR_NAME, description=_USR_DESC),
        LazyAgentTool(module_path=f"{_BASE}.routineinspector.agent", agent_attr="ag_pg_routine_inspector", name=_RTN_NAME, description=_RTN_DESC),
        LazyAgentTool(module_path=f"{_BASE}.typeinspector.agent", agent_attr="ag_pg_type_inspector", name=_TYP_NAME, description=_TYP_DESC),
        LazyAgentTool(module_path=f"{_BASE}.extensioninspector.agent", agent_attr="ag_pg_extension_inspector", name=_EXT_NAME, description=_EXT_DESC),
        LazyAgentTool(module_path=f"{_BASE}.foreigndatainspector.agent", agent_attr="ag_pg_foreign_data_inspector", name=_FDW_NAME, description=_FDW_DESC),
        LazyAgentTool(module_path=f"{_BASE}.replicationinspector.agent", agent_attr="ag_pg_replication_inspector", name=_REP_NAME, description=_REP_DESC),
        LazyAgentTool(module_path=f"{_BASE}.textsearchinspector.agent", agent_attr="ag_pg_text_search_inspector", name=_TSR_NAME, description=_TSR_DESC),
        LazyAgentTool(module_path=f"{_BASE}.objectinspector.agent", agent_attr="ag_pg_object_inspector", name=_OBJ_NAME, description=_OBJ_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
