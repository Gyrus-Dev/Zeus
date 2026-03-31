from google.adk.runners import Runner


class ADKRunner:
    def __init__(self, agent, app_name, session_service, memory_service=None):
        self.agent = agent
        self.app_name = app_name
        self.session_service = session_service
        self.memory_service = memory_service

    def get_runner(self):
        return Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service,
        )
