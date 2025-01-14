# error_window.py
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


@Gtk.Template(resource_path="/org/techtowers/CloudSurge/blueprints/error.ui")
class ErrorWindow(Adw.Window):
    __gtype_name__ = "ErrorWindow"

    err_message = Gtk.Template.Child()

    def __init__(self, text, parent, **kwargs):
        super().__init__(**kwargs)
        self.show_error(text)
        if parent:
            self.set_transient_for(parent)
            self.set_modal(True)

    def show_error(self, text):
        self.err_message.set_label(text)
