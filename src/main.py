import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        # Create main application window
        window = Gtk.ApplicationWindow(application=app)
        window.set_default_size(600, 400)
        window.set_title("Simple Tabbed Application")

        # Create main box layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        window.set_child(main_box)

        # Header bar with a "Create" button on the left
        header_bar = Gtk.HeaderBar()
        main_box.append(header_bar)

        # "Create" button (Plus Sign) on the top left
        create_button = Gtk.Button(label="+")
        create_button.connect("clicked", self.on_create_button_clicked)
        header_bar.pack_start(create_button)

        # Notebook for tabs
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        notebook.set_tab_label(notebook, None)
        main_box.append(notebook)

        # Tab 1: Providers
        providers_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        providers_page.append(Gtk.Label(label="List of Providers:"))
        provider_list = Gtk.ListBox()
        provider_list.append(Gtk.Label(label="Provider 1"))
        provider_list.append(Gtk.Label(label="Provider 2"))
        provider_list.append(Gtk.Label(label="Provider 3"))
        providers_page.append(provider_list)

        notebook.append_page(providers_page, Gtk.Label(label="Providers"))

        # Tab 2: VMs
        vms_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vms_page.append(Gtk.Label(label="List of VMs:"))
        vm_list = Gtk.ListBox()
        vm_list.append(Gtk.Label(label="VM 1"))
        vm_list.append(Gtk.Label(label="VM 2"))
        vm_list.append(Gtk.Label(label="VM 3"))
        vms_page.append(vm_list)

        notebook.append_page(vms_page, Gtk.Label(label="VMs"))

        # Show all elements
        window.show()

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
