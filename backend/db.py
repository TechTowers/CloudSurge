# author: Luka Pacar 4CN
import sqlite3
from datetime import date
import re
import os

from backend import AWS
from backend.no_provider import NoProvider


# author: Luka Pacar
class Database:
    """Simulates a SQLite database and provides methods to interact with it."""

    _no_provider = NoProvider("No-Provider", date.today())

    def __init__(
        self,
        db_file: str = os.path.expanduser("~") + "/cloud_provider_db.sqlite",
    ):
        self.db_file = db_file
        self.connection = None
        self.cursor = None

    # Database Starting-Methods
    def init(self):
        """Initialize the database by creating tables for Provider and VirtualMachine if not exist."""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()

            self.create_table_provider()
            self.create_table_vm()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    # Provider
    def create_table_provider(self):
        """Creates the provider table if not exists, with account_name as PRIMARY KEY."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS provider (
                    account_name TEXT PRIMARY KEY,
                    connection_date TEXT NOT NULL,
                    provider_info TEXT
                );
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating provider table: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def insert_provider(self, provider, print_output=True) -> None:
        """Inserts a provider object into the provider table."""
        try:
            self.cursor.execute(
                """
                INSERT INTO provider (account_name, connection_date, provider_info)
                VALUES (?, ?, ?);
            """,
                (
                    provider.get_account_name(),
                    provider.get_connection_date(),
                    provider.get_provider_info(),
                ),
            )
            self.connection.commit()
            print(
                f"Provider with account_name '{provider.get_account_name()}' inserted successfully."
            ) if print_output else None
        except sqlite3.Error as e:
            print(f"Error inserting provider into database: {e}")
        except Exception as e:
            print(f"Unexpected error while inserting provider: {e}")

    def reload_provider(self, provider, print_output=True) -> None:
        """Deletes and re-inserts a provider object into the provider table."""
        self.delete_provider(provider, False)
        self.insert_provider(provider, False)
        print(
            f"Provider '{provider.get_account_name()}' reloaded successfully."
        ) if print_output else None

    def delete_provider(self, provider, print_output=True) -> None:
        """Deletes a provider from the provider table based on the account name."""
        try:
            # Execute the deletion query
            self.cursor.execute(
                """
                DELETE FROM provider
                WHERE account_name = ?;
            """,
                (provider.get_account_name(),),
            )
            self.connection.commit()  # Commit the transaction to the database
            print(
                f"Provider with account_name '{provider.get_account_name()}' deleted successfully."
            ) if print_output else None
        except sqlite3.Error as e:
            print(f"Error deleting provider from database: {e}")
        except Exception as e:
            print(f"Unexpected error while deleting provider: {e}")

    def read_provider(self):
        """Reads and returns all provider information from the database."""
        from backend import DigitalOcean

        try:
            self.cursor.execute("SELECT * FROM provider")
            rows = self.cursor.fetchall()
            providers = []
            for row in rows:
                provider = {
                    "account_name": row[0],
                    "connection_date": row[1],
                    "provider_info": row[2],
                }

                parts = re.split(r":", provider["provider_info"])
                provider_name = parts[0]
                if provider_name == "No-Provider":
                    providers.append(
                        NoProvider.from_provider_info(
                            provider["account_name"],
                            provider["connection_date"],
                            provider["provider_info"],
                        )
                    )
                elif provider_name == "DigitalOcean":
                    providers.append(
                        DigitalOcean.from_provider_info(
                            provider["account_name"],
                            provider["connection_date"],
                            provider["provider_info"],
                        )
                    )
                elif provider_name == "AWS":
                    providers.append(
                        AWS.from_provider_info(
                            provider["account_name"],
                            provider["connection_date"],
                            provider["provider_info"],
                        )
                    )

            return providers
        except sqlite3.Error as e:
            print(f"Error reading provider data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while reading providers: {e}")
            raise

    # VM

    def create_table_vm(self):
        """Creates the virtual machine table if not exists, with vm_name as PRIMARY KEY."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS virtual_machine (
                    vm_name TEXT PRIMARY KEY,
                    root_username TEXT,
                    root_password TEXT,
                    ssh_key TEXT,
                    zerotier_network TEXT,
                    provider_account_name TEXT,
                    cost_limit INTEGER,
                    public_ip TEXT,
                    first_connection_date TEXT,
                    FOREIGN KEY (provider_account_name) REFERENCES provider (account_name)
                );
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating virtual machine table: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def reload_vm(self, vm, print_output=True) -> None:
        """Deletes and re-inserts a virtual machine object into the virtual machine table."""
        self.delete_vm(vm)
        self.insert_vm(vm)
        print(
            f"Virtual machine '{vm.get_vm_name()}' reloaded successfully."
        ) if print_output else None

    def insert_vm(self, vm, print_output=True) -> None:
        """Inserts a virtual machine object into the virtual machine table."""
        try:
            self.cursor.execute(
                """
                INSERT INTO virtual_machine (vm_name,root_username,root_password,ssh_key,zerotier_network, provider_account_name, cost_limit, public_ip, first_connection_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
                (
                    vm.get_vm_name(),
                    vm.get_root_username(),
                    vm.get_password(),
                    vm.get_ssh_key(),
                    vm.get_zerotier_network(),
                    vm.get_provider().get_account_name(),
                    vm.get_cost_limit(),
                    str(vm.get_public_ip()),
                    str(vm.get_first_connection_date()),
                ),
            )
            self.connection.commit()
            print(
                f"Virtual machine '{vm.get_vm_name()}' inserted successfully."
            ) if print_output else None
        except sqlite3.Error as e:
            print(f"Error inserting VM into database: {e}")
        except Exception as e:
            print(f"Unexpected error while inserting VM: {e}")

    def delete_vm(self, vm, print_output=True) -> None:
        """Deletes a virtual machine from the virtual machine table based on the VM name."""
        try:
            # Execute the deletion query
            self.cursor.execute(
                """
                DELETE FROM virtual_machine
                WHERE vm_name = ?;
            """,
                (vm.get_vm_name(),),
            )
            self.connection.commit()  # Commit the transaction to the database
            print(
                f"Virtual machine '{vm.get_vm_name()}' deleted successfully."
            ) if print_output else None
        except sqlite3.Error as e:
            print(f"Error deleting virtual machine from database: {e}")
        except Exception as e:
            print(f"Unexpected error while deleting virtual machine: {e}")

    def read_vm(self, available_provider_accounts):
        """Reads and returns all virtual machine information from the database."""
        try:
            self.cursor.execute("SELECT * FROM virtual_machine")
            rows = self.cursor.fetchall()
            vms = []
            for row in rows:
                vm = {
                    "vm_name": row[0],
                    "root_username": row[1],
                    "root_password": row[2],
                    "ssh_key": row[3],
                    "zerotier_network": row[4],
                    "provider_account_name": row[5],
                    "cost_limit": row[6],
                    "public_ip": row[7],
                    "first_connection_date": row[8],
                }

                # Find the corresponding provider for the VM
                from backend import VirtualMachine

                for provider_account in available_provider_accounts:
                    if (
                        provider_account.get_account_name()
                        == vm["provider_account_name"]
                    ):
                        # Create VirtualMachine object with the full updated attributes
                        vms.append(
                            VirtualMachine(
                                vm["vm_name"],
                                provider_account,
                                vm["cost_limit"],
                                vm["public_ip"],
                                vm["first_connection_date"],
                                vm["root_username"],  # Pass root_username
                                vm["root_password"],  # Pass root_password
                                vm["zerotier_network"],  # Pass zerotier_network
                                vm["ssh_key"],  # SSH Key
                                False,
                            )
                        )
                        break

            return vms
        except sqlite3.Error as e:
            print(f"Error reading VM data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while reading VMs: {e}")
            raise

    # Database Ending-Methods
    def delete_database(self, print_output=True):
        """Deletes the entire database file."""
        try:
            self.close()
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                print(
                    "Database successfully deleted."
                ) if print_output else None
            else:
                print(f"Database file {self.db_file} does not exist.")
        except Exception as e:
            print(f"Error deleting database: {e}")

    def close(self):
        """Closes the database connection and saves all changes."""
        if self.connection:
            self.connection.close()

    @property
    def no_provider(self):
        return self._no_provider
