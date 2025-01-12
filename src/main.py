# main.py
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
import sys
import gi
import requests
import subprocess

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import CloudsurgeWindow
from .new import NewView
from .db import Database

#from .db import Database

class CloudsurgeApplication(Adw.Application):
    """The main application singleton class."""
    main_window: CloudsurgeWindow
    main_listbox: Gtk.ListBox
    #providers: list[Adw.ActionRow] = []
    vms = []
    providers = []

    #db: Database

    def __init__(self):
        super().__init__(application_id='org.gnome.Example',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        get_cloudsurge_script()

        self.db = Database()
        self.db.init()

        self.providers = self.db.read_provider()
        self.vms = self.db.read_vm(self.providers)

        # prov = self.db.read_provider()
        # vm = self.db.read_vm(prov)
        # print(prov)
        # print(vm)


        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)
        self.create_action('new', self.show_add_view)
        self.create_action('test', self.test)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CloudsurgeWindow(self.db, self.vms, self.providers, application=self)
            self.main_listbox = win.get_content().get_content().get_first_child()
        win.present()
        self.main_window = win
        self.main_window.app = self


        zerotier_id = self.db.retrieve_zerotier_id()
        if zerotier_id:
            self.main_window.zerotier_id.set_title("current: " + zerotier_id)



    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='cloudsurge',
                                application_icon='org.gnome.Example',
                                developer_name='Benedikt',
                                version='0.1.0',
                                developers=['Benedikt'],
                                copyright='© 2024 Benedikt')
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def test(self, button, huh):
        print(button.get_name())
        print(huh)

    def show_providers(self):
        print(providers)

    def add_provider(self, name: str, _):
        row = Adw.ActionRow()
        row.set_title("Azure")
        self.providers.append(row)
        self.main_listbox.append(row)
        print(self.main_listbox)

    def show_add_view(self, _, widget=False):
        new_window = NewView(self.main_window, self.vms, self.providers, self.db)
        new_window.app = self
        new_window.present()


def get_cloudsurge_script():
    """Retrieves the CloudSurge script from the GitHub repository and saves it to the local filesystem."""
    file_path = f"{os.path.expanduser("~")}/.local/bin/cloudsurge.sh"
    url = "https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/main/scripts/cloudsurge.sh"
    
    if not os.path.exists(".local/bin"):
        os.makedirs(".local/bin")

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )

    _ = subprocess.call(["chmod", "+x", file_path])

def main(version):
    """The application's entry point."""
    app = CloudsurgeApplication()
    return app.run(sys.argv)
