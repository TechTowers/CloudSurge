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

@Gtk.Template(resource_path='/org/gnome/Example/blueprints/window.ui')
class CloudsurgeWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CloudsurgeWindow'

    home_button = Gtk.Template.Child()
    providers_button = Gtk.Template.Child()
    machines_button = Gtk.Template.Child()

    save_zerotier_id_button = Gtk.Template.Child()
    zerotier_id = Gtk.Template.Child()

    home_box = Gtk.Template.Child()
    providers_list = Gtk.Template.Child()
    machines_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.providers_button.set_active(True)
        
        self.providers_button.connect("clicked", self.show_providers)
        self.machines_button.connect("clicked", self.show_machines)
        self.home_button.connect("clicked", self.show_home)
        self.save_zerotier_id_button.connect("clicked", self.save_zerotier_id)

    def show_providers(self, _):
        self.machines_list.hide()
        self.home_box.hide()
        self.providers_list.show()

        self.machines_button.set_active(False)
        self.home_button.set_active(False)
        self.providers_button.set_active(True)

    def show_machines(self, _):
        self.providers_list.hide()
        self.home_box.hide()
        self.machines_list.show()

        self.providers_button.set_active(False)
        self.home_button.set_active(False)
        self.machines_button.set_active(True)

    def show_home(self, _):
        self.providers_list.hide()
        self.machines_list.hide()
        self.home_box.show()

        self.providers_button.set_active(False)
        self.machines_button.set_active(False)
        self.home_button.set_active(True)

    def save_zerotier_id(self, _):
        path = os.path.expanduser("~") + "/.cloudsurge_zerotierid"
        t = self.zerotier_id.get_text()
        with open(path, "w+") as f:
            f.write(t)
        self.zerotier_id.set_title("current: " + t)
