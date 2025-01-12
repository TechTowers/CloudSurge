# provider_settings_dialog.py
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
#import backend.db

@Gtk.Template(resource_path='/org/gnome/Example/blueprints/provider_settings_window.ui')
class ProviderSettingsWindow(Adw.Window):
    __gtype_name__ = 'ProviderSettingsWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
