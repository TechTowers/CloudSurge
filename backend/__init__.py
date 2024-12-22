from datetime import date

from backend.azure import Azure
from backend.db import Database
from backend.vm import VirtualMachine
from backend.vm import Provider

if __name__ == "__main__":
    provider = Azure("Luka Pacar- Second Account",date.today(),"jojoID","sus","baa","kaa")
    vm = VirtualMachine("test-vm-2", provider, True, True, 100, "192.168.0.101", date.today())

    db = Database()
    db.init()

    db.insert_provider(provider)
    db.insert_vm(vm)
    providers = db.read_provider()
    print(str(providers[0]))
    for d in db.read_vm(providers):
        print (str(d))
    db.close()