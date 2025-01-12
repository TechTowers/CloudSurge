# window.py
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

import os
from gi.repository import Adw
from gi.repository import Gtk

from .db import Database

# import backend.db
from .vm_settings_window import VmSettingsWindow
from .provider_settings_window import ProviderSettingsWindow


@Gtk.Template(resource_path="/org/techtowers/CloudSurge/blueprints/window.ui")
class CloudsurgeWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CloudsurgeWindow"

    db: Database

    curr_selected_provider = None
    curr_selected_vm = None

    home_button = Gtk.Template.Child()
    providers_button = Gtk.Template.Child()
    machines_button = Gtk.Template.Child()
    cost_button = Gtk.Template.Child()

    save_zerotier_id_button = Gtk.Template.Child()
    zerotier_id = Gtk.Template.Child()

    home_box = Gtk.Template.Child()
    providers_list = Gtk.Template.Child()
    providers_window = Gtk.Template.Child()
    machines_list = Gtk.Template.Child()
    machines_window = Gtk.Template.Child()
    cost_window = Gtk.Template.Child()

    vm_settings_button = Gtk.Template.Child()
    provider_settings_button = Gtk.Template.Child()

    def __init__(self, db, vms, providers, **kwargs):
        super().__init__(**kwargs)
        # self.providers_button.set_active(True)

        self.vms = vms
        self.providers = providers
        for provider in self.providers:
            self.add_provider_to_gui(provider)
        self.db = db
        self.home_button.connect("clicked", self.show_home)
        self.providers_button.connect("clicked", self.show_providers)
        self.machines_button.connect("clicked", self.show_machines)
        self.cost_button.connect("clicked", self.show_cost)
        self.save_zerotier_id_button.connect("activated", self.save_zerotier_id)
        self.vm_settings_button.connect("clicked", self.show_vm_settings_window)
        self.provider_settings_button.connect(
            "clicked", self.show_provider_settings_window
        )

    def show_home(self, _):
        self.providers_window.hide()
        self.machines_window.hide()
        self.cost_window.hide()
        self.home_box.show()

        self.providers_button.set_active(False)
        self.machines_button.set_active(False)
        self.cost_button.set_active(False)
        self.home_button.set_active(True)

    def show_providers(self, _):
        self.machines_window.hide()
        self.home_box.hide()
        self.cost_window.hide()
        self.providers_window.show()

        self.machines_button.set_active(False)
        self.home_button.set_active(False)
        self.cost_button.set_active(False)
        self.providers_button.set_active(True)

    def show_machines(self, _):
        self.providers_window.hide()
        self.home_box.hide()
        self.cost_window.hide()
        self.machines_window.show()

        self.providers_button.set_active(False)
        self.home_button.set_active(False)
        self.cost_button.set_active(False)
        self.machines_button.set_active(True)

    def show_cost(self, _):
        self.providers_window.hide()
        self.home_box.hide()
        self.machines_window.hide()
        self.cost_window.show()

        self.providers_button.set_active(False)
        self.home_button.set_active(False)
        self.machines_button.set_active(False)
        self.cost_button.set_active(True)

    def save_zerotier_id(self, _):
        path = os.path.expanduser("~") + "/.cloudsurge_zerotierid"
        t = self.zerotier_id.get_text()
        with open(path, "w+") as f:
            f.write(t)
        self.zerotier_id.set_title("current: " + t)

    def show_vm_settings_window(self, _, vm, vm_gui_widget):
        dialog = VmSettingsWindow(vm, vm_gui_widget, self.db, self)
        dialog.app = self.app
        dialog.present()

    def show_provider_settings_window(self, _, provider, provider_gui_widget):
        dialog = ProviderSettingsWindow(
            provider, provider_gui_widget, self.db, self
        )
        dialog.app = self.app
        dialog.present()

    # Provider-Methods
    def add_provider_to_gui(self, provider):
        self.providers_list.append(self.provider_to_widget(provider))

    def provider_to_widget(self, provider) -> Adw.ActionRow:
        row = Adw.ActionRow()
        row.set_title(provider.get_account_name())
        row.set_subtitle(provider.get_provider_name())

        # Create the button and add the desired child elements
        button = Gtk.Button()
        # button.set_action_name("app.test")
        button.connect(
            "clicked", self.show_provider_settings_window, provider, row
        )
        # Define the Box to hold the child widget, with appropriate spacing
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Create the Image widget with the icon
        image = Gtk.Image(icon_name="applications-system-symbolic")

        # Add the image to the box
        box.append(image)

        # Set the Box as the child of the button
        button.set_child(box)

        # Add the button to the ActionRow
        row.add_suffix(button)
        return row

    # VM-Methods
    def add_vm_to_gui(self, vm):
        self.machines_list.append(self.vm_to_widget(vm))

    def vm_to_widget(self, vm) -> Adw.ActionRow:
        row = Adw.ActionRow()
        row.set_title(vm.get_vm_name())
        row.set_subtitle(vm.get_provider().get_account_name())

        # Create the button and add the desired child elements
        button = Gtk.Button()
        button.set_action_name("app.test")
        button.connect("clicked", self.show_vm_settings_window, vm, row)

        # Define the Box to hold the child widget, with appropriate spacing
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Create the Image widget with the icon
        image = Gtk.Image(icon_name="applications-system-symbolic")

        # Add the image to the box
        box.append(image)

        # Set the Box as the child of the button
        button.set_child(box)

        # Add the button to the ActionRow
        row.add_suffix(button)
        return row
