import os
from datetime import date

import requests

from backend.aws_provider import AWS
from backend.DEPRECATED_azure_provider import Azure
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
    db = Database()
    db.init()

    provider_connection = DigitalOcean("sussy", date.today(),  "nothing")
    vm = provider_connection.create_vm(
        vm_name="sussy1233333",
        ssh_key_ids=["47:4c:06:a3:ec:7e:9f:a1:34:58:01:18:97:60:0a:ba"],
        zerotier_network="12345",
        ssh_key_path="C:\\Users\\you\\.ssh\\id_ed25519"
    )
