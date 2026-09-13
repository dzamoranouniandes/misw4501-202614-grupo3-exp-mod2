import pytest

from app.application.use_cases import ChangeActiveProvider, ProviderNotRegisteredError, VerifyLiveness
from app.domain.models import LivenessStatus, VerificationCommand, VerificationResult
from app.infrastructure.configuration import InMemoryActiveProviderConfiguration


class DiditSpy:
    def verify(self, command: VerificationCommand) -> VerificationResult:
        return VerificationResult("check-1", LivenessStatus.APPROVED, command.correlation_id)


def test_verification_uses_the_configured_provider() -> None:
    configuration = InMemoryActiveProviderConfiguration("didit")
    use_case = VerifyLiveness({"didit": DiditSpy()}, configuration)

    result = use_case.execute(VerificationCommand("customer-1", "evidence-1", "corr-1"))

    assert result.verification_id == "check-1"
    assert result.status == LivenessStatus.APPROVED


def test_cannot_select_a_provider_that_is_not_registered() -> None:
    configuration = InMemoryActiveProviderConfiguration("didit")
    use_case = ChangeActiveProvider({"didit": DiditSpy()}, configuration)

    with pytest.raises(ProviderNotRegisteredError):
        use_case.execute("alternative")

