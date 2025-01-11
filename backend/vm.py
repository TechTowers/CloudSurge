# author: Luka Pacar
import os
from abc import abstractmethod, ABC
from datetime import date
from ipaddress import IPv4Address

import subprocess

import requests


def get_cloudsurge_script():
    """ Retrieves the CloudSurge script from the GitHub repository and saves it to the local filesystem. """
    file_path = "~/.local/bin/cloudsurge.sh"
    url = "https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/development/scripts/cloudsurge.sh"

    if not os.path.exists(".local/bin"):
        os.makedirs(".local/bin")

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

class Provider(ABC):
    """Represents a Connection with no Provider. Typically skipping the vm-creation step and using ssh"""

    delimiter = ",,,"
    starting_character = ":"

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
        if provider is None:
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

    def install_vm(self):
        """Installs CloudSurge specific data on the virtual machine."""
        get_cloudsurge_script()
        process = subprocess.Popen([
            "~/.local/bin/cloudsurge.sh",
            "-s", f"{self.get_root_username()}@{self.get_public_ip()}",
            "-k", self.get_ssh_key(),
            "-i"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.stdin.write(f"{self.get_password()}\n".encode("utf-8"))

    def configure_vm(self):
        """Configures the virtual machine using the cloudsurge-script."""
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
        process.stdin.write(f"{self.get_password()}\n".encode("utf-8"))
        pass

    # Setters
    def set_zerotier_network(self, zerotier_network: str):
        """Set the zerotier network."""
        self._zerotier_network = zerotier_network

    def set_is_active(self, is_active: bool):
        """Set the active status of the virtual machine."""
        self._is_active = is_active

    def set_cost_limit(self, cost_limit: int):
        """Set the cost limit for the virtual machine."""
        self._cost_limit = cost_limit

    def set_is_configured(self, is_configured: bool):
        """Set the configured status of the virtual machine."""
        self._is_configured = is_configured

    # Getters
    def get_zerotier_network(self) -> str:
        """Get the zerotier network."""
        return self._zerotier_network

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
        """Get the provider object."""
        return self._provider

    def get_is_active(self) -> bool:
        """Check if the virtual machine is active."""
        return self._is_active

    def get_is_configured(self) -> bool:
        """Check if the virtual machine is configured."""
        return self._is_configured

    def get_cost_limit(self) -> int:
        """Get the cost limit for the virtual machine."""
        return self._cost_limit

    def get_public_ip(self) -> IPv4Address:
        """Get the public IP address of the virtual machine."""
        return self._public_ip

    def get_first_connection_date(self) -> date:
        """Get the first connection date of the virtual machine."""
        return self._first_connection_date

    def get_ssh_key(self) -> str:
        """Get the ssh key."""
        return self._ssh_key

    # toString
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