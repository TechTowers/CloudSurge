from vm import Provider
from datetime import date
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

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
        # Retrieve Ids using:
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        # az ad sp create-for-rbac --name <your-service-principal-name> --role Contributor --scopes /subscriptions/<your-subscription-id> --output json

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

    def connection_is_alive(self) -> bool:
        """
        Verifies if the Azure login/authentication works.

        :return: True if login/authentication is successful, False otherwise.
        """
        try:
            # Attempt to list subscriptions to confirm authentication
            subscriptions = list(ComputeManagementClient(self.credential, self.subscription_id).subscriptions.list())
            print(f"Authenticated successfully. Found {len(subscriptions)} subscriptions.")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def create_vm(
            self,
            subscription_id: str,
            resource_group_name: str,
            location: str,
            vm_name: str,
            vm_size: str,
            admin_username: str,
            admin_password: str,
            image_reference: dict,
            network_vnet_name: str,
            network_subnet_name: str,
            public_ip_name: str,
            nic_name: str
    ):

        # Authenticate using ClientSecretCredential
        credential = self.credential

        # Create clients for managing Azure resources
        resource_client = ResourceManagementClient(credential, subscription_id)
        compute_client = ComputeManagementClient(credential, subscription_id)
        network_client = NetworkManagementClient(credential, subscription_id)

        # Step 1: Create Resource Group
        resource_client.resource_groups.create_or_update(
            resource_group_name,
            {"location": location}
        )

        # Step 2: Create Virtual Network and Subnet
        vnet = network_client.virtual_networks.begin_create_or_update(
            resource_group_name,
            network_vnet_name,
            {
                "location": location,
                "address_space": {"address_prefixes": ["10.0.0.0/16"]},
            },
        ).result()

        subnet = network_client.subnets.begin_create_or_update(
            resource_group_name,
            network_vnet_name,
            network_subnet_name,
            {"address_prefix": "10.0.0.0/24"},
        ).result()

        # Step 3: Create Public IP Address
        public_ip = network_client.public_ip_addresses.begin_create_or_update(
            resource_group_name,
            public_ip_name,
            {
                "location": location,
                "sku": {"name": "Basic"},
                "public_ip_allocation_method": "Dynamic",
            },
        ).result()

        # Step 4: Create Network Interface
        nic = network_client.network_interfaces.begin_create_or_update(
            resource_group_name,
            nic_name,
            {
                "location": location,
                "ip_configurations": [
                    {
                        "name": "default",
                        "subnet": {"id": subnet.id},
                        "public_ip_address": {"id": public_ip.id},
                    }
                ],
            },
        ).result()

        # Step 5: Create Virtual Machine
        vm_parameters = {
            "location": location,
            "hardware_profile": {"vm_size": vm_size},
            "storage_profile": {"image_reference": image_reference},
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": admin_username,
                "admin_password": admin_password,
            },
            "network_profile": {
                "network_interfaces": [{"id": nic.id, "primary": True}],
            },
        }

        vm = compute_client.virtual_machines.begin_create_or_update(
            resource_group_name,
            vm_name,
            vm_parameters,
        ).result()

        print(f"Virtual Machine '{vm_name}' created successfully.")

    def stop_vm(self, resource_group_name, vm_name):
        """
        Stops a VM in Azure.

        :param resource_group_name: Name of the resource group containing the VM.
        :param vm_name: Name of the VM to stop.
        """
        try:
            print(f"Stopping VM '{vm_name}' in resource group '{resource_group_name}'...")
            operation = self.compute_client.virtual_machines.begin_power_off(resource_group_name, vm_name)
            operation.result()  # Wait for completion
            print(f"VM '{vm_name}' has been stopped successfully.")
        except Exception as e:
            print(f"Failed to stop VM '{vm_name}': {e}")


    def delete_vm(self, resource_group_name, vm_name) -> None:
        """
        Deletes a VM from Azure.

        :param resource_group_name: Name of the resource group containing the VM.
        :param vm_name: Name of the VM to delete.
        """
        try:
            print(f"Deleting VM '{vm_name}' in resource group '{resource_group_name}'...")
            operation = self.compute_client.virtual_machines.begin_delete(resource_group_name, vm_name)
            operation.result()  # Wait for completion
            print(f"VM '{vm_name}' has been deleted successfully.")
        except Exception as e:
            print(f"Failed to delete VM '{vm_name}': {e}")

    def configure_vm(self, virtual_machine) -> None:
        """Configures the virtual machine as per the Azure specifics."""
        print(f"Configuring VM for Azure account {self._account_name}...")

    def __str__(self):
        return f"\n  Provider-Azure:\n  Account Name: {self._account_name}\n  Connection Date: {self._connection_date}\n  Subscription ID: {self._subscription_id}\n  Client ID: {self._client_id}\n  Client Secret: {self._client_secret}\n  Tenant ID: {self._tenant_id}"
