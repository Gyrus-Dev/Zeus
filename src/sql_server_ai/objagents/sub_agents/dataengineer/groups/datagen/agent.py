from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...syntheticdata.prompt import AGENT_NAME as _SD_NAME, DESCRIPTION as _SD_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_datagen_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.syntheticdata.agent", agent_attr="ag_pg_manage_synthetic_data", name=_SD_NAME, description=_SD_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
