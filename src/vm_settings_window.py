# vm_settings_dialog.py
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
from .wait_popup_window import WaitPopupWindow
import threading


# import backend.db


@Gtk.Template(
    resource_path="/org/techtowers/CloudSurge/blueprints/vm_settings_window.ui"
)
class VmSettingsWindow(Adw.Window):
    __gtype_name__ = "VmSettingsWindow"

    start_machine = Gtk.Template.Child()
    stop_machine = Gtk.Template.Child()
    delete_machine = Gtk.Template.Child()
    update_machine = Gtk.Template.Child()
    curr_cost = Gtk.Template.Child()
    cost_limit = Gtk.Template.Child()
    provider_acc = Gtk.Template.Child()

    def __init__(self, vm, vm_gui_widget, db, window, all_vms, **kwargs):
        self.vm = vm
        self.all_vms = all_vms
        self.vm_gui_widget = vm_gui_widget
        self.db = db
        self.window = window
        super().__init__(**kwargs)

        self.start_machine.connect("activated", self.start_vm)
        self.stop_machine.connect("activated", self.stop_vm)
        self.delete_machine.connect("activated", self.delete_vm)
        self.update_machine.connect("activated", self.update_vm)

        thread_values = threading.Thread(
            target=self.update_vm_value, args=(vm,)
        )
        thread_values.start()

        thread_running = threading.Thread(target=self.update_state, args=(vm,))
        thread_running.start()

    def update_state(self, vm):
        if vm.is_reachable():
            self.set_title("Running")
        else:
            self.set_title("Unreachable")

    def update_vm_value(self, vm):
        self.provider_acc.set_title(vm.get_provider().get_account_name())
        self.provider_acc.set_subtitle("Linked Provider Account")
        self.cost_limit.set_title(f"{vm.get_cost_limit()}$")
        self.cost_limit.set_subtitle("Cost Limit")
        self.curr_cost.set_title(f"{vm.get_provider().get_vm_cost(vm):.2f}$")
        self.curr_cost.set_subtitle("Current Cost")

    def start_vm(self, _):
        self.vm.get_provider().start_vm(self.vm)
        self.close()

    def stop_vm(self, _):
        self.vm.get_provider().stop_vm(self.vm)
        self.close()

    def delete_vm(self, _):
        self.vm.get_provider().delete_vm(self.vm, self.db)
        self.all_vms.remove(self.vm)
        self.window.machines_list.remove(self.vm_gui_widget)
        self.close()

    def update_vm(self, _):
        def action():
            if self.vm.is_reachable():
                print("Updating VM")
                self.vm.configure_vm()
                self.close()
            else:
                print("VM not reachable")

        dialog = WaitPopupWindow(action)
        dialog.app = self.app
        dialog.present()
