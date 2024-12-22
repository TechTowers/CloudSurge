import sqlite3
from typing import List
import os

class Database:
    """Simulates a SQLite database and provides methods to interact with it."""

    def __init__(self, db_file: str = os.path.expanduser("~") + '/cloud_provider_db.sqlite'):
        self.db_file = db_file
        self.connection = None
        self.cursor = None

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

    def create_table_vm(self):
        """Creates the virtual machine table if not exists."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS virtual_machine (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vm_name TEXT NOT NULL,
                    provider_account_name TEXT,
                    is_active BOOLEAN,
                    is_configured BOOLEAN,
                    cost_limit INTEGER,
                    public_ip TEXT,
                    first_connection_date TEXT,
                    total_cost INTEGER,
                    total_uptime INTEGER,
                    FOREIGN KEY (provider_account_name) REFERENCES provider (account_name)
                );
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating virtual machine table: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def read_provider(self) -> List[dict]:
        """Reads and returns all provider information from the database."""
        try:
            self.cursor.execute("SELECT * FROM provider")
            rows = self.cursor.fetchall()
            providers = []
            for row in rows:
                provider = {
                    'account_name': row[0],
                    'connection_date': row[1],
                    'provider_info': row[2]
                }
                providers.append(provider)
            return providers
        except sqlite3.Error as e:
            print(f"Error reading provider data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while reading providers: {e}")
            raise

    def read_vm(self) -> List[dict]:
        """Reads and returns all virtual machine information from the database."""
        try:
            self.cursor.execute("SELECT * FROM virtual_machine")
            rows = self.cursor.fetchall()
            vms = []
            for row in rows:
                vm = {
                    'id': row[0],
                    'vm_name': row[1],
                    'provider_account_name': row[2],
                    'is_active': row[3],
                    'is_configured': row[4],
                    'cost_limit': row[5],
                    'public_ip': row[6],
                    'first_connection_date': row[7],
                    'total_cost': row[8],
                    'total_uptime': row[9]
                }
                vms.append(vm)
            return vms
        except sqlite3.Error as e:
            print(f"Error reading VM data: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while reading VMs: {e}")
            raise

    def insert_provider(self, provider: 'Provider') -> None:
        """Inserts a provider object into the provider table."""
        try:
            self.cursor.execute("""
                INSERT INTO provider (account_name, connection_date, provider_info)
                VALUES (?, ?, ?);
            """, (provider.get_account_name(), provider.get_connection_date(), ', '.join(provider.get_provider_info())))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting provider into database: {e}")
        except Exception as e:
            print(f"Unexpected error while inserting provider: {e}")

    def insert_vm(self, vm: 'VirtualMachine') -> None:
        """Inserts a virtual machine object into the virtual machine table."""
        try:
            self.cursor.execute("""
                INSERT INTO virtual_machine (vm_name, provider_account_name, is_active, is_configured,
                                              cost_limit, public_ip, first_connection_date,
                                              total_cost, total_uptime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (vm.get_vm_name(), vm.get_provider().get_account_name(), vm.get_is_active(),
                  vm.get_is_configured(), vm.get_cost_limit(), str(vm.get_public_ip()),
                  str(vm.get_first_connection_date()), vm.get_total_cost(), vm.get_total_uptime()))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting VM into database: {e}")
        except Exception as e:
            print(f"Unexpected error while inserting VM: {e}")

    def insert_multiple_providers(self, providers: List['Provider']) -> None:
        """Inserts multiple providers into the database."""
        for provider in providers:
            self.insert_provider(provider)

    def insert_multiple_vms(self, vms: List['VirtualMachine']) -> None:
        """Inserts multiple virtual machines into the database."""
        for vm in vms:
            self.insert_vm(vm)

    def close(self):
        """Closes the database connection and saves all changes."""
        if self.connection:
            self.connection.close()
