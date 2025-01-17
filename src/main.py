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

from .reached_cost_limits import get_reached_cost_limits
from .server_is_active import get_active_servers
from .db import Database
import webbrowser

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Gio, Adw, GLib
from .window import CloudsurgeWindow
from .new import NewView


class CloudsurgeApplication(Adw.Application):
    """The main application singleton class."""

    main_window: CloudsurgeWindow
    main_listbox: Gtk.ListBox
    # providers: list[Adw.ActionRow] = []
    vms = []
    providers = []

    # db: Database

    def __init__(self):
        super().__init__(
            application_id="org.techtowers.CloudSurge",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )

        get_cloudsurge_script()

        self.db = Database()
        self.db.init()

        self.providers = self.db.read_provider()
        self.vms = self.db.read_vm(self.providers)

        # prov = self.db.read_provider()
        # vm = self.db.read_vm(prov)
        # print(prov)
        # print(vm)

        self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action("new", self.show_add_view)
        self.create_action("test", self.test)
        self.create_action("howto", self.howto)
        self.create_action("aboutus", self.aboutus)

        self.__register_arguments()

    def __register_arguments(self):
        self.add_main_option(
            "costs",
            ord("c"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            ("Displays all VMs that overrun the cost limit"),
            None,
        )
        self.add_main_option(
            "online",
            ord("o"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            ("Shows the count of the currently online VMs"),
            None,
        )

    def do_command_line(self, command):
        commands = command.get_options_dict()
        if commands.contains("costs"):
            get_reached_cost_limits()
            quit()
        if commands.contains("online"):
            get_active_servers()
            quit()

        self.do_activate()
        return 0

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CloudsurgeWindow(
                self.db, self.vms, self.providers, application=self
            )
            self.main_listbox = (
                win.get_content().get_content().get_first_child()
            )
        win.present()
        self.main_window = win
        self.main_window.app = self

        zerotier_id = self.db.retrieve_zerotier_id()
        if zerotier_id:
            self.main_window.zerotier_id.set_title("current: " + zerotier_id)

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name="cloudsurge",
            application_icon="org.techtowers.CloudSurge",
            developer_name="Benedikt",
            version="0.2.0",
            developers=["Benedikt"],
            copyright="© 2024 Benedikt",
        )
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(("translator-credits"))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print("app.preferences action activated")

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
        print(self.providers)

    def add_provider(self, name: str, _):
        row = Adw.ActionRow()
        row.set_title("Azure")
        self.providers.append(row)
        self.main_listbox.append(row)
        print(self.main_listbox)

    def show_add_view(self, _, widget=False):
        new_window = NewView(
            self.main_window, self.vms, self.providers, self.db
        )
        new_window.app = self
        new_window.present()

    def howto(self, *_):
        webbrowser.open_new_tab(
            "https://github.com/TechTowers/CloudSurge?tab=readme-ov-file#%EF%B8%8F-cloudsurge"
        )

    def aboutus(self, *_):
        webbrowser.open_new_tab("https://github.com/TechTowers")


def get_cloudsurge_script():
    """Retrieves the CloudSurge script from the GitHub repository and saves it to the local filesystem."""
    file_path = os.path.expandvars("$XDG_DATA_HOME/cloudsurge.sh")
    url = "https://raw.githubusercontent.com/TechTowers/CloudSurge/refs/heads/main/scripts/cloudsurge.sh"

    r = requests.get(url, stream=True)
    if r.ok:
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
