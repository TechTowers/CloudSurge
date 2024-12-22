from datetime import date

from backend.azure import Azure
from backend.db import Database
from backend.vm import VirtualMachine
from backend.vm import Provider

if __name__ == "__main__":
    provider = Azure("Luka Pacar",date.today(),"","","","")
    vm = VirtualMachine("test-vm", provider, True, True, 100, "192.168.0.1", date.today(), 50, 120)
    #vm.print_info()

    db = Database()
    db.init()

    db.insert_provider(provider)
    db.insert_vm(vm)
    print (db.read_provider())
    for d in db.read_vm():
        print ("yeah " + str(d))