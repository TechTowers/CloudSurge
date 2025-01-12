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
import threading

from gi.repository import Adw
from gi.repository import Gtk, GLib
@Gtk.Template(resource_path='/org/techtowers/CloudSurge/blueprints/wait_popup.ui')
class WaitPopupWindow(Adw.Window):
    __gtype_name__ = 'WaitPopupWindow'

    def __init__(self, action, **kwargs):
        super().__init__(**kwargs)
        self.execute_in_thread(action)

    def execute_in_thread(self, action):
        def wrapper():
            # Execute the passed code block
            action()
            # Close Window after Block is finished. Resuming GUI
            GLib.idle_add(self.close)

        # Create a new thread to execute the wrapped code block
        thread = threading.Thread(target=wrapper)
        thread.start()
        return thread


