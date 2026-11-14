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
        self.active_run_id = None
        self.cancelling = False

    @property
    def busy(self):
        return self.cancelling or self.task is not None and not self.task.done()

    def start_run(self, run_id):
        self.active_run_id = run_id
        self.task = asyncio.create_task(execute_run(self.repository, self.ai, run_id))

    def start_improvement(self, experiment_id):
        self.active_run_id = None
        self.task = asyncio.create_task(execute_improvement(self.repository, self.ai, experiment_id))

    async def cancel_run(self, run_id):
        if self.active_run_id != run_id or self.cancelling:
            return False
        self.cancelling = True
        try:
            if self.task and not self.task.done():
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
            if self.repository.get_run(run_id)["status"] == "RUNNING":
                self.repository.finish(run_id, "CANCELLED")
            return True
        finally:
            self.cancelling = False

    async def close(self):
        if self.busy:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.repository.interrupt_active()
