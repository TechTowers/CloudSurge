from vm import Provider
from datetime import date

import subprocess
import json

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

    def connection_is_alive(self) -> str:
        """Returns if the connection to the provider is still alive"""

        pass
    def create_vm(self):
        """Creates a virtual machine on Azure using `curl`."""

        # Step 1: Obtain an OAuth 2.0 token using client credentials
        token_url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "https://management.azure.com/.default"
        }

        # Execute curl to get the token
        token_command = [
            "curl", "-X", "POST", token_url,
            "-H", "Content-Type: application/x-www-form-urlencoded",
            "-d", f"grant_type={token_data['grant_type']}&client_id={token_data['client_id']}&client_secret={token_data['client_secret']}&scope={token_data['scope']}"
        ]
        response = subprocess.run(token_command, capture_output=True, text=True)
        token_response = json.loads(response.stdout)

        if "access_token" not in token_response:
            print("Failed to obtain access token.")
            return

        access_token = token_response["access_token"]

        # Step 2: Create a Virtual Machine (VM) using Azure REST API
        # Variables for VM creation
        resource_group = "myResourceGroup"
        vm_name = "myVMName"  # VM name variable
        location = "eastus"
        vm_size = "Standard_DS1_v2"
        publisher = "Canonical"
        offer = "UbuntuServer"
        sku = "20_04-lts"
        version = "latest"
        os_disk_create_option = "FromImage"
        admin_username = "azureuser"
        admin_password = "Password123!"
        nic_id = f"/subscriptions/{self._subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkInterfaces/myNic"

        vm_creation_url = f"https://management.azure.com/subscriptions/{self._subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}?api-version=2023-05-01"

        vm_creation_payload = {
            "location": location,
            "properties": {
                "hardwareProfile": {
                    "vmSize": vm_size
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": publisher,
                        "offer": offer,
                        "sku": sku,
                        "version": version
                    },
                    "osDisk": {
                        "createOption": os_disk_create_option
                    }
                },
                "osProfile": {
                    "computerName": vm_name,
                    "adminUsername": admin_username,
                    "adminPassword": admin_password
                },
                "networkProfile": {
                    "networkInterfaces": [{
                        "id": nic_id
                    }]
                }
            }
        }

        # Execute the curl to create the VM
        vm_creation_command = [
            "curl", "-X", "PUT", vm_creation_url,
            "-H", f"Authorization: Bearer {access_token}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(vm_creation_payload)
        ]
        create_vm_response = subprocess.run(vm_creation_command, capture_output=True, text=True)

        if create_vm_response.returncode == 0:
            print(f"VM creation response: {create_vm_response.stdout}")
        else:
            print(f"Failed to create VM: {create_vm_response.stderr}")

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
