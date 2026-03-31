from google.adk.agents import LlmAgent
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
import src.sql_server_ai.objagents.config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.tools import execute_query

ag_pg_extension_inspector = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    tools=[execute_query],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
