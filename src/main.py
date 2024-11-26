# author: Benedikt und Luka 4CN
import sys
import os
import gi

import src.db
from cupsext import getPassword

from src.vm import VirtualMachine

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

# Window
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.db_server = self.initDB()
        self.vms = self.initVMs(self.db_server)
        self.bspWerte()

    def on_activate(self, app):
        if not app.get_active_window():
            global window
            window = Gtk.ApplicationWindow(application=app)
            window.set_default_size(900, 600)
            window.set_title("CloudSurge")

            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            window.set_child(main_box)

            header_bar = window.get_titlebar()
            if not header_bar:
                header_bar = Gtk.HeaderBar()
                window.set_titlebar(header_bar)

            create_button = Gtk.Button(label="+")
            create_button.connect("clicked", lambda btn: self.open_create_window(window))
            header_bar.pack_start(create_button)

            tabs_box = Gtk.Box(spacing=10)
            header_bar.set_title_widget(tabs_box)

            stack = Gtk.Stack()
            main_box.append(stack)

            providers_button = Gtk.Button(label="Providers")
            tabs_box.append(providers_button)
            providers_button.connect("clicked", self.activate_menu, stack, "providers", tabs_box)

            vms_button = Gtk.Button(label="Machines")
            tabs_box.append(vms_button)
            vms_button.connect("clicked", self.activate_menu, stack, "vms", tabs_box)

            aboutus_button = Gtk.Button(label="About Us")
            tabs_box.append(aboutus_button)
            aboutus_button.connect("clicked", self.activate_menu, stack, "About Us", tabs_box)

            stack.add_named(self.get_provider_page(), "providers")
            stack.add_named(self.get_vm_page(), "vms")
            stack.add_named(self.get_about_us_page(), "About Us")

            providers_button.emit("clicked")
            window.present()

    def get_vm_page(self):
        vms_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vms_page.append(Gtk.Label(label="List of VMs:"))
        vm_list = Gtk.ListBox()

        # Update button creation to pass open_create_window
        vm_list.append(self.create_button("VM1", self.create_popup_with_labels))
        vm_list.append(self.create_button("VM2", self.create_popup_with_labels))
        vm_list.append(self.create_button("VM3", self.create_popup_with_labels))

        vms_page.append(vm_list)
        return vms_page

    def get_provider_page(self):
        providers_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        providers_page.append(Gtk.Label(label="List of Providers:"))
        provider_list = Gtk.ListBox()

        # Update button creation to pass open_create_window
        provider_list.append(self.create_button("Azure", self.create_popup_with_labels))
        provider_list.append(self.create_button("Google", self.create_popup_with_labels))
        provider_list.append(self.create_button("Scaleway", self.create_popup_with_labels))

        providers_page.append(provider_list)
        return providers_page

    def get_about_us_page(self):
        aboutus_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        aboutus_page.append(self.create_button("About Us", self.create_popup_with_labels))
        return aboutus_page

    def activate_menu(self, button, stack, page_name, tabs_box):
        stack.set_visible_child_name(page_name)
        child = tabs_box.get_first_child()
        while child:
            child.remove_css_class("suggested-action")
            child = child.get_next_sibling()
        button.add_css_class("suggested-action")

    def open_create_window(self, parent_window, title="Create"):
        dialog = Gtk.Window(
            transient_for=parent_window,
            modal=True,
            title=title,
            default_width=400,
            default_height=300,
        )
        dialog.set_resizable(False)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        dialog.set_child(content_box)

        title_label = Gtk.Label(label="Add a new item to the list:")
        title_label.set_halign(Gtk.Align.START)
        content_box.append(title_label)

        entry = Gtk.Entry(placeholder_text="Enter item name...")
        content_box.append(entry)

        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.END)
        content_box.append(buttons_box)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.add_css_class("destructive-action")
        cancel_button.connect("clicked", lambda btn: dialog.destroy())
        buttons_box.append(cancel_button)

        add_button = Gtk.Button(label="Add")
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", lambda btn: self.on_add_button_clicked(entry, dialog))
        buttons_box.append(add_button)

        dialog.present()

   # @staticmethod
    def create_button(self, title, onclick):
        button = Gtk.Button()
        button.set_label(title)
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.CENTER)

        button.connect("clicked", lambda btn: onclick(title))

        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
        button {
            font-size: 18px;
            margin: 10px;
            padding: 10px;
            border-radius: 8px;
            border: 1px transparent;
            min-width: 150px;
            min-height: 40px;
        }
        """)

        context = button.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        return button

    def on_add_button_clicked(self, entry, dialog):
        item_name = entry.get_text()
        if item_name:
            # Do something with the item_name (e.g., add it to a list)
            print(f"Added item: {item_name}")
        dialog.destroy()

    def initDB(self):
        src.db.create_db_server()
        db_server = src.db.get_db_server()
        return db_server

    def saveVMInfo(self, db_server):
        for vm in self.vms:
            db_server.addEntry(vm)

    def initVMs(self, db_server):
        return db_server.getAllVMs()

    def create_popup_with_labels(self, title):
        # Statische Werte für die Attribute

        print(title)
        vm_found = None
        for vm in self.vms:
            if title == vm.get_name():
                vm_found = vm

        if vm_found is None:
            pass

        title = "VM Status"
        name = vm_found.get_name()
        public_ip = vm_found.get_public_ip()
        provider = vm_found.get_provider()
        username = vm_found.get_username()
        connection_date = vm_found.get_connection_date()
        total_cost = vm_found.get_total_cost()

        # Erstelle das Dialogfenster, das ein Popup im Parent-Fenster ist
        dialog = Gtk.Window(title=title, default_width=300, default_height=300)
        dialog.set_resizable(False)
        dialog.set_modal(True)
        dialog.set_transient_for(window)  # Macht es zu einem Popup im Parent-Fenster

        # Erstelle einen Box-Container für das Layout
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        dialog.set_child(content_box)

        # Füge die Labels für jedes Attribut hinzu
        label_name = Gtk.Label(label=f"Name: {name}")
        content_box.append(label_name)

        label_public_ip = Gtk.Label(label=f"Public IP: {public_ip}")
        content_box.append(label_public_ip)

        label_provider = Gtk.Label(label=f"Provider: {provider}")
        content_box.append(label_provider)

        label_username = Gtk.Label(label=f"Username: {username}")
        content_box.append(label_username)

        label_connection_date = Gtk.Label(label=f"Connection Date: {connection_date}")
        content_box.append(label_connection_date)

        label_total_cost = Gtk.Label(label=f"Total Cost: {total_cost}")
        content_box.append(label_total_cost)

        # Füge einen "OK"-Button hinzu, um das Popup zu schließen
        ok_button = Gtk.Button(label="OK")
        ok_button.connect("clicked", lambda btn: dialog.close())
        content_box.append(ok_button)

        # Zeige das Dialogfenster
        dialog.present()

    def bspWerte(self):
        self.vms.append(VirtualMachine(
            name="VM1",
            password="testPW",
            public_ip="10.0.0.0",
            provider="MyAss",
            username="benediktusmaxmimus",  # Adding username
            connection_date="17-09-2024 17:07:36", # %Y-%m-%d %H:%M:%S
            total_cost="2"
        ));


app = MyApp(application_id="cloud.surge")
app.run(sys.argv)
