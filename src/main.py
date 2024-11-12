import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .custom-button {
            background-color: #333333;
            color: #ffffff;
        }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_activate(self, app):
        self.load_css()

        # Check if the application already has a window
        if not app.get_active_window():
            # Create main application window
            window = Gtk.ApplicationWindow(application=app)
            window.set_default_size(600, 400)
            window.set_title("Simple Tabbed Application")

            # Main box layout
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            window.set_child(main_box)

            # Header bar setup
            header_bar = Gtk.HeaderBar()
            main_box.append(header_bar)

            # "Create" button (Plus sign) on the top left
            create_button = Gtk.Button(label="+")
            create_button.connect("clicked", self.on_create_button_clicked)
            header_bar.pack_start(create_button)

            # Box for ToggleButtons (tabs) in the center
            tabs_box = Gtk.Box(spacing=10)
            header_bar.set_title_widget(tabs_box)

            # Stack to hold content for each tab
            stack = Gtk.Stack()
            main_box.append(stack)

            # ToggleButton for Providers tab
            providers_button = Gtk.Button(label="Providers")
            tabs_box.append(providers_button)
            providers_button.connect("clicked", self.activate_menu, stack, "providers", tabs_box)

            # ToggleButton for VMs tab
            vms_button = Gtk.Button(label="VMs")
            tabs_box.append(vms_button)
            vms_button.connect("clicked", self.activate_menu, stack, "vms", tabs_box)

            # ToggleButton for About Us tab
            aboutus_button = Gtk.Button(label="About Us")
            tabs_box.append(aboutus_button)
            aboutus_button.connect("clicked", self.activate_menu, stack, "About Us", tabs_box)

            # Stack pages for each tab
            # Providers page
            providers_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            providers_page.append(Gtk.Label(label="List of Providers:"))
            provider_list = Gtk.ListBox()
            provider_list.append(Gtk.Label(label="Provider 1"))
            provider_list.append(Gtk.Label(label="Provider 2"))
            provider_list.append(Gtk.Label(label="Provider 3"))
            providers_page.append(provider_list)
            stack.add_named(providers_page, "providers")

            # VMs page
            vms_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vms_page.append(Gtk.Label(label="List of VMs:"))
            vm_list = Gtk.ListBox()
            vm_list.append(Gtk.Label(label="VM 1"))
            vm_list.append(Gtk.Label(label="VM 2"))
            vm_list.append(Gtk.Label(label="VM 3"))
            vms_page.append(vm_list)
            stack.add_named(vms_page, "vms")

            # About Us page
            aboutus_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            aboutus_page.append(Gtk.Label(label="About us:"))
            stack.add_named(aboutus_page, "About Us")

            # Show all elements
            window.present()
            providers_button.emit("clicked")

    def activate_menu(self, button, stack, page_name, tabs_box):
        # Set the stack's visible page based on the selected tab
        stack.set_visible_child_name(page_name)

        # Deactivate other buttons in the tabs box and activate the selected one
        child = tabs_box.get_first_child()
        while child:
            child.remove_css_class("custom-button")
            child = child.get_next_sibling()

        # Add custom style to the selected button
        button.add_css_class("custom-button")

    def on_create_button_clicked(self, button):
        # Pop-up window on create button click
        dialog = Gtk.MessageDialog(
            transient_for=button.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Create New Entry",
        )
        dialog.format_secondary_text("This is where you can create a new entry.")
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.show()

app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
