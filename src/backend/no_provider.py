# author: Luka Pacar
from .vm import Provider
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
        """Returns information about the provider (e.g., No-Provider Name)."""
        return self.get_provider_name() + self.starting_character + " "

    def connection_is_alive(self) -> str:
        """Does Nothing."""

    def create_vm(self):
        """Does Nothing."""

    def start_vm(self, virtual_machine) -> None:
        """Does Nothing."""

    def stop_vm(self, virtual_machine) -> None:
        """Does Nothing."""

    def delete_vm(self, virtual_machine) -> None:
        """Does Nothing."""

    def is_active(self, vm):
        """Check if the connection is active."""
        return False

    def get_vm_cost(self, vm):
        """Get the cost of the virtual machine."""
        return 0

    def get_vm_uptime(self, vm):
        """Get the uptime of the virtual machine."""
        return 0

    def get_vm_hourly_rate(self, vm):
        """Get the hourly rate of the virtual machine."""
        return 0

    def __str__(self):
        return "\n  No-Provider"