# author: Luka Pacar
import time
import digitalocean # From python-digitalocean
from datetime import date, datetime, timedelta, timezone

from backend import Database
from vm import VirtualMachine, Provider

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

    def connection_is_alive(self, print_output=True) -> bool:
        """Verifies if the DigitalOcean authentication works."""
        try:
            droplets = self.client.get_all_droplets()  # Correct way to list all droplets
            if droplets:
                print("\033[32mAuthenticated successfully. Found droplets.\033[0m") if print_output else None
                return True
            else:
                print("Authenticated successfully. No droplets found.") if print_output else None
                return True
        except Exception as e:
            print(f"Authentication failed: {e}") if print_output else None
            return False

    def create_vm(
            self,
            vm_name: str,
            ssh_key_ids: list,
            zerotier_network: str,
            ssh_key_path: str,
            location: str = "fra1",
            vm_size: str = "s-1vcpu-1gb",
            admin_password: str = "YourSecurePassword!",
            image_reference: str = "ubuntu-20-04-x64",
            max_retries: int = 10,  # Maximum retries for load
            retry_interval: int = 10,  # Time in seconds between each retry
            print_output=True
    ):
        """Creates a Droplet (VM) on DigitalOcean.

        Args:
            location (str): Location of the VM.
            vm_name (str): Name of the VM.
            vm_size (str): Size of the VM.
            admin_password (str): Admin password.
            image_reference (str): Image reference.
            ssh_key_ids (list): List of SSH key IDs.
            zerotier_network (str): ZeroTier network ID.
            ssh_key_path (str): Path to the SSH key file.
            max_retries (int): Maximum retries for load (until the VM gets an IP).
            retry_interval (int): Time in seconds between each Public-IP-Test-Retry.
            print_output (bool): Print outputs with useful info.
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
                print("\033[31mAPI token is missing.\033[0m")
                return None

            # Create the vm
            droplet = digitalocean.Droplet(**req)
            print(f"\033[31mVM '{vm_name}' is being created...\033[0m") if print_output else None

            # Initiate VM creation
            droplet.create()
            print(f"\033[32mVM '{vm_name}' has been created.\033[0m") if print_output else None
            # Retry mechanism to wait until the droplet is fully created and has an IP address
            retries = 0
            while retries < max_retries:
                try:
                    droplet.load()
                    if droplet.ip_address:
                        print(f'\033[32mDroplet/VM IP: {droplet.ip_address}\033[0m') if print_output else None
                        print(f"\033[32mSuccessfully created VM '{vm_name}'.\033[0m") if print_output else None
                        break
                    else:
                        print(f'\033[33mVM IP not available yet...\033[0m') if print_output else None
                except Exception as e:
                    print(f'\033[31mError loading droplet: {e}\033[0m')

                retries += 1
                time.sleep(retry_interval)  # Wait before retrying

            if retries == max_retries:
                print(f'\033[31mFailed to load droplet after {max_retries} retries.f\033[0m') if print_output else None
                return None


            # Return the VirtualMachine object after creation
            return VirtualMachine(
                vm_name,
                self,
                True,
                False,
                -1,
                droplet.ip_address,
                date.today(),
                "root",
                admin_password,
                zerotier_network,
                ssh_key_path
            )
        except Exception as e:  # General exception to catch all errors
            print(f"Failed to create VM '{vm_name}': {e}")
            return None

    def stop_vm(self, vm: VirtualMachine, print_output=True):
        """Stops (powers off) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.power_off()
            vm.set_is_active(False)
            print(f"VM '{vm.get_vm_name()}' has been powered off.") if print_output else None
        except Exception as e:
            print(f"Failed to stop VM '{vm.get_vm_name()}': {e}")

    def start_vm(self, vm: VirtualMachine, print_output=True):
        """Starts (powers on) a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.power_on()
            vm.set_is_active(True)
            print(f"VM '{vm.get_vm_name()}' has been powered on.") if print_output else None
        except Exception as e:
            print(f"Failed to start VM '{vm.get_vm_name()}': {e}")

    def delete_vm(self, vm: VirtualMachine, db: Database, print_output=True):
        """Deletes a VM on DigitalOcean."""
        try:
            droplet = self._get_droplet(vm)
            droplet.destroy()
            print(f"VM '{vm.get_vm_name()}' has been deleted.") if print_output else None
            if db:
                db.delete_vm(vm)
        except Exception as e:
            print(f"Failed to delete VM '{vm.get_vm_name()}': {e}")

    def get_vm_hourly_rate(self, vm: VirtualMachine, print_output=True) -> float:
        """
        Retrieves the hourly rate for the specified VM (Droplet).

        Args:
            vm (VirtualMachine): The virtual machine to query for hourly rate.
            print_output (bool): Print the output.

        Returns:
            float: The hourly rate for the VM in USD.
        """
        try:
            # Retrieve the droplet by name
            droplet = self._get_droplet(vm)

            # Match the droplet's size_slug with available sizes to get the hourly rate
            size_slug = droplet.size_slug  # Example: 's-1vcpu-1gb'
            sizes = self.client.get_all_sizes()  # Get all size options

            for size in sizes:
                if size.slug == size_slug:
                    hourly_rate = size.price_hourly
                    print(f"Hourly rate for VM '{vm.get_vm_name()}' ({size_slug}): ${hourly_rate:.4f} USD.") if print_output else None
                    return hourly_rate

            raise ValueError(f"Size slug '{size_slug}' not found in available sizes.")
        except Exception as e:
            print(f"Failed to retrieve hourly rate for VM '{vm.get_vm_name()}': {e}")
            return 0.0

    def get_vm_uptime(self, vm: VirtualMachine, print_output=True) -> timedelta:
        """
        Retrieves the total uptime of the specified VM (Droplet).

        Args:
            vm (VirtualMachine): The virtual machine to query for uptime.
            print_output (bool): Print the output.

        Returns:
            str: The total uptime in a human-readable format (e.g., '2 days, 3 hours, 15 minutes').
        """
        try:
            # Retrieve the droplet by name
            droplet = self._get_droplet(vm)

            # Parse the created_at timestamp
            creation_date = datetime.strptime(droplet.created_at, '%Y-%m-%dT%H:%M:%SZ')
            creation_date = creation_date.replace(tzinfo=timezone.utc)  # Ensure it's timezone-aware

            # Calculate uptime using UTC time
            current_time = datetime.now(timezone.utc)
            uptime_timedelta = current_time - creation_date

            print(f"Uptime for VM '{vm.get_vm_name()}': {uptime_timedelta}.") if print_output else None
            return uptime_timedelta
        except Exception as e:
            print(f"Failed to retrieve uptime for VM '{vm.get_vm_name()}': {e}")
            return timedelta(0)

    def get_vm_cost(self, vm: VirtualMachine, print_output=True) -> float:
        """
        Retrieves the total cost incurred by the specified VM (Droplet).

        Args:
            vm (VirtualMachine): The virtual machine to query for cost.
            print_output (bool): Print the output.

        Returns:
            float: The total cost for the VM in USD.
        """
        try:

            # Get hourly rate
            hourly_rate = self.get_vm_hourly_rate(vm, False)
            if hourly_rate == 0.0:
                raise ValueError(f"Hourly rate could not be retrieved for VM '{vm.get_vm_name()}'.")

            running_hours = self.get_vm_uptime(vm, False).total_seconds() / 3600

            # Calculate total cost
            total_cost = running_hours * hourly_rate
            print(f"VM '{vm.get_vm_name()}' has incurred a cost of ${total_cost:.2f} USD.") if print_output else None
            return total_cost
        except Exception as e:
            print(f"Failed to retrieve cost for VM '{vm.get_vm_name()}': {e}")
            return 0.0

    def _get_droplet(self, vm: VirtualMachine):
        """Finds and returns the droplet information."""
        droplets = self.client.get_all_droplets()
        for droplet in droplets:
            if droplet.name == vm.get_vm_name():
                return droplet
        raise ValueError(f"Droplet '{vm.get_vm_name()}' not found.")
