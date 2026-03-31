from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTIONS, SEARCH_INSTRUCTIONS
from .tools import save_research_results, web_search
import src.sql_server_ai.objagents.config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback

if cfg.IS_GOOGLE_MODEL:
    from google.adk.tools import google_search
    _search_tool = google_search
else:
    _search_tool = web_search

_ag_pg_research_search = LlmAgent(
    name="RESEARCH_SEARCH_AGENT",
    model=cfg.PRIMARY_MODEL,
    description="Performs web searches about PostgreSQL.",
    instruction=SEARCH_INSTRUCTIONS,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    tools=[_search_tool],
)

ag_pg_research = LlmAgent(
    name=AGENT_NAME,
    model=cfg.PRIMARY_MODEL,
    description=DESCRIPTION,
    instruction=INSTRUCTIONS,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    tools=[AgentTool(agent=_ag_pg_research_search), save_research_results],
)
