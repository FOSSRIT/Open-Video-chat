#    This file is part of OpenVideoChat.
#
#    OpenVideoChat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenVideoChat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenVideoChat.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod: `OpenVideoChat.activity/gui` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# Imports
import logging
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Constants
MIN_CHAT_HEIGHT = 160
MAX_CHAT_MESSAGE_SIZE = 200


class Gui(Gtk.Grid):
    def __init__(self):

        # Add Video
        logger.debug("Adding Video")
        self.attach(self.build_video(), 0, 1, 1, 1)

        # Add Chat
        logger.debug("Adding Chat")
        self.attach(self.build_chat(), 0, 2, 1, 1)

        # Display Grid
        self.show()

    def build_video(self):

        # Create [GtkDrawingArea](https://developer.gnome.org/gtk3/3.0/GtkDrawingArea.html) & [Modify Background](https://developer.gnome.org/gtk3/3.0/gtk-question-index.html)
        self.video = video = Gtk.DrawingArea(vexpand=True, hexpand=True)
        video.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))
        video.show()

        # Return Video Component
        return video

    def build_chat(self):

        # Create Chat Components
        self.chat_text_buffer = chat_text_buffer = Gtk.TextBuffer()
        chat_text_view = Gtk.TextView(editable=False, buffer=chat_text_buffer, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD)
        chat_scrollable_history = Gtk.ScrolledWindow(hexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC, min_content_height=MIN_CHAT_HEIGHT)
        chat_scrollable_history.add(chat_text_view)
        chat_entry = Gtk.Entry(hexpand=True, max_length=MAX_CHAT_MESSAGE_SIZE)
        chat_entry.connect("activate", self.send_message)
        chat_send_message_button = Gtk.Button(_("Send"))
        chat_send_message_button.connect("clicked", self.send_message)

        # Create Grid and Append Chat Components
        chat_grid = Gtk.Grid()
        chat_grid.attach(chat_scrollable_history, 0, 0, 2, 1)
        chat_grid.attach(chat_entry, 0, 1, 1, 1)
        chat_grid.attach(chat_send_message_button, 1, 1, 1, 1)

        # Add User List (Multi-User Feature - Not yet ready for implementation)
        # self.chat_grid.attach(self.build_user_list(), 2, 0, 1, 1)

        # Create Expander, Add Grid & Display
        chat_expander = Gtk.Expander(expanded=True, label=_("Chat"))
        chat_expander.add(chat_grid)
        chat_expander.show_all()

        # Return Attachable Component
        return chat_expander

    def build_user_list(self):
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
        return False

    def send_message(self, sender):
        # Send a message over the tubes
        return False
