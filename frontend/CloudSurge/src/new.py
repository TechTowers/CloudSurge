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

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.app = window.app
        self.window = window
        #self.manager = window.manager
        self.is_closable = True

        self.check_provider.connect("activate", self.show_provider_settings)
        self.check_machine.connect("activate", self.show_machine_settings)
        self.provider_dropdown.connect("notify::selected-item", self.test)

    def show_provider_settings(self, _):
        self.machine_settings.hide()
        self.provider_settings.show()

    def show_machine_settings(self, _):
        self.provider_settings.hide()
        self.machine_settings.show()

