import os
from datetime import date

import requests

from backend.azure_provider import Azure
from backend.db import Database
from backend.digitalocean_provider import DigitalOcean
from backend.no_provider import NoProvider
from backend.vm import Provider
from backend.vm import VirtualMachine


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


if __name__ == "__main__":
    print("Starting Test")
    db = Database()
    db.init()

    providers = db.read_provider()
    print("SUS: " + str(providers))
    if len(providers) != 0:

        print("Detected Providers:")
        vm = db.read_vm(providers)[0]
        print(str(vm))
        vm.get_provider().delete_vm(vm)
    else:
        pass
        provider_connection = DigitalOcean("t31@gmail.com", date.today(), "Sussybaka123")


        print(provider_connection.connection_is_alive())

        ssh_key_ids = ["irgendwasmit: dazwischen"]  # Assuming you have SSH keys registered

        # Parameters for creating the VM
        location = 'nyc3'
        vm_name = 'test-vm'
        vm_size = 's-1vcpu-1gb'
        admin_username = 'admin'
        admin_password = 'password'
        image_reference = 'ubuntu-20-04-x64'  # You can replace this with an actual image name/slug
        zerotier_network = '12345'  # Optional field, if required
        ssh_key_path = '/path/to/your/ssh/key'

        # Create the VM
        vm = provider_connection.create_vm(
            location, vm_name, vm_size, admin_username, admin_password,
            image_reference, ssh_key_ids, zerotier_network, ssh_key_path
        )

        db.insert_provider(provider_connection)
        db.insert_vm(vm)
        pass