import httpx

from app.domain.models import LivenessRequest, LivenessResult, LivenessStatus


class HttpLivenessAdapterClient:
    """Secondary adapter: the application knows only its port, not HTTP details."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def verify(self, request: LivenessRequest) -> LivenessResult:
        response = httpx.post(
            f"{self._base_url}/liveness/verifications",
            json={
                "customer_id": request.customer_id,
                "evidence_ref": request.evidence_ref,
                "correlation_id": request.correlation_id,
            },
            timeout=5.0,
        )
        response.raise_for_status()
        body = response.json()
        return LivenessResult(
            verification_id=body["verification_id"],
            status=LivenessStatus(body["status"]),
            correlation_id=body["correlation_id"],
        )

