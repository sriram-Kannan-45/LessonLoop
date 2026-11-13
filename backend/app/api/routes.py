from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.schemas import CheckError, CheckSuccess, HealthResponse, Provider, ProvidersStatus
from app.services.providers import ProviderFailure, check_provider, configuration_status

router = APIRouter(prefix="/api")
Config = Annotated[Settings, Depends(get_settings)]


@router.get("/health", response_model=HealthResponse)
async def health(settings: Config):
    return HealthResponse(app=settings.app_name, environment=settings.app_env)


@router.get("/providers/status", response_model=ProvidersStatus)
async def providers_status(settings: Config):
    return ProvidersStatus(**{
        provider.value: configuration_status(settings, provider) for provider in Provider
    })


@router.post("/providers/{provider}/check", response_model=CheckSuccess,
             responses={code: {"model": CheckError} for code in (401, 403, 404, 429, 502, 503, 504)})
async def provider_check(provider: Provider, settings: Config, request: Request):
    # A browser origin check also prevents cross-site pages from triggering paid POSTs.
    origin = request.headers.get("origin")
    if settings.app_env != "development" or (origin and origin != settings.frontend_origin):
        error = CheckError(provider=provider, error_code="DIAGNOSTICS_DISABLED",
                           message="Provider checks are available only from the configured local development frontend.")
        return JSONResponse(status_code=403, content=error.model_dump(mode="json"))
    try:
        return await check_provider(settings, provider)
    except ProviderFailure as exc:
        error = CheckError(provider=provider, error_code=exc.code, message=exc.message)
        return JSONResponse(status_code=exc.status_code, content=error.model_dump(mode="json"))
