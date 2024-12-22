from datetime import date

from backend.azure import Azure
from backend.db import Database
from backend.vm import VirtualMachine
from backend.vm import Provider

if __name__ == "__main__":
    #provider = Azure("Luka Pacar",date.today(),"","","","")
    #vm = VirtualMachine("test-vm", provider, True, True, 100, "192.168.0.1", date.today(), 50, 120)

    db = Database()
    db.init()

    #db.insert_provider(provider)
    #db.insert_vm(vm)
    providers = db.read_provider()
    print(str(providers[0]))
    for d in db.read_vm(providers):
        print (str(d))
    db.close()