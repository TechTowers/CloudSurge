from datetime import date
import os
import requests

import subprocess
from .aws_provider import AWS
from .db import Database
from .digitalocean_provider import DigitalOcean
from .vm import VirtualMachine


def get_cloudsurge_script():
    """Retrieves the CloudSurge script from the GitHub repository and saves it to the local filesystem."""
    file_path = f"{os.path.expanduser("~")}/.local/bin/cloudsurge.sh"
    url = "https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/development/scripts/cloudsurge.sh"

    if not os.path.exists(".local/bin"):
        os.makedirs(".local/bin")

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )

    _ = subprocess.call(["chmod", "+x", file_path])


get_cloudsurge_script()

if __name__ == "__main__":
    db = Database()
    db.init()
    # db.delete_database()

    providers = db.read_provider()
    vms: list[VirtualMachine] = db.read_vm(providers)

    if len(providers) != 0:
        print("Found Instances")

    else:
        digitalocean_provider = DigitalOcean(
            "sussyDIGITAL",
            date.today(),
            "",
        )

        aws_provider = AWS(
            "sussyAWS",
            date.today(),
            "",
            "",
            "us-east-1",
        )

        vm = aws_provider.create_vm(
            location="us-east-1",
            vm_name="aws-num1",
            aws_ssh_key_name="sus",
            zerotier_network="",
        )
        db.insert_provider(aws_provider)
        db.insert_vm(vm)
