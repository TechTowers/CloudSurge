from abc import abstractmethod, ABC
from datetime import date
from ipaddress import IPv4Address


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

    def get_account_name(self) -> str:
        """Returns the name of this account"""
        return self._account_name

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
    def configure_vm(self, virtual_m) -> None:
        """Configures the virtual machine."""
        pass

    def get_connection_date(self) -> date:
        """Get the connection date."""
        return self._connection_date

    def __str__(self):
        return f"Account Name: {self._account_name}, Connection Date: {self._connection_date}"


class VirtualMachine:
    """Class representing a virtual machine."""

    def __init__(self, vm_name: str, provider: Provider, is_active: bool, is_configured: bool,
                 cost_limit: int, public_ip: str, first_connection_date: date):
        self._vm_name = vm_name
        self._provider = provider
        self._is_active = is_active
        self._is_configured = is_configured
        self._cost_limit = cost_limit
        self._public_ip = IPv4Address(public_ip)
        self._first_connection_date = first_connection_date

    def get_vm_name(self) -> str:
        """Get the virtual machine name."""
        return self._vm_name

    def set_vm_name(self, vm_name: str):
        """Set the virtual machine name.

        Args:
            vm_name (str): New virtual machine name.
        """
        self._vm_name = vm_name

    def get_provider(self) -> Provider:
        """Get the provider object.

        Returns:
            Provider: Provider object.
        """
        return self._provider

    def set_provider(self, provider: Provider):
        """Set the provider object.

        Args:
            provider (Provider): New provider object.
        """
        self._provider = provider

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

    def set_public_ip(self, public_ip: str):
        """Set the public IP address of the virtual machine.

        Args:
            public_ip (str): New public IP address.
        """
        self._public_ip = IPv4Address(public_ip)

    def get_first_connection_date(self) -> date:
        """Get the first connection date of the virtual machine.

        Returns:
            date: First connection date.
        """
        return self._first_connection_date

    def set_first_connection_date(self, first_connection_date: date):
        """Set the first connection date of the virtual machine.

        Args:
            first_connection_date (date): New first connection date.
        """
        self._first_connection_date = first_connection_date



    def __str__(self):
        return f"\n VirtualMachine:\n VM Name: {self._vm_name}\n Provider: {self._provider.get_provider_name()}\n Active: {self._is_active}\n Configured: {self._is_configured}\n Cost Limit: ${self._cost_limit}\n Public IP: {self._public_ip}\n First Connection Date: {self._first_connection_date}"

    def print_info(self):
        """Print information about the virtual machine."""
        print(self.__str__())