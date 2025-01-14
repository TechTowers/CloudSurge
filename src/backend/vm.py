# author: Luka Pacar
import os
from abc import abstractmethod, ABC
from datetime import date
from ipaddress import IPv4Address

import subprocess


class Provider(ABC):
    """Represents a Connection with no Provider. Typically skipping the vm-creation step and using ssh"""

    delimiter = ",,,"
    starting_character = ":"

    def __init__(self, account_name: str, connection_date: date):
        self._account_name = account_name
        self._connection_date = connection_date

    @staticmethod
    @abstractmethod
    def from_provider_info(
        account_name: str, connection_date: date, provider_info: str
    ):
        """Creates a Provider object from the provider information.

        Args:
            account_name (str): Account name.
            connection_date (date): Connection date.
            provider_info (str): Provider information.

        Returns:
            Provider: Provider object.
        """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the name of the provider."""

    @abstractmethod
    def get_provider_info(self) -> str:
        """Returns a list of provider-related information."""

    def get_connection_date(self) -> date:
        """Get the connection date."""
        return self._connection_date

    def get_account_name(self) -> str:
        """Returns the name of this account"""
        return self._account_name

    @abstractmethod
    def is_active(self, vm):
        """Check if the connection is active."""

    @abstractmethod
    def get_vm_cost(self, vm):
        """Get the cost of the virtual machine."""

    @abstractmethod
    def get_vm_uptime(self, vm):
        """Get the uptime of the virtual machine."""

    @abstractmethod
    def get_vm_hourly_rate(self, vm):
        """Get the hourly rate of the virtual machine."""

    @abstractmethod
    def create_vm(self, *args, **kwargs):
        """Create a virtual machine."""

    @abstractmethod
    def stop_vm(self, virtual_machine) -> None:
        """Stop the virtual machine."""

    @abstractmethod
    def delete_vm(self, virtual_machine, db) -> None:
        """Delete the virtual machine."""

    @abstractmethod
    def start_vm(self, virtual_machine) -> None:
        """Start the virtual machine."""

    def __str__(self):
        return f"Account Name: {self._account_name}, Connection Date: {self._connection_date}"


class VirtualMachine:
    """Class representing a virtual machine."""

    def __init__(
        self,
        vm_name: str,
        provider: Provider,
        cost_limit: int,
        public_ip: str,
        first_connection_date: date,
        root_username: str,
        password: str,
        zerotier_network: str,
        ssh_key: str,
        new_vm: bool = True,
    ):
        self._vm_name = vm_name
        from .db import Database

        if provider is None:
            self._provider = Database.no_provider
        else:
            self._provider = provider
        self._cost_limit = cost_limit
        self._public_ip = IPv4Address(public_ip)
        self._first_connection_date = first_connection_date
        self._root_username = root_username
        self._password = password
        self._zerotier_network = zerotier_network
        self._ssh_key = ssh_key

    def is_reachable(self):
        """Check if the virtual machine is reachable."""
        process = subprocess.call(
            [
                "flatpak-spawn",
                "--host",
                "--",
                "ssh",
                f"{self.get_root_username()}@{str(self.get_public_ip())}",
                "-i",
                f"{self.get_ssh_key()}",
                "-o",
                "StrictHostKeyChecking=no",
                "echo exit",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )

        return process == 0

    def install_vm(self):
        """Installs CloudSurge specific data on the virtual machine."""
        proc = subprocess.run(
            [
                "flatpak-spawn",
                "--host",
                os.path.expandvars("$XDG_DATA_HOME/cloudsurge.sh"),
                "-s",
                f"{self.get_root_username()}@{str(self.get_public_ip())}",
                "-k",
                self.get_ssh_key(),
                "-i",
                "-p",
            ],
            input=f"{self.get_password()}\n",
            capture_output=True,
            check=True,
            text=True,
        )
        print(proc.stdout)

    def configure_vm(self):
        """Configures the virtual machine using the cloudsurge-script."""
        proc = subprocess.run(
            [
                "flatpak-spawn",
                "--host",
                os.path.expandvars("$XDG_DATA_HOME/cloudsurge.sh"),
                "-s",
                f"{self.get_root_username()}@{str(self.get_public_ip())}",
                "-k",
                self.get_ssh_key(),
                "-c",
                "-z",
                self.get_zerotier_network(),
                "-p",
            ],
            input=f"{self.get_password()}\n",
            capture_output=True,
            check=True,
            text=True,
        )
        print(proc.stdout)

    # Setters
    def set_zerotier_network(self, zerotier_network: str):
        """Set the zerotier network."""
        self._zerotier_network = zerotier_network

    def set_cost_limit(self, cost_limit: int):
        """Set the cost limit for the virtual machine."""
        self._cost_limit = cost_limit

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
        return (
            f"\n VirtualMachine:\n"
            f" VM Name: {self._vm_name}\n"
            f" Provider: {self._provider.get_provider_name()}\n"
            f" Cost Limit: ${self._cost_limit}\n"
            f" Public IP: {self._public_ip}\n"
            f" First Connection Date: {self._first_connection_date}\n"
            f" Root Username: {self._root_username}\n"
            f" ZeroTier Network: {self._zerotier_network}"
        )
