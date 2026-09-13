from typing import Protocol

from app.domain.models import LivenessRequest, LivenessResult


class LivenessVerificationPort(Protocol):
    def verify(self, request: LivenessRequest) -> LivenessResult: ...

