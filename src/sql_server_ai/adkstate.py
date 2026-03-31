import logging

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)


class ADKState:
    def __init__(self):
        self.state_dict = {}

    def add_state(self, key, value=None):
        self.state_dict[key] = value if value is not None else ""

    def add_user_state(self, key, value=None):
        self.state_dict[f"user:{key}"] = value if value is not None else ""

    def add_app_state(self, key, value=None):
        self.state_dict[f"app:{key}"] = value if value is not None else ""


class SQLServerState(ADKState):
    def __init__(self, user_name, pg_user, password, host, port=1433, database=None):
        super().__init__()
        self.user_name = user_name
        self.pg_user = pg_user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def init_sqlserver_state(self):
        self.add_user_state("USER_NAME", self.user_name)
        self.add_user_state("SQLSERVER_USER", self.pg_user)
        self.add_user_state("SQLSERVER_PASSWORD", self.password)
        self.add_user_state("QUERIES_EXECUTED", [])
        self.add_app_state("SQLSERVER_HOST", self.host)
        self.add_app_state("SQLSERVER_PORT", self.port)
        self.add_app_state("SQLSERVER_DATABASE", self.database)
        self.add_app_state("LOGGER", logger.name)
        self.add_app_state("TASKS_PERFORMED", [])
        self.add_app_state("RESEARCH_RESULTS", {})
        self.add_app_state("INFRASTRUCTURE_SNAPSHOT", [])

    def init_postgres_state(self):
        self.init_sqlserver_state()


PostgresState = SQLServerState
