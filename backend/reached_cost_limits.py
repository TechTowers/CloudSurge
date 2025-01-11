# author: Luka Pacar
from backend import VirtualMachine
from backend import Database

def get_reached_cost_limits():
    """Prints a list of virtual machines that have reached their cost limits."""
    db = Database()
    db.init()

    providers = db.read_provider()
    vms = db.read_vm(providers)

    for vm in vms:
        try:
            val = reached_cost_limit(vm)
            if val > 0:
                print_cost_limits(vm, val)
        except:
            pass

def reached_cost_limit(vm: VirtualMachine):
    """Check if the virtual machine has reached its cost limit."""
    return vm.get_provider().get_vm_cost(vm) - vm.get_cost_limit()

def print_cost_limits(vm: VirtualMachine, val: int):
    """Print the cost limits."""
    print(f"{vm.get_provider().get_provider_name()};{vm.get_vm_name()};{vm.get_cost_limit()};{val}")

if __name__ == "__main__":
    get_reached_cost_limits()