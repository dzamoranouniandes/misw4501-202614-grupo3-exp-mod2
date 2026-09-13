from app.application.ports import LivenessVerificationPort
from app.domain.models import LivenessRequest, LivenessResult


class StartLivenessOnboarding:
    def __init__(self, liveness_port: LivenessVerificationPort) -> None:
        self._liveness_port = liveness_port

    def execute(self, request: LivenessRequest) -> LivenessResult:
        return self._liveness_port.verify(request)

