from backend.aws_provider import AWS
from backend.db import Database
from backend.digitalocean_provider import DigitalOcean
from backend.no_provider import NoProvider
from backend.vm import Provider
from backend.vm import VirtualMachine

if __name__ == "__main__":
    db = Database()
    db.init()

    prov = db.read_provider()
    vm = db.read_vm(prov)
