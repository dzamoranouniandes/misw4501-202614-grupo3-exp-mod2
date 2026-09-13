import os
import uuid
import logging
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app.application.use_cases import StartLivenessOnboarding
from app.domain.models import LivenessRequest
from app.infrastructure.http_liveness_client import HttpLivenessAdapterClient

app = FastAPI(title="Identity Service", version="0.1.0")
logger = logging.getLogger("uvicorn.error")


class OnboardingRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    evidence_ref: str = Field(min_length=1, max_length=200)


class OnboardingResponse(BaseModel):
    verification_id: str
    status: str
    correlation_id: str


def get_use_case() -> StartLivenessOnboarding:
    return StartLivenessOnboarding(
        HttpLivenessAdapterClient(os.getenv("LIVENESS_ADAPTER_URL", "http://localhost:8002"))
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/onboarding/liveness", response_model=OnboardingResponse)
def start_onboarding(
    body: OnboardingRequest,
    x_correlation_id: Annotated[str | None, Header()] = None,
) -> OnboardingResponse:
    correlation_id = x_correlation_id or str(uuid.uuid4())
    logger.info("onboarding_received correlation_id=%s", correlation_id)
    request = LivenessRequest(
        customer_id=body.customer_id,
        evidence_ref=body.evidence_ref,
        correlation_id=correlation_id,
    )
    try:
        result = get_use_case().execute(request)
    except Exception as error:
        logger.error("onboarding_failed correlation_id=%s", correlation_id)
        raise HTTPException(status_code=502, detail="Liveness verification is unavailable") from error
    logger.info("onboarding_completed correlation_id=%s status=%s", correlation_id, result.status.value)
    return OnboardingResponse(
        verification_id=result.verification_id,
        status=result.status.value,
        correlation_id=result.correlation_id,
    )
