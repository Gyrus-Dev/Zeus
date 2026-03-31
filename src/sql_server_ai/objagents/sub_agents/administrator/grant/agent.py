from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
import src.sql_server_ai.objagents.config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.tools import execute_query, get_research_results
from src.sql_server_ai.objagents.sub_agents.research.agent import ag_pg_research

ag_pg_manage_grant = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    planner=cfg.get_planner(512),
    tools=[AgentTool(agent=ag_pg_research), execute_query, get_research_results],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
