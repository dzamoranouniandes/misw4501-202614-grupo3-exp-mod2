from app.application.use_cases import StartLivenessOnboarding
from app.domain.models import LivenessRequest, LivenessResult, LivenessStatus


class LivenessSpy:
    def __init__(self) -> None:
        self.request: LivenessRequest | None = None

    def verify(self, request: LivenessRequest) -> LivenessResult:
        self.request = request
        return LivenessResult("lv-123", LivenessStatus.APPROVED, request.correlation_id)


def test_onboarding_delegates_to_the_liveness_port() -> None:
    spy = LivenessSpy()
    use_case = StartLivenessOnboarding(spy)
    request = LivenessRequest("customer-1", "synthetic-selfie-approved", "corr-1")

    result = use_case.execute(request)

    assert spy.request == request
    assert result.status == LivenessStatus.APPROVED
    assert result.correlation_id == "corr-1"

