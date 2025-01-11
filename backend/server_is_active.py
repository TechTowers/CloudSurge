# author: Luka Pacar
from subprocess import TimeoutExpired
from backend import VirtualMachine
from backend import Database

def get_active_servers():
    """Returns a list of virtual machines that have reached their cost limits."""
    db = Database()
    db.init()

    providers = db.read_provider()
    vms = db.read_vm(providers)

    amount_reachable = 0
    for vm in vms:
        if is_reachable(vm):
            amount_reachable += 1

    print(amount_reachable)

def is_reachable(vm: VirtualMachine):
    """Check if the virtual machine is reachable."""
    try:
        if vm.is_reachable():
            return True
    except TimeoutExpired:
        if vm.get_provider().get_provider_name() == "No-Provider":
            return False
        elif vm.get_provider().is_active(vm):
            return True


if __name__ == "__main__":
    get_active_servers()