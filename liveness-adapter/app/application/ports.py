from typing import Protocol

from app.domain.models import VerificationCommand, VerificationResult


class LivenessProvider(Protocol):
    """Port implemented by each external liveness provider."""

    def verify(self, command: VerificationCommand) -> VerificationResult: ...


class ActiveProviderConfiguration(Protocol):
    def get_active_provider(self) -> str: ...

    def set_active_provider(self, provider_name: str) -> None: ...

