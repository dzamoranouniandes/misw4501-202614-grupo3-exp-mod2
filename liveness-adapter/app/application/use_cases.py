from app.application.ports import ActiveProviderConfiguration, LivenessProvider
from app.domain.models import VerificationCommand, VerificationResult


class ProviderNotRegisteredError(ValueError):
    pass


class VerifyLiveness:
    def __init__(
        self,
        providers: dict[str, LivenessProvider],
        configuration: ActiveProviderConfiguration,
    ) -> None:
        self._providers = providers
        self._configuration = configuration

    def execute(self, command: VerificationCommand) -> VerificationResult:
        provider_name = self._configuration.get_active_provider()
        provider = self._providers.get(provider_name)
        if provider is None:
            raise ProviderNotRegisteredError(f"Provider '{provider_name}' is not registered")
        return provider.verify(command)


class ChangeActiveProvider:
    def __init__(
        self,
        providers: dict[str, LivenessProvider],
        configuration: ActiveProviderConfiguration,
    ) -> None:
        self._providers = providers
        self._configuration = configuration

    def execute(self, provider_name: str) -> None:
        if provider_name not in self._providers:
            raise ProviderNotRegisteredError(f"Provider '{provider_name}' is not registered")
        self._configuration.set_active_provider(provider_name)

