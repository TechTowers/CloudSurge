import os
from datetime import date

import requests

from backend.azure_provider import Azure
from backend.db import Database
from backend.no_provider import NoProvider
from backend.vm import Provider
from backend.vm import VirtualMachine


def get_cloudsurge_script():
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
    provider = Azure("Sussybaka12321",date.today(),"39b171f0-e5a8-4caa-b47a-30b8436b2fcc","sus","baa","kaa")
    provider.create_vm()
    #print(provider.check_subscription())

    ###
    #vm = VirtualMachine("test-vm-2", provider, True, True, 100, "192.168.0.101", date.today(), "root", "sus123!", "123456","")
    #vm2 = VirtualMachine("test vm no provider", None, True, True, 100, "", date.today(), "username", "dogdogdogdog123!", "12132","")


    db = Database()
    db.init()

    #db.insert_provider(provider)
    #db.insert_vm(vm)
    #db.insert_vm(vm2)
    #providers = db.read_provider()
    #for d in providers:
    #    print (str(d))
    #for d in db.read_vm(providers):
    #    print (str(d))

    vm_cs = VirtualMachine("CloudSurge VM", None, True, True, 100, "50.85.216.201", date.today(), "azureuser", "", "e3918db483871f02", "~/.ssh/test_key.pem")
    vm_cs.install_vm()

    print(vm2.is_reachable())
    db.close()
