import pydo
from datetime import date
from vm import VirtualMachine, Provider

#author: Luka Pacar
class DigitalOcean(Provider):
    """DigitalOcean cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, token: str):
        super().__init__(account_name, connection_date)
        self.token = token
        self.client = pydo.Client(self.token)  # Initialize the PyDo Client with the token
        self.provider_info_string = self.get_provider_name() + self.starting_character + f"{self.token}"

    @staticmethod
    def from_provider_info(account_name: str, connection_date: date, provider_info: str):
        """Creates a Provider object from the provider information."""
        return DigitalOcean(account_name, connection_date, provider_info)

    def get_provider_name(self) -> str:
        """Returns the name of the provider (DigitalOcean)."""
        return "DigitalOcean"

    def get_provider_info(self) -> str:
        """Returns information about the provider (token)."""
        return self.provider_info_string

    def connection_is_alive(self) -> bool:
        """Verifies if the DigitalOcean authentication works."""
        try:
            # Instead of using account_info(), check droplets directly to verify access
            droplets = self.client.droplets.list()  # List all droplets to check authentication
            if droplets:
                print("Authenticated successfully. Found droplets.")
                return True
            else:
                print("Authenticated successfully. No droplets found.")
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
            image_reference: str,
            ssh_key_ids: list,
            zerotier_network: str = "",
            ssh_key_path: str = ""
    ):
        """Creates a Droplet (VM) on DigitalOcean.

        Args:
            location (str): Location of the VM.
            vm_name (str): Name of the VM.
            vm_size (str): Size of the VM.
            admin_username (str): Admin username.
            admin_password (str): Admin password.
            image_reference (str): Image reference.
            ssh_key_ids (list): List of SSH key IDs.
            zerotier_network (str): ZeroTier network ID.
            ssh_key_path (str): Path to the SSH key file.
        """
        try:
            # Creating droplet on DigitalOcean using the PyDo client
            droplet = self.client.droplets.create(
                name=vm_name,
                region=location,
                size=vm_size,
                image=image_reference,
                ssh_keys=ssh_key_ids
            )
            print(f"VM '{vm_name}' is being created.")

            # Retrieve droplet information to access its IP and other info
            droplet = self.client.droplets.get(droplet['id'])

            # Check public IP address from the droplet information (waiting for network info)
            ip_address = None
            if 'networks' in droplet:
                for network in droplet['networks']['v4']:
                    if network.get('type') == 'public':
                        ip_address = network['ip_address']
                        break

            # Return the VirtualMachine object
            return VirtualMachine(
                vm_name,
                self,
                True,
                False,
                1000000,
                ip_address or "Pending",
                date.today(),
                admin_username,
                admin_password,
                zerotier_network,
                ssh_key_path
            )
        except Exception as e:
            print(f"Failed to create VM '{vm_name}': {e}")
            return None

    def stop_vm(self, vm: VirtualMachine):
        """Stops (powers off) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            self.client.droplets.power_off(droplet['id'])
            vm.set_is_active(False)
            print(f"VM '{vm.get_vm_name()}' has been powered off.")
        except Exception as e:
            print(f"Failed to stop VM '{vm.get_vm_name()}': {e}")

    def start_vm(self, vm: VirtualMachine):
        """Starts (powers on) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            self.client.droplets.power_on(droplet['id'])
            vm.set_is_active(True)
            print(f"VM '{vm.get_vm_name()}' has been powered on.")
        except Exception as e:
            print(f"Failed to start VM '{vm.get_vm_name()}': {e}")

    def delete_vm(self, vm: VirtualMachine):
        """Deletes a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            self.client.droplets.delete(droplet['id'])
            print(f"VM '{vm.get_vm_name()}' has been deleted.")
        except Exception as e:
            print(f"Failed to delete VM '{vm.get_vm_name()}': {e}")

    def _get_droplet(self, vm: VirtualMachine):
        """Finds and returns the droplet information."""
        droplets = self.client.droplets.list()
        for droplet in droplets:
            if droplet['name'] == vm.get_vm_name():
                return droplet
        raise ValueError(f"Droplet '{vm.get_vm_name()}' not found.")
