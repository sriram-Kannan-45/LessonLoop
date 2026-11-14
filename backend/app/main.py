import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import get_settings
from app.api.workspace import ApiProblem, router as workspace_router
from app.runtime import Runtime


def create_app(settings=None, repository=None, ai=None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application):
        current = Runtime(settings, repository, ai)
        current.repository.interrupt_active()
        application.state.runtime = current
        yield
        await current.close()

    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware, allow_origins=[settings.frontend_origin],
        allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
    )
    application.include_router(router)
    application.include_router(workspace_router)

    @application.exception_handler(ApiProblem)
    async def api_problem_handler(request, exc):
        return JSONResponse(status_code=exc.status, content={"status": "error", "error_code": exc.code, "message": exc.message})

    return application


app = create_app()

if __name__ == "__main__":
    config = get_settings()
    uvicorn.run("app.main:app", host=config.backend_host, port=config.backend_port, reload=True)
