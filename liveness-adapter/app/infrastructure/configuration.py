class InMemoryActiveProviderConfiguration:
    """Runtime configuration. Replace with a ConfigMap or persisted store if needed later."""

    def __init__(self, initial_provider: str) -> None:
        self._active_provider = initial_provider

    def get_active_provider(self) -> str:
        return self._active_provider

    def set_active_provider(self, provider_name: str) -> None:
        self._active_provider = provider_name

