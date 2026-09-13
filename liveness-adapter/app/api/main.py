import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.application.use_cases import ChangeActiveProvider, ProviderNotRegisteredError, VerifyLiveness
from app.domain.models import VerificationCommand
from app.infrastructure.alternative_provider import AlternativeProvider
from app.infrastructure.configuration import InMemoryActiveProviderConfiguration
from app.infrastructure.didit_provider import DiditProvider

app = FastAPI(title="Liveness Adapter", version="0.1.0")


class VerificationRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    evidence_ref: str = Field(min_length=1, max_length=200)
    correlation_id: str = Field(min_length=1, max_length=100)


class VerificationResponse(BaseModel):
    verification_id: str
    status: str
    correlation_id: str


class ProviderSelection(BaseModel):
    provider: str = Field(min_length=1, max_length=50)


configuration = InMemoryActiveProviderConfiguration(os.getenv("LIVENESS_PROVIDER", "didit"))
providers = {
    "didit": DiditProvider(os.getenv("DIDIT_BASE_URL", "http://localhost:8003")),
    "alternative": AlternativeProvider(),
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/liveness/verifications", response_model=VerificationResponse)
def verify_liveness(body: VerificationRequest) -> VerificationResponse:
    try:
        result = VerifyLiveness(providers, configuration).execute(
            VerificationCommand(**body.model_dump())
        )
    except ProviderNotRegisteredError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Configured liveness provider is unavailable") from error
    return VerificationResponse(
        verification_id=result.verification_id,
        status=result.status.value,
        correlation_id=result.correlation_id,
    )


@app.get("/admin/liveness-provider", response_model=ProviderSelection)
def get_active_provider() -> ProviderSelection:
    return ProviderSelection(provider=configuration.get_active_provider())


@app.put("/admin/liveness-provider", response_model=ProviderSelection)
def set_active_provider(body: ProviderSelection) -> ProviderSelection:
    try:
        ChangeActiveProvider(providers, configuration).execute(body.provider)
    except ProviderNotRegisteredError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return body
