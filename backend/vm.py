from abc import abstractmethod, ABC
from datetime import date
from ipaddress import IPv4Address

import subprocess

import paramiko

from backend import get_cloudsurge_script


class Provider(ABC):
    """Abstract class for a cloud provider."""

    def __init__(self, account_name: str, connection_date: date):
        self._account_name = account_name
        self._connection_date = connection_date

    @staticmethod
    @abstractmethod
    def from_provider_info(account_name: str, connection_date: date, provider_info: str):
        """Creates a Provider object from the provider information.

        Args:
            account_name (str): Account name.
            connection_date (date): Connection date.
            provider_info (str): Provider information.

        Returns:
            Provider: Provider object.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the name of the provider."""
        pass

    @abstractmethod
    def get_provider_info(self) -> str:
        """Returns a list of provider-related information."""
        pass

    @abstractmethod
    def create_vm(self) -> None:
        """Creates or starts a virtual machine."""
        pass

    @abstractmethod
    def stop_vm(self, virtual_machine) -> None:
        """Stops the virtual machine if it exists."""
        pass

    @abstractmethod
    def delete_vm(self, virtual_machine) -> None:
        """Deletes the virtual machine if it exists."""
        pass

    @abstractmethod
    def connection_is_alive(self) -> str:
        """Returns if the connection to the provider is still alive"""

        pass

    def get_connection_date(self) -> date:
        """Get the connection date."""
        return self._connection_date

    def get_account_name(self) -> str:
        """Returns the name of this account"""
        return self._account_name

    def __str__(self):
        return f"Account Name: {self._account_name}, Connection Date: {self._connection_date}"


class VirtualMachine:
    """Class representing a virtual machine."""

    def __init__(self, vm_name: str, provider: Provider, is_active: bool, is_configured: bool,
                 cost_limit: int, public_ip: str, first_connection_date: date, root_username: str, password: str, zerotier_network: str, ssh_key:str):
        self._vm_name = vm_name
        from backend import Database
        if (provider == None):
            self._provider = Database.no_provider
        else:
            self._provider = provider
        self._is_active = is_active
        self._is_configured = is_configured
        self._cost_limit = cost_limit
        self._public_ip = IPv4Address(public_ip)
        self._first_connection_date = first_connection_date
        self._root_username = root_username
        self._password = password
        self._zerotier_network = zerotier_network
        self._ssh_key = ssh_key

    def is_reachable(self):
        """Checks if the virtual machine is reachable via SSH."""
        try:
            # Initialize SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown host keys


            # Attempt to establish an SSH connection
            ssh.connect(str(self._public_ip), username=self._root_username, password=self._password, timeout=15)

            # If we reach here, the VM is reachable
            ssh.close()  # Close the SSH connection after test
            return True
        except paramiko.AuthenticationException:
            print(f"SSH Authentication failed for VM: {self._vm_name}")
            return False
        except paramiko.SSHException as e:
            print(f"SSH connection failed for VM {self._vm_name}: {str(e)}")
            return False
        except Exception as e:
            print(f"An error occurred while testing SSH connection for VM {self._vm_name}: {str(e)}")
            return False

    def install_vm(self):
        get_cloudsurge_script()
        subprocess.run([
            "~/.local/bin/cloudsurge.sh",
            "-s", f"{self.get_root_username()}@{self.get_public_ip()}",
            "-k", self.get_ssh_key(),
            "-i"
        ])

    def configure_vm(self):
        from backend import get_cloudsurge_script
        get_cloudsurge_script()
        process = subprocess.Popen([
            "~/.local/bin/cloudsurge.sh",
            "-s", f"{self.get_root_username()}@{self.get_public_ip()}",
            "-k", self.get_ssh_key(),
            "-c",
            "-z", self.get_zerotier_network()],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        pass

    def get_zerotier_network(self) -> str:
        """Get the zerotier network."""
        return self._zerotier_network

    def set_zerotier_network(self, zerotier_network: str):
        """Set the zerotier network.

        Args:
            zerotier_network (str): New zerotier network.
        """
        self._zerotier_network = zerotier_network

    def get_root_username(self) -> str:
        """Get the root username."""
        return self._root_username

    def get_password(self) -> str:
        """Get the root password."""
        return self._password

    def get_vm_name(self) -> str:
        """Get the virtual machine name."""
        return self._vm_name

    def get_provider(self) -> Provider:
        """Get the provider object.

        Returns:
            Provider: Provider object.
        """
        return self._provider

    def get_is_active(self) -> bool:
        """Check if the virtual machine is active.

        Returns:
            bool: True if active, otherwise False.
        """
        return self._is_active

    def set_is_active(self, is_active: bool):
        """Set the active status of the virtual machine.

        Args:
            is_active (bool): Active status.
        """
        self._is_active = is_active

    def get_is_configured(self) -> bool:
        """Check if the virtual machine is configured.

        Returns:
            bool: True if configured, otherwise False.
        """
        return self._is_configured

    def set_is_configured(self, is_configured: bool):
        """Set the configured status of the virtual machine.

        Args:
            is_configured (bool): Configured status.
        """
        self._is_configured = is_configured

    def get_cost_limit(self) -> int:
        """Get the cost limit for the virtual machine.

        Returns:
            int: Cost limit.
        """
        return self._cost_limit

    def set_cost_limit(self, cost_limit: int):
        """Set the cost limit for the virtual machine.

        Args:
            cost_limit (int): New cost limit.
        """
        self._cost_limit = cost_limit

    def get_public_ip(self) -> IPv4Address:
        """Get the public IP address of the virtual machine.

        Returns:
            IPv4Address: Public IP address.
        """
        return self._public_ip
    def get_first_connection_date(self) -> date:
        """Get the first connection date of the virtual machine.

        Returns:
            date: First connection date.
        """
        return self._first_connection_date
    def get_ssh_key(self) -> str:
        """Get the ssh key."""
        return self._ssh_key

    def __str__(self):
        return f"\n VirtualMachine:\n" \
               f" VM Name: {self._vm_name}\n" \
               f" Provider: {self._provider.get_provider_name()}\n" \
               f" Active: {self._is_active}\n" \
               f" Configured: {self._is_configured}\n" \
               f" Cost Limit: ${self._cost_limit}\n" \
               f" Public IP: {self._public_ip}\n" \
               f" First Connection Date: {self._first_connection_date}\n" \
               f" Root Username: {self._root_username}\n" \
               f" ZeroTier Network: {self._zerotier_network}"

    def print_info(self):
        """Print information about the virtual machine."""
        print(self.__str__())