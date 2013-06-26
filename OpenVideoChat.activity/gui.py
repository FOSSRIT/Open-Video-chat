

# Imports
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _


# Constants
ICONS = {
    'play': 'media-playback-start-insensitive.svg',
    'stop': 'media-playback-stop-insensitive.svg',
    'unmute': 'speaker-100.svg',
    'mute': 'speaker-000.svg'
}
DEFAULT_WINDOW_SIZE = {
    'width': 800,
    'height': 600
}
MIN_CHAT_HEIGHT = 160
MAX_CHAT_MESSAGE_SIZE = 200


class Gui(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Open Video Chat")
        self.connect("delete-event", Gtk.main_quit)

        # Assume a default size of 800x600
        self.set_default_size(DEFAULT_WINDOW_SIZE['width'], DEFAULT_WINDOW_SIZE['height'])

        # Create a Grid Layout & Add to Window
        self.layout = Gtk.Grid()
        self.add(self.layout)
        self.layout.show()

        # Add Toolbar
        self.build_toolbar()

        # Add Video
        self.build_video()

        # Add Chat
        self.build_chat()

        # Add Resize Event
        self.connect('check-resize', self.on_resize)

        # Display Contents & Execute Main Loop
        self.show()

    def build_toolbar(self):

        # Create Toolbar & Attach to Expander
        self.toolbar = Gtk.Toolbar()

        # Create Toggles
        self.toggles = {
            'outgoing-video': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Video", icon_widget=Gtk.Image(file=ICONS['stop'])),
            'outgoing-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Audio", icon_widget=Gtk.Image(file=ICONS['mute'])),
            'incoming-video': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Video", icon_widget=Gtk.Image(file=ICONS['stop'])),
            'incoming-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Audio", icon_widget=Gtk.Image(file=ICONS['mute']))
        }

        # Append to Window
        self.toolbar.insert(self.toggles['outgoing-video'], 0)
        self.toolbar.insert(self.toggles['outgoing-audio'], 1)
        self.toolbar.insert(self.toggles['incoming-video'], 2)
        self.toolbar.insert(self.toggles['incoming-audio'], 3)

        # Create Expander, add toolbar, connect to grid, and display
        self.toolbar_expander = Gtk.Expander(expanded=True)
        self.toolbar.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))
        self.toolbar_expander.add(self.toolbar)
        self.layout.attach(self.toolbar_expander, 0, 0, 1, 1)
        self.toolbar_expander.show_all()

    def build_video(self):

        # Create a Gtk Drawing Area & Append to grid then display
        self.video = Gtk.DrawingArea(vexpand=True, hexpand=True)
        self.video.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .8))
        self.layout.attach(self.video, 0, 1, 1, 1)
        self.video.show()

    def build_chat(self):

        # Create Chat Components
        self.chat_text_buffer = Gtk.TextBuffer()
        self.chat_text_view = Gtk.TextView(editable=False, buffer=self.chat_text_buffer, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD)
        self.chat_scrollable_history = Gtk.ScrolledWindow(hexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC, min_content_height=MIN_CHAT_HEIGHT)
        self.chat_scrollable_history.add(self.chat_text_view)
        self.chat_entry = Gtk.Entry(hexpand=True, max_length=MAX_CHAT_MESSAGE_SIZE)
        self.chat_entry.connect("activate", self.send_message)
        self.chat_send_message_button = Gtk.Button(_("Send"))
        self.chat_send_message_button.connect("clicked", self.send_message)

        # # Create User List Components
        # self.user_list_search_entry = Gtk.Entry(max_length=MAX_CHAT_MESSAGE_SIZE)
        # self.user_list_search_button = Gtk.Button(_("Search"))
        # # self.user_list_search_entry.connect("clicked", undefined_user_search_function)
        # self.user_list_grid = Gtk.Grid()
        # # self.user_list_grid.attach(self.user_list, 0, 0, 2, 1)
        # self.user_list_grid.attach(self.user_list_search_entry, 0, 1, 1, 1)
        # self.user_list_grid.attach(self.user_list_search_button, 1, 1, 1, 1)
        # self.user_list_expander = Gtk.Expander(label=_("Users"))
        # self.user_list_expander.add(self.user_list_grid)
        # self.user_list_expander.show_all()

        # Create Grid and Append Chat Components
        self.chat_grid = Gtk.Grid()
        self.chat_grid.attach(self.chat_scrollable_history, 0, 0, 2, 1)
        self.chat_grid.attach(self.chat_entry, 0, 1, 1, 1)
        self.chat_grid.attach(self.chat_send_message_button, 1, 1, 1, 1)
        # self.chat_grid.attach(self.user_list_expander, 2, 0, 1, 1)

        # Create Expander & Add Grid to Expander and Expander to Layout Grid
        self.chat_expander = Gtk.Expander(expanded=True, label=_("Chat"))
        self.chat_expander.add(self.chat_grid)
        self.layout.attach(self.chat_expander, 0, 2, 1, 1)
        self.chat_expander.show_all()

    def send_message(self, sender):
        return False



    # May remove this if I can figure out a smarter implementation
    def on_resize(self, trigger):
        # On resize adjust video components etc
        return False
