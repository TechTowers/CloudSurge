import datetime

class VirtualMachine:
    """
    A class to represent a virtual machine with attributes for public IP, password, username, and other details.
    """

    def __init__(self, name: str, password: str, public_ip: str, provider: str, username: str, connection_date: datetime.datetime, total_cost: float):
        """
        Initialize the Virtual Machine with a name, password, public IP, username, connection date, and total cost.

        Args:
            name (str): The name of the virtual machine.
            password (str): The password of the virtual machine.
            public_ip (str): The public IP address of the virtual machine.
            provider (str): The provider of the virtual machine.
            username (str): The username associated with the virtual machine.
            connection_date (datetime): The connection date of the virtual machine.
            total_cost (float): The total cost associated with the virtual machine.
        """
        self._name = name
        self._password = password
        self._public_ip = public_ip
        self._provider = provider
        self._username = username
        self._connection_date = connection_date
        self._total_cost = total_cost

    # Getter and setter for name
    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    # Getter and setter for provider
    def get_provider(self) -> str:
        return self._provider

    def set_provider(self, provider: str):
        self._provider = provider

    # Getter and setter for public IP
    def get_public_ip(self) -> str:
        return self._public_ip

    def set_public_ip(self, public_ip: str):
        self._public_ip = public_ip

    # Getter and setter for username
    def get_username(self) -> str:
        return self._username

    def set_username(self, username: str):
        self._username = username

    # Getter and setter for connection date
    def get_connection_date(self) -> datetime.datetime:
        return self._connection_date

    def set_connection_date(self, connection_date: datetime.datetime):
        self._connection_date = connection_date

    # Getter and setter for total cost
    def get_total_cost(self) -> float:
        return self._total_cost

    def set_total_cost(self, total_cost: float):
        self._total_cost = total_cost

    # Getter and setter for password
    def get_password(self) -> str:
        return self._password

    def set_password(self, password: str):
        self._password = password

    def __str__(self):
        return f"VirtualMachine(Name: {self._name}, Public IP: {self._public_ip}, Username: {self._username}, Connection Date: {self._connection_date}, Total Cost: {self._total_cost})"
