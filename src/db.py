import datetime
import sqlite3
import os

from src.vm import VirtualMachine

class SQLiteServer:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Connect to the SQLite database. If the file does not exist, it will be created automatically."""
        self.connection = sqlite3.connect(self.db_name)
        self.createPasswordDatabase()

    def close(self):
        """Close the connection to the database."""
        if self.connection:
            self.connection.close()

    def createPasswordDatabase(self):
        """Create a table to store VM details including username, provider, and total cost."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vm_passwords (
                vm_name TEXT PRIMARY KEY,         -- vm_name is unique, primary key
                password TEXT NOT NULL,           -- password cannot be NULL
                name TEXT NOT NULL,               -- VM name or label
                public_ip TEXT NOT NULL,          -- VM's public IP address
                provider TEXT,                    -- Provider
                username TEXT,                    -- Username
                connection_date DATETIME NOT NULL, -- Date and time the VM was connected
                total_cost REAL NOT NULL          -- Total cost associated with the VM
            )
        """)
        self.connection.commit()

    def addEntry(self, vm):
        """Add a VM entry to the database, or update it if it already exists."""
        cursor = self.connection.cursor()
        cursor.execute("""
        INSERT INTO vm_passwords (vm_name, password, name, public_ip, provider, username, connection_date, total_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(vm_name) DO UPDATE SET 
            password = ?, 
            name = ?, 
            public_ip = ?, 
            provider = ?, 
            username = ?, 
            connection_date = ?, 
            total_cost = ?
    """, (
            vm.get_name(),
            vm.get_password(),
            vm.get_name(),
            vm.get_public_ip(),
            vm.get_provider(),
            vm.get_username(),  # Adding username here
            vm.get_connection_date(),
            vm.get_total_cost(),
            vm.get_password(),
            vm.get_name(),
            vm.get_public_ip(),
            vm.get_provider(),
            vm.get_username(),  # Adding username here too
            vm.get_connection_date(),
            vm.get_total_cost()
        ))  # Insert or update the virtual machine attributes including username
        self.connection.commit()

    def getAllVMs(self):
        """Retrieve all VM entries from the database and return them as a list of VirtualMachine objects."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT vm_name, password, name, public_ip, provider, username, connection_date, total_cost
            FROM vm_passwords
        """)

        # Fetch all rows from the query result
        rows = cursor.fetchall()

        # Create a list to store the VirtualMachine objects
        vm_list = []

        # Iterate through the rows and create VirtualMachine objects
        for row in rows:
            vm_name, password, name, public_ip, provider, username, connection_date, total_cost = row

            # Convert connection_date to datetime if it's not already
            if isinstance(connection_date, str):
                connection_date = datetime.datetime.strptime(connection_date, '%Y-%m-%d %H:%M:%S')

            # Create a VirtualMachine object using the retrieved data
            vm = VirtualMachine(
                name=name,
                password=password,
                public_ip=public_ip,
                provider=provider,
                username=username,  # Adding username
                connection_date=connection_date,
                total_cost=total_cost
            )

            # Append the VirtualMachine object to the list
            vm_list.append(vm)

        # Return the list of VirtualMachine objects
        return vm_list

    def getPassword(self, vm_name):
        """Retrieve the password for a given VM name."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT password FROM vm_passwords
            WHERE vm_name = ?
        """, (vm_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

# Global SQLiteServer instance
global_db_server = None

def create_db_server(db_name=os.path.expanduser("~") + "/.local/share/cloudsurge/data.db"):
    """Create and initialize the global SQLiteServer instance."""
    global global_db_server
    if global_db_server is None:
        global_db_server = SQLiteServer(db_name)
        global_db_server.connect()
        directory_name = os.path.dirname(db_name)
        if directory_name:
            os.makedirs(directory_name, exist_ok=True)

def get_db_server():
    """Return the global SQLiteServer instance."""
    return global_db_server
