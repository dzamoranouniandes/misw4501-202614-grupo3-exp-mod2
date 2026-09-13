import logging
import uuid

import httpx

from app.domain.models import LivenessStatus, VerificationCommand, VerificationResult

logger = logging.getLogger("uvicorn.error")


class AlternativeProvider:
    """Mock implementation of a second liveness provider for the HA12 experiment.

    It deliberately uses a different internal decision vocabulary to demonstrate
    that provider-specific semantics remain inside the adapter.
    """

    def verify(self, command: VerificationCommand) -> VerificationResult:
        if command.evidence_ref.startswith("synthetic-selfie-error"):
            logger.info("liveness_provider=alternative_unavailable correlation_id=%s", command.correlation_id)
            raise httpx.ConnectError("Simulated alternative provider outage")
        external_decision = (
            "NOT_LIVE"
            if command.evidence_ref.startswith("synthetic-selfie-rejected")
            else "LIVE_CONFIRMED"
        )
        status = (
            LivenessStatus.REJECTED
            if external_decision == "NOT_LIVE"
            else LivenessStatus.APPROVED
        )
        logger.info("liveness_provider=alternative correlation_id=%s", command.correlation_id)
        return VerificationResult(
            verification_id=f"alternative-{uuid.uuid4()}",
            status=status,
            correlation_id=command.correlation_id,
        )
