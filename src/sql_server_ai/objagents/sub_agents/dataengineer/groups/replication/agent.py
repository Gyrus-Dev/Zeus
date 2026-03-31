from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
from src.sql_server_ai.objagents import config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.lazy_agent_tool import LazyAgentTool

from ...publication.prompt import AGENT_NAME as _PUB_NAME, DESCRIPTION as _PUB_DESC
from ...subscription.prompt import AGENT_NAME as _SUB_NAME, DESCRIPTION as _SUB_DESC

_SPECIALISTS = "src.sql_server_ai.objagents.sub_agents.dataengineer"

ag_pg_replication_group = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[
        LazyAgentTool(module_path=f"{_SPECIALISTS}.publication.agent", agent_attr="ag_pg_manage_publication", name=_PUB_NAME, description=_PUB_DESC),
        LazyAgentTool(module_path=f"{_SPECIALISTS}.subscription.agent", agent_attr="ag_pg_manage_subscription", name=_SUB_NAME, description=_SUB_DESC),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
