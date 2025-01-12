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

@Gtk.Template(resource_path='/org/gnome/Example/blueprints/new.ui')
class NewView(Adw.Window):
    def test(self, jojo, _):
        print(self.provider_dropdown.get_selected_item().get_string())

    __gtype_name__ = 'NewView'

    check_provider = Gtk.Template.Child()
    check_machine = Gtk.Template.Child()
    provider_settings = Gtk.Template.Child()
    machine_settings = Gtk.Template.Child()
    provider_dropdown = Gtk.Template.Child()
    vm_provider_dropdown = Gtk.Template.Child()
    btn_create = Gtk.Template.Child()

    account_name = Gtk.Template.Child()
    provider_name = Gtk.Template.Child()

    account_name_string: str
    provider_name_string: str

    # Aws
    access_key = Gtk.Template.Child()
    secret_key = Gtk.Template.Child()
    region = Gtk.Template.Child()

    access_key_string: str
    secret_key_string: str
    region_string: str
    #aws_fields = [access_key, secret_key, region, vpc_id , subnet_id, security_group_id]

    # DigitalOcean
    token = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.app = window.app
        self.window = window
        #self.manager = window.manager
        self.is_closable = True

        self.aws_fields = [self.provider_name, self.account_name, self.access_key, self.secret_key, self.region]
        self.check_provider.connect("activate", self.show_provider_settings)
        self.check_machine.connect("activate", self.show_machine_settings)
        self.provider_dropdown.connect("notify::selected-item", self.change_provider)
        self.btn_create.connect("clicked", self.submit)


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

        elif self.provider_dropdown.get_selected_item().get_string() == "DigitalOcean":
            self.access_key.hide()
            self.secret_key.hide()
            self.region.hide()

            self.token.show()

    def change_vm_provider(self, signal, _):
        if self.provider_dropdown.get_selected_item().get_string() == "Aws":
            self.token.hide()

            self.access_key.show()
            self.secret_key.show()
            self.region.show()

        elif self.provider_dropdown.get_selected_item().get_string() == "DigitalOcean":
            self.access_key.hide()
            self.secret_key.hide()
            self.region.hide()

            self.token.show()

    def submit(self, _):
        if self.provider_dropdown.get_selected_item().get_string() == "Aws":
            for field in self.aws_fields:
                if field.get_text() == "":
                    print("empty")
                    return
        elif self.provider_dropdown.get_selected_item().get_string() == "DigitalOcean":
            pass
