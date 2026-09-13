import logging
import uuid
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="Didit Mock", version="0.1.0")


class DiditCheckRequest(BaseModel):
    subject_reference: str = Field(min_length=1)
    selfie_reference: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/liveness/checks")
def create_check(
    body: DiditCheckRequest,
    x_correlation_id: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    correlation_id = x_correlation_id or "missing"
    logger.info("didit_mock_received correlation_id=%s", correlation_id)
    if body.selfie_reference.startswith("synthetic-selfie-error"):
        raise HTTPException(status_code=503, detail="Simulated Didit outage")
    decision = "FAILED" if body.selfie_reference.startswith("synthetic-selfie-rejected") else "PASSED"
    return {"check_id": f"didit-{uuid.uuid4()}", "decision": decision}

