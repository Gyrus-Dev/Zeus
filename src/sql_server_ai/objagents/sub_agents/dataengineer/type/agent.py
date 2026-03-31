import logging
import pathlib
from google.adk.agents import LlmAgent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.tools import AgentTool
from .prompt import AGENT_NAME, DESCRIPTION, INSTRUCTION
import src.sql_server_ai.objagents.config as cfg
from src.sql_server_ai.objagents.sub_agents.pillar_callbacks import before_model_callback, after_model_callback
from src.sql_server_ai.objagents.tools import execute_query, get_research_results
from src.sql_server_ai.objagents.sub_agents.research.agent import ag_pg_research

logger = logging.getLogger(__name__)

_skills_dir = pathlib.Path(__file__).parents[6] / "skills"
_skill_toolset = SkillToolset(
    skills=[load_skill_from_dir(_skills_dir / "sqlserver-create-type")]
)

ag_pg_manage_type = LlmAgent(
    model=cfg.PRIMARY_MODEL,
    name=AGENT_NAME,
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    planner=cfg.get_planner(512),
    tools=([_skill_toolset] if cfg.USE_SKILLS else []) + [AgentTool(agent=ag_pg_research), execute_query, get_research_results],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
