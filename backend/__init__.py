from datetime import date

from backend.azure import Azure
from backend.vm import VirtualMachine
from backend.vm import Provider

vm = VirtualMachine("test-vm", Azure("Luka Pacar",date.today(),"","","",""), True, True, 100, "192.168.0.1", date.today(), 50, 120)
vm.print_info()