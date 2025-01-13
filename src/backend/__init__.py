from datetime import date
from .aws_provider import AWS
from .db import Database
from .digitalocean_provider import DigitalOcean
from .vm import VirtualMachine


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
