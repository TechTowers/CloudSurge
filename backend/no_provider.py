from vm import Provider
from datetime import date


class NoProvider(Provider):
    """Azure cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date):
        super().__init__(account_name, connection_date)

    @staticmethod
    def from_provider_info(account_name: str, connection_date: date, provider_info: str):
        """Creates a Provider object from the provider information.

        Args:
            account_name (str): Account name.
            connection_date (date): Connection date.
            provider_info (str): Provider information.

        Returns:
            Provider: Provider object.
        """
        return NoProvider(account_name, connection_date)

    def get_provider_name(self) -> str:
        """Returns the name of the provider (Azure)."""
        return "No-Provider"

    def get_provider_info(self) -> str:
        """Returns information about the provider (e.g., Subscription ID)."""
        return self.get_provider_name() + ": "


    def connection_is_alive(self) -> str:
        """Returns if the connection to the provider is still alive"""
        pass

    def create_vm(self):
        pass

    def stop_vm(self, virtual_machine) -> None:
        """Stops the virtual machine on Azure."""
        pass

    def delete_vm(self, virtual_machine) -> None:
        """Deletes the virtual machine on Azure."""
        pass

    def configure_vm(self, virtual_machine) -> None:
        """Configures the virtual machine as per the Azure specifics."""
        pass

    def __str__(self):
        return "\n  No-Provider"