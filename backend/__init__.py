import os
import time
from datetime import date

import requests

from backend.aws_provider import AWS
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

    v = db.read_vm(providers)

    if len(providers) != 0:
        print(str(providers))
        print("DISCTINCT")
        print(str(providers[0]))
        vm = providers[0].create_vm(
            location="us-east-1",
            vm_name="test-instance",
            vm_size="t3.micro",
            admin_password="YourSecurePassword!",
            image_reference="ami-079cb33ef719a7b78",
            ssh_key_name="CloudSurge"
        )
        db.insert_vm(vm)
        db.reload_provider(providers[0])
    else:

        provider_connection = AWS("@gmail.com", date.today(), "AKIJB2IT", "oINYvZ", "us-east-1")
        #db.insert_provider(provider_connection)


        print(provider_connection.connection_is_alive())

        from datetime import datetime

        # Test parameters for VM creation
        location = "us-east-1"  # AWS region (us-east-1, Virginia region)
        vm_name = "test-instance"  # VM Name
        vm_size = "t3.micro"  # Instance type (free-tier eligible)
        admin_password = "YourSecurePassword!"  # Admin password for tagging
        image_reference = "ami-079cb33ef719a7b78"  # Ubuntu 20.04 LTS AMI ID
        ssh_key_name = "CloudSurge"  # Ensure this key pair already exists

        # Call the create_vm method to create the VM
        vm_instance = provider_connection.create_vm(
            location=location,
            vm_name=vm_name,
            vm_size=vm_size,
            admin_password=admin_password,
            image_reference=image_reference,
            ssh_key_name=ssh_key_name
        )

        # Check and print the VM details after creation
        if vm_instance:
            print(f"VM '{vm_instance.get_vm_name()}' created successfully!")
            print(f"Public IP: {vm_instance.get_public_ip()}")
            db.insert_vm(vm_instance)
            print("Finished")
        else:
            print("VM creation failed.")
        db.reload_provider(provider_connection)
