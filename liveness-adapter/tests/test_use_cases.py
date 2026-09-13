import pytest
import httpx

from app.application.use_cases import ChangeActiveProvider, ProviderNotRegisteredError, VerifyLiveness
from app.domain.models import LivenessStatus, VerificationCommand, VerificationResult
from app.infrastructure.alternative_provider import AlternativeProvider
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


def test_alternative_provider_is_selected_by_runtime_configuration() -> None:
    configuration = InMemoryActiveProviderConfiguration("didit")
    providers = {"didit": DiditSpy(), "alternative": AlternativeProvider()}
    ChangeActiveProvider(providers, configuration).execute("alternative")

    result = VerifyLiveness(providers, configuration).execute(
        VerificationCommand("customer-1", "synthetic-selfie-approved", "corr-alternative")
    )

    assert result.verification_id.startswith("alternative-")
    assert result.status == LivenessStatus.APPROVED
    assert result.correlation_id == "corr-alternative"


def test_alternative_provider_simulates_an_unavailable_external_service() -> None:
    provider = AlternativeProvider()

    with pytest.raises(httpx.ConnectError):
        provider.verify(VerificationCommand("customer-1", "synthetic-selfie-error", "corr-error"))
