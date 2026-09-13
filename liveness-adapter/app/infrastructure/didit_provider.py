import logging

import httpx

from app.domain.models import LivenessStatus, VerificationCommand, VerificationResult

logger = logging.getLogger(__name__)


class DiditProvider:
    """Secondary adapter translating the internal port to Didit's external contract."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def verify(self, command: VerificationCommand) -> VerificationResult:
        response = httpx.post(
            f"{self._base_url}/v1/liveness/checks",
            json={
                "subject_reference": command.customer_id,
                "selfie_reference": command.evidence_ref,
            },
            headers={"X-Correlation-Id": command.correlation_id},
            timeout=5.0,
        )
        response.raise_for_status()
        body = response.json()
        status = LivenessStatus.APPROVED if body["decision"] == "PASSED" else LivenessStatus.REJECTED
        logger.info("liveness_provider=didit correlation_id=%s", command.correlation_id)
        return VerificationResult(
            verification_id=body["check_id"],
            status=status,
            correlation_id=command.correlation_id,
        )

