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

    def get_provider_name(self) -> str:
        """Returns the name of the provider (Azure)."""
        return "Azure"

    def get_provider_info(self) -> str:
        """Returns information about the provider (e.g., Subscription ID)."""
        return f"Subscription ID:'{self._subscription_id}',client-id:'{self._client_id}',client-secret:'{self._client_secret}',tenant-id:'{self._tenant_id}'"

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
