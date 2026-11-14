import asyncio

from app.db import Repository
from app.improvements import execute_improvement
from app.services.lesson_ai import LessonAI
from app.workflow import execute_run


class Runtime:
    def __init__(self, settings, repository=None, ai=None):
        self.settings = settings
        self.repository = repository or Repository(settings.database_path)
        self.ai = ai or LessonAI(settings)
        self.task = None

    @property
    def busy(self):
        return self.task is not None and not self.task.done()

    def start_run(self, run_id):
        self.task = asyncio.create_task(execute_run(self.repository, self.ai, run_id))

    def start_improvement(self, experiment_id):
        self.task = asyncio.create_task(execute_improvement(self.repository, self.ai, experiment_id))

    async def close(self):
        if self.busy:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.repository.interrupt_active()
