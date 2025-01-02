from datetime import date
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from vm import VirtualMachine
from vm import Provider

#author: Luka Pacar
class Azure(Provider):
    """Azure cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, subscription_id: str, client_id: str, client_secret: str, tenant_id: str, resource_group_name: str):
        super().__init__(account_name, connection_date)
        # Set-Up Credentials:
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self.provider_info_string = self.get_provider_name() + self.starting_character+ f"{self._subscription_id}{self.delimiter}{client_id}{self.delimiter}{client_secret}{self.delimiter}{tenant_id}{self.delimiter}{resource_group_name}"
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
        self.compute_client = ComputeManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)

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
        provider_info = provider_info.split(Provider.delimiter)
        return Azure(account_name, connection_date, provider_info[0], provider_info[1], provider_info[2], provider_info[3], provider_info[4])

    def get_provider_name(self) -> str:
        """Returns the name of the provider (Azure)."""
        return "Azure"

    def get_provider_info(self) -> str:
        """Returns information about the provider (Provider, SubscriptionID, ClientID, ClientSecret, TenantID)."""
        return self.provider_info_string

    def connection_is_alive(self) -> bool:
        """
        Verifies if the Azure authentication works by attempting to list subscriptions.

        :return: True if authentication works, False otherwise.
        """
        try:
            subscription_client = SubscriptionClient(self.credential)  # Uses the Azure Credential
            subscriptions = list(subscription_client.subscriptions.list())
            print(f"Authenticated successfully. Found {len(subscriptions)} subscriptions.")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def create_vm(
            self,
            location: str,
            vm_name: str,
            vm_size: str,
            admin_username: str,
            admin_password: str,
            image_reference: dict,
            network_vnet_name: str,
            network_subnet_name: str,
            public_ip_name: str,
            nic_name: str,
            zerotier_network: str,
            ssh_key_path: str
    ):
        """Creates a VM in Azure.

          Args:
            location (str): Location of the VM.
            vm_name (str): Name of the VM.
            vm_size (str): Size of the VM.
            admin_username (str): Admin username.
            admin_password (str): Admin password.
            image_reference (dict): Image reference.
            network_vnet_name (str): Virtual Network name.
            public_ip_name (str): Public IP name.
            nic_name (str): Network Interface name.
            zerotier_network (str): ZeroTier network ID.
            ssh_key_path (str): Path to the SSH key file.
        """

        # Step 1: Create Resource Group
        self.resource_client.resource_groups.create_or_update(
            self._resource_group_name,
            {"location": location}
        )

        # Step 2: Create Virtual Network and Subnet
        self.network_client.virtual_networks.begin_create_or_update(
            self._resource_group_name,
            network_vnet_name,
            {
                "location": location,
                "address_space": {"address_prefixes": ["10.0.0.0/16"]},
            },
        ).result()

        subnet = self.network_client.subnets.begin_create_or_update(
            self._resource_group_name,
            network_vnet_name,
            network_subnet_name,
            {"address_prefix": "10.0.0.0/24"},
        ).result()

        # Step 3: Create Public IP Address
        public_ip = self.network_client.public_ip_addresses.begin_create_or_update(
            self._resource_group_name,
            public_ip_name,
            {
                "location": location,
                "sku": {"name": "Basic"},
                "public_ip_allocation_method": "Dynamic",
            },
        ).result()

        # Step 4: Create Network Interface
        nic = self.network_client.network_interfaces.begin_create_or_update(
            self._resource_group_name,
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

        self.compute_client.virtual_machines.begin_create_or_update(
            self._resource_group_name,
            vm_name,
            vm_parameters,
        ).result()

        print(f"Virtual Machine '{vm_name}' created successfully.")
        return VirtualMachine(vm_name, self, True, False, 10000000000, public_ip.ip_address, date.today(), admin_username, admin_password, zerotier_network, ssh_key_path)

    def stop_vm(self, vm: VirtualMachine):
        """
        Stops a VM in Azure.

        :param vm: Name of the VM to stop.
        """
        name = vm.get_vm_name()
        try:
            print(f"Stopping VM '{name}' in resource group '{self._resource_group_name}'...")
            operation = self.compute_client.virtual_machines.begin_power_off(self._resource_group_name, name)
            operation.result()  # Wait for completion
            vm.set_is_active(False)
            print(f"VM '{name}' has been stopped successfully.")
        except Exception as e:
            print(f"Failed to stop VM '{name}': {e}")


    def start_vm(self, vm: VirtualMachine):
        """
        Starts a VM in Azure.

        :param vm: The VM instance containing the name.
        """
        name = vm.get_vm_name()
        try:
            print(f"Starting VM '{name}' in resource group '{self._resource_group_name}'...")
            operation = self.compute_client.virtual_machines.begin_start(self._resource_group_name, name)
            operation.result()  # Wait for completion
            vm.set_is_active(True)
            print(f"VM '{name}' has been started successfully.")
        except Exception as e:
            print(f"Failed to start VM '{name}': {e}")


    def delete_vm(self, vm: VirtualMachine) -> None:
        """
        Deletes a VM from Azure.

        :param vm: Name of the VM to delete.
        """
        name = vm.get_vm_name()
        try:
            print(f"Deleting VM '{name}' in resource group '{self._resource_group_name}'...")
            operation = self.compute_client.virtual_machines.begin_delete(self._resource_group_name, name)
            operation.result()  # Wait for completion
            print(f"VM '{name}' has been deleted successfully.")
        except Exception as e:
            print(f"Failed to delete VM '{name}': {e}")

    def __str__(self):
        return f"\n  Provider-Azure:\n  Account Name: {self._account_name}\n  Connection Date: {self._connection_date}\n Info: {self.provider_info_string}\n"
