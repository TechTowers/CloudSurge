import time
import digitalocean
from datetime import date

from backend import Database
from vm import VirtualMachine, Provider

# author: Luka Pacar
class DigitalOcean(Provider):
    """DigitalOcean cloud provider implementation."""

    def __init__(self, account_name: str, connection_date: date, token: str):
        super().__init__(account_name, connection_date)
        self.provider_info_string = self.get_provider_name() + self.starting_character + f"{token}"
        self.token = token
        self.client = digitalocean.Manager(token=self.token)  # Initialize the PyDo Client with the token
        self.provider_info_string = self.get_provider_name() + self.starting_character + f"{self.token}"

    @staticmethod
    def from_provider_info(account_name: str, connection_date: date, provider_info: str):
        """Creates a Provider object from the provider information."""
        provider_info = provider_info.split(Provider.starting_character)[1]
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
            droplets = self.client.get_all_droplets()  # Correct way to list all droplets
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
            admin_password: str,
            image_reference: str,
            ssh_key_ids: list,
            zerotier_network: str = "",
            ssh_key_path: str = "",
            max_retries: int = 10,  # Maximum retries for load
            retry_interval: int = 10  # Time in seconds between each retry
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
            max_retries (int): Maximum retries for load (until the VM gets an IP).
            retry_interval (int): Time in seconds between each Public-IP-Test-Retry.
        """
        try:
            req = {
                "token": self.token,
                "name": vm_name,
                "region": location,
                "size": vm_size,
                "image": image_reference,
                "ssh_keys": ssh_key_ids,
                "backups": False,
                "ipv6": False,
                "monitoring": False,
            }

            if not self.token:
                print("API token is missing.")
                return None

            # Create the vm
            droplet = digitalocean.Droplet(**req)
            print(f"VM '{vm_name}' is being created...")

            # Initiate VM creation
            droplet.create()

            # Retry mechanism to wait until the droplet is fully created and has an IP address
            retries = 0
            while retries < max_retries:
                try:
                    droplet.load()
                    if droplet.ip_address:
                        print(f'Droplet IP: {droplet.ip_address}')
                        break
                    else:
                        print("Droplet IP not available yet...")
                except Exception as e:
                    print(f"Error loading droplet: {e}")

                retries += 1
                time.sleep(retry_interval)  # Wait before retrying

            if retries == max_retries:
                print(f"Failed to load droplet after {max_retries} retries.")


            # Return the VirtualMachine object after creation
            return VirtualMachine(
                vm_name,
                self,
                True,
                False,
                1000000,  # Approximate cost, you can adjust this based on your pricing
                droplet.ip_address or "Pending",
                date.today(),
                "root",
                admin_password,
                zerotier_network,
                ssh_key_path
            )
        except Exception as e:  # General exception to catch all errors
            print(f"Failed to create VM '{vm_name}': {e}")
            return None

    def stop_vm(self, vm: VirtualMachine):
        """Stops (powers off) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.power_off()
            vm.set_is_active(False)
            print(f"VM '{vm.get_vm_name()}' has been powered off.")
        except Exception as e:
            print(f"Failed to stop VM '{vm.get_vm_name()}': {e}")

    def start_vm(self, vm: VirtualMachine):
        """Starts (powers on) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.power_on()
            vm.set_is_active(True)
            print(f"VM '{vm.get_vm_name()}' has been powered on.")
        except Exception as e:
            print(f"Failed to start VM '{vm.get_vm_name()}': {e}")

    def delete_vm(self, vm: VirtualMachine, db: Database):
        """Deletes a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.destroy()
            print(f"VM '{vm.get_vm_name()}' has been deleted.")
            if db:
                db.delete_vm(vm)
        except Exception as e:
            print(f"Failed to delete VM '{vm.get_vm_name()}': {e}")

    def _get_droplet(self, vm: VirtualMachine):
        """Finds and returns the droplet information."""
        droplets = self.client.get_all_droplets()
        for droplet in droplets:
            if droplet.name == vm.get_vm_name():
                return droplet
        raise ValueError(f"Droplet '{vm.get_vm_name()}' not found.")
