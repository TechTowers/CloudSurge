# author: Benedikt und Luka 4CN
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

# Window
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # Schaut ob die Applikation schon ein aktives Fenster hat
        if not app.get_active_window():
            # Initialisiert das Haupt-Fenster
            window = Gtk.ApplicationWindow(application=app)
            window.set_default_size(900, 600)
            window.set_title("CloudSurge")

            # Main-box Layout
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            window.set_child(main_box)

            # Header bar Setup
            header_bar = window.get_titlebar()
            if not header_bar:
                header_bar = Gtk.HeaderBar()
                window.set_titlebar(header_bar)

            # "Create" button (Plus)
            create_button = Gtk.Button(label="+")
            create_button.connect("clicked", lambda btn: self.open_create_window(window))
            header_bar.pack_start(create_button)

            # Box for ToggleButtons (tabs) in the center
            tabs_box = Gtk.Box(spacing=10)
            header_bar.set_title_widget(tabs_box)

            # Stack um Daten über die Tabs zu halten
            stack = Gtk.Stack()
            main_box.append(stack)

            # ToggleButton für Providers tab
            providers_button = Gtk.Button(label="Providers")
            tabs_box.append(providers_button)
            providers_button.connect("clicked", self.activate_menu, stack, "providers", tabs_box)

            # ToggleButton für VMs tab
            vms_button = Gtk.Button(label="VMs")
            tabs_box.append(vms_button)
            vms_button.connect("clicked", self.activate_menu, stack, "vms", tabs_box)

            # ToggleButton für About Us tab
            aboutus_button = Gtk.Button(label="About Us")
            tabs_box.append(aboutus_button)
            aboutus_button.connect("clicked", self.activate_menu, stack, "About Us", tabs_box)

            stack.add_named(self.get_provider_page(), "providers")
            stack.add_named(self.get_vm_page(), "vms")
            stack.add_named(self.get_about_us_page(), "About Us")

            # Show all elements
            window.present()
            providers_button.emit("clicked")

    def get_vm_page(self):
        vms_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vms_page.append(Gtk.Label(label="List of VMs:"))
        vm_list = Gtk.ListBox()
        # vm_list.append(Gtk.Label(label="VM 1"))
        vm_list.append(self.create_label("test", 1))
        vm_list.append(Gtk.Label(label="VM 2"))
        vm_list.append(Gtk.Label(label="VM 3"))
        vms_page.append(vm_list)
        return vms_page

    def get_provider_page(self):
        providers_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        providers_page.append(Gtk.Label(label="List of Providers:"))
        provider_list = Gtk.ListBox()
        provider_list.append(Gtk.Label(label="Provider 1"))
        provider_list.append(Gtk.Label(label="Provider 2"))
        provider_list.append(Gtk.Label(label="Provider 3"))
        providers_page.append(provider_list)
        return providers_page

    def get_about_us_page(self):
        aboutus_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        aboutus_page.append(Gtk.Label(label="About us:"))
        return aboutus_page

    def activate_menu(self, button, stack, page_name, tabs_box):
        # Setz die im Stack sehbare Attribute
        stack.set_visible_child_name(page_name)

        # Andere Button Hintergründe ausmachen
        child = tabs_box.get_first_child()
        while child:
            child.remove_css_class("suggested-action")
            child = child.get_next_sibling()

        button.add_css_class("suggested-action")

    def open_create_window(self, parent_window, title="Create"):
        # Create a pop-up dialog window
        dialog = Gtk.Window(
            transient_for=parent_window,
            modal=True,
            title=title,
            default_width=400,
            default_height=300,
        )
        dialog.set_resizable(False)

        # Main vertical box for content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        dialog.set_child(content_box)

        # Title label
        title_label = Gtk.Label(label="Add a new item to the list:")
        title_label.set_halign(Gtk.Align.START)
        content_box.append(title_label)

        # Entry field for user input
        entry = Gtk.Entry(placeholder_text="Enter item name...")
        content_box.append(entry)

        # Buttons box
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.END)
        content_box.append(buttons_box)

        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.add_css_class("destructive-action")
        cancel_button.connect("clicked", lambda btn: dialog.destroy())
        buttons_box.append(cancel_button)

        # Add button
        add_button = Gtk.Button(label="Add")
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", lambda btn: on_add_button_clicked(entry, dialog))
        buttons_box.append(add_button)

        # Show the dialog window
        dialog.present()

    @staticmethod
    def create_label(title, onklick) -> Gtk.Label:
        label = Gtk.Label()
        label.set_text(title)

        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
        label {
            font-size: 20px;
        }
        """)

        context = label.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        return label

app = MyApp(application_id="cloud.surge")
app.run(sys.argv)
