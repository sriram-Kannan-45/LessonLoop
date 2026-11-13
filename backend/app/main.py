import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        CORSMiddleware, allow_origins=[settings.frontend_origin],
        allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
    )
    application.include_router(router)
    return application


app = create_app()

if __name__ == "__main__":
    config = get_settings()
    uvicorn.run("app.main:app", host=config.backend_host, port=config.backend_port, reload=True)
