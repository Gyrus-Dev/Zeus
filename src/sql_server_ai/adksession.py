import uuid
from google.adk.sessions import InMemorySessionService
from .adkstate import SQLServerState


class ADKSession:
    def __init__(self, app_name, user_id, state: SQLServerState):
        self.id = str(uuid.uuid4())
        self.app_name = app_name
        self.user_id = user_id
        self.state = state.state_dict

    async def create_session(self):
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            state=self.state,
        )
        session_id = getattr(session, "id", None)
        if session_id:
            self.id = session_id
        return session, session_service


class SQLServerADKSession(ADKSession):
    def __init__(self, user_id, app_name, state: SQLServerState):
        super().__init__(app_name=app_name, user_id=user_id, state=state)


PostgresADKSession = SQLServerADKSession
