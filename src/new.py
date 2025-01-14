# new.py
#
# Copyright 2024 Benedikt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
from gi.repository import Adw
from gi.repository import Gtk

from datetime import date
from time import sleep

from .error_window import ErrorWindow
from .vm import VirtualMachine
from .no_provider import NoProvider
from .db import Database
from .aws_provider import AWS
from .digitalocean_provider import DigitalOcean
from .wait_popup_window import WaitPopupWindow


@Gtk.Template(resource_path="/org/techtowers/CloudSurge/blueprints/new.ui")
class NewView(Adw.Window):
    def test(self, jojo, _):
        print(self.provider_dropdown.get_selected_item().get_string())

    __gtype_name__ = "NewView"

    check_provider = Gtk.Template.Child()
    check_machine = Gtk.Template.Child()
    provider_settings = Gtk.Template.Child()
    machine_settings = Gtk.Template.Child()
    provider_dropdown = Gtk.Template.Child()

    vm_provider_choice = Gtk.Template.Child()
    btn_create = Gtk.Template.Child()

    account_name = Gtk.Template.Child()
    provider_name = Gtk.Template.Child()

    # Machine fields
    vm_name = Gtk.Template.Child()
    vm_provider_dropdown = Gtk.Template.Child()
    cost_limit = Gtk.Template.Child()
    public_ip = Gtk.Template.Child()
    username = Gtk.Template.Child()
    password = Gtk.Template.Child()
    do_key_id = Gtk.Template.Child()
    aws_key_name = Gtk.Template.Child()
    ssh_key = Gtk.Template.Child()

    account_name_string: str
    provider_name_string: str

    # Aws
    access_key = Gtk.Template.Child()
    secret_key = Gtk.Template.Child()
    region = Gtk.Template.Child()

    access_key_string: str
    secret_key_string: str
    region_string: str
    # aws_fields = [access_key, secret_key, region, vpc_id , subnet_id, security_group_id]

    # DigitalOcean
    token = Gtk.Template.Child()

    def __init__(self, window, vms, providers, db, **kwargs):
        super().__init__(**kwargs)

        self.vms = vms
        self.providers = providers
        self.db = db
        self.app = window.app
        self.window = window
        # self.manager = window.manager
        self.is_closable = True

        for prov in providers:
            self.vm_provider_choice.append(prov.get_account_name())

        self.aws_fields = [
            self.provider_name,
            self.account_name,
            self.access_key,
            self.secret_key,
            self.region,
        ]
        self.check_provider.connect("activate", self.show_provider_settings)
        self.check_machine.connect("activate", self.show_machine_settings)
        self.provider_dropdown.connect(
            "notify::selected-item", self.change_provider
        )
        self.vm_provider_dropdown.connect(
            "notify::selected-item", self.change_vm_provider
        )
        self.btn_create.connect("clicked", self.submit)
        self.set_transient_for(window)
        self.set_modal(True)

    def show_provider_settings(self, _):
        self.machine_settings.hide()
        self.provider_settings.show()

    def show_machine_settings(self, _):
        self.provider_settings.hide()
        self.machine_settings.show()

    def change_provider(self, signal, _):
        if self.provider_dropdown.get_selected_item().get_string() == "Aws":
            self.token.hide()

            self.access_key.show()
            self.secret_key.show()
            self.region.show()

        elif (
            self.provider_dropdown.get_selected_item().get_string()
            == "DigitalOcean"
        ):
            self.access_key.hide()
            self.secret_key.hide()
            self.region.hide()

            self.token.show()

    def change_vm_provider(self, obj, _):
        account_name = (
            self.vm_provider_dropdown.get_selected_item().get_string()
        )
        if account_name == "SSH (No provider)":
            self.do_key_id.hide()
            self.aws_key_name.hide()
            self.public_ip.show()
            self.username.show()
            self.password.show()
            return
        for provider in self.providers:
            if provider.get_account_name() == account_name:
                if provider.get_provider_name() == "AWS":
                    self.do_key_id.hide()
                    self.aws_key_name.show()
                    self.public_ip.hide()
                    self.username.hide()
                    self.password.hide()
                else:
                    self.do_key_id.show()
                    self.aws_key_name.hide()
                    self.public_ip.hide()
                    self.username.hide()
                    self.password.hide()

    def submit(self, _):
        def submit_block(pop_up_window):
            if self.check_provider.get_active():
                if not self.process_provider_input(pop_up_window):
                    pass
            elif self.check_machine.get_active():
                if not self.process_machine_input(pop_up_window):
                    pass

        self.show_popup_window(submit_block)

    def process_provider_input(self, pop_up_window) -> bool:
        db = Database()
        db.init()
        provider: str = self.provider_dropdown.get_selected_item().get_string()
        acc_name = self.account_name.get_text()
        all_providers = db.read_provider()
        for prov_conn in all_providers:
            if prov_conn.get_account_name() == acc_name:
                self.show_error_window(
                    ValueError(
                        "Provider with that Account-Name already exists."
                    ),
                    pop_up_window,
                )
                return False
        creation_time = date.today()
        if provider == "Aws":
            access_key = self.access_key.get_text()
            secret_key = self.secret_key.get_text()
            region = self.region.get_text()
            provider_connection = AWS(
                acc_name, creation_time, access_key, secret_key, region
            )
            if provider_connection.connection_is_alive():
                db.insert_provider(provider_connection, print_output=False)
                self.providers.append(provider_connection)
                print("inserted Successfully")
                self.window.add_provider_to_gui(provider_connection)

                self.close()
                return True
            else:
                self.show_error_window(
                    ValueError("Could not Connect - Invalid Credentials?"),
                    pop_up_window,
                )
                return False
        elif provider == "DigitalOcean":
            token = self.token.get_text()
            provider_connection = DigitalOcean(acc_name, creation_time, token)
            if provider_connection.connection_is_alive():
                db.insert_provider(provider_connection, print_output=False)
                self.providers.append(provider_connection)
                print("inserted Successfully")
                self.window.add_provider_to_gui(provider_connection)
                self.close()
                return True
            else:
                self.show_error_window(
                    ValueError("Could not Connect - Invalid Credentials?"),
                    pop_up_window,
                )
                return False
        return False

    def show_popup_window(
        self,
        action,
    ):
        dialog = WaitPopupWindow(action, self)
        dialog.app = self.app
        dialog.present()

    def add_vm(self, vm, db):
        if vm is None:
            print("Error Creating VM")
            return
        for i in range(10):
            if i == 10:
                raise ValueError("Could not reach VM")
            elif vm.is_reachable():
                print("Starting Install..")
                vm.install_vm()
                print("Starting Configuring..")
                vm.configure_vm()
                print("Finished Configuring")
                break
            else:
                sleep(2)

        self.window.add_vm_to_gui(vm)
        self.vms.append(vm)
        db.insert_vm(vm)
        self.close()

    def show_error_window(self, exception, pop_up_window):
        pop_up_window.close()
        dialog = ErrorWindow(str(exception), self)

        # self.children().push(dialog)
        dialog.app = self.app
        dialog.present()
        dialog.set_focus()
        print("showing error")

    def process_machine_input(self, pop_up_window):
        db = Database()
        db.init()
        selected_provider = (
            self.vm_provider_dropdown.get_selected_item().get_string()
        )
        vm_name = self.vm_name.get_text()
        all_providers = db.read_provider()
        all_vms = db.read_vm(all_providers)
        for vm in all_vms:
            if vm.get_vm_name() == vm_name:
                self.show_error_window(
                    ValueError("VM with that Name already exists."),
                    pop_up_window,
                )
                return False
        cost_limit = self.cost_limit.get_text()
        ssh_key = self.ssh_key.get_text()
        if selected_provider.lower().startswith("ssh"):
            print("Connection VM using SSH")
            provider = NoProvider("No-Provider", date.today())
            public_ip = self.public_ip.get_text()
            first_connection_date = date.today()
            root_username = self.username.get_text()
            password = self.password.get_text()

            zerotier_network = db.retrieve_zerotier_id()
            if not zerotier_network:
                self.show_error_window(
                    ValueError("ZeroTier-ID not set"), pop_up_window
                )
                return False
            try:
                vm = VirtualMachine(
                    vm_name=vm_name,
                    provider=provider,
                    cost_limit=cost_limit,
                    public_ip=public_ip,
                    first_connection_date=first_connection_date,
                    root_username=root_username,
                    password=password,
                    zerotier_network=zerotier_network,
                    ssh_key=ssh_key,
                )
                self.add_vm(vm, db)
            except Exception as e:
                self.show_error_window(e, pop_up_window)
        else:
            found_provider = None
            for prov_connection in self.providers:
                if prov_connection.get_account_name() == selected_provider:
                    found_provider = prov_connection
                    break

            if not found_provider:  # Provider not found in db
                return False

            if found_provider.get_provider_name() == "AWS":
                print("Creating VM using AWS")
                aws_ssh_key_name = self.aws_key_name.get_text()
                zerotier_network = db.retrieve_zerotier_id()
                if not zerotier_network:
                    self.show_error_window(
                        ValueError("ZeroTier-ID not set"), pop_up_window
                    )
                    return False
                if len(ssh_key) != 0:
                    try:
                        vm = found_provider.create_vm(
                            vm_name=vm_name,
                            aws_ssh_key_name=aws_ssh_key_name,
                            zerotier_network=zerotier_network,
                            cost_limit=cost_limit,
                            ssh_key_path=ssh_key,
                        )
                        self.add_vm(vm, db)
                    except Exception as e:
                        self.show_error_window(e, pop_up_window)
                else:
                    try:
                        vm = found_provider.create_vm(
                            vm_name=vm_name,
                            aws_ssh_key_name=aws_ssh_key_name,
                            zerotier_network=zerotier_network,
                            cost_limit=cost_limit,
                        )
                        self.add_vm(vm, db)
                    except Exception as e:
                        self.show_error_window(e, pop_up_window)

            elif found_provider.get_provider_name() == "DigitalOcean":
                print("Creating VM using DigitalOcean")
                ssh_key_ids = [self.do_key_id.get_text()]
                zerotier_network = db.retrieve_zerotier_id()
                if not zerotier_network:
                    self.show_error_window(
                        ValueError("ZeroTier-ID not set"), pop_up_window
                    )
                    return False

                try:
                    vm = found_provider.create_vm(
                        vm_name=vm_name,
                        ssh_key_ids=ssh_key_ids,
                        zerotier_network=zerotier_network,
                        cost_limit=cost_limit,
                        ssh_key_path=ssh_key,
                    )
                    self.add_vm(vm, db)
                except Exception as e:
                    self.show_error_window(e, pop_up_window)
