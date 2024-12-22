from vm import Provider
from datetime import date

class Azure(Provider):
    """Azure cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, subscription_id: str, client_id: str, client_secret: str, tenant_id: str):
        super().__init__(account_name, connection_date)
        self._subscription_id = subscription_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._tenant_id = tenant_id

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
        provider_info = provider_info.split(",,,")
        return Azure(account_name, connection_date, provider_info[0], provider_info[1], provider_info[2], provider_info[3])

    def get_provider_name(self) -> str:
        """Returns the name of the provider (Azure)."""
        return "Azure"

    def get_provider_info(self) -> str:
        """Returns information about the provider (e.g., Subscription ID)."""
        return self.get_provider_name() + ":" + f"{self._subscription_id},,,{self._client_id},,,{self._client_secret},,,{self._tenant_id}"

    def create_vm(self) -> None:
        """Creates or starts a virtual machine on Azure."""
        print(f"Creating/starting VM for Azure account {self._account_name}...")

    def stop_vm(self, virtual_machine) -> None:
        """Stops the virtual machine on Azure."""
        print(f"Stopping VM for Azure account {self._account_name}...")

    def delete_vm(self, virtual_machine) -> None:
        """Deletes the virtual machine on Azure."""
        print(f"Deleting VM for Azure account {self._account_name}...")

    def configure_vm(self, virtual_machine) -> None:
        """Configures the virtual machine as per the Azure specifics."""
        print(f"Configuring VM for Azure account {self._account_name}...")

    def __str__(self):
        return f"\n  Provider-Azure:\n  Account Name: {self._account_name}\n  Connection Date: {self._connection_date}\n  Subscription ID: {self._subscription_id}\n  Client ID: {self._client_id}\n  Client Secret: {self._client_secret}\n  Tenant ID: {self._tenant_id}"
