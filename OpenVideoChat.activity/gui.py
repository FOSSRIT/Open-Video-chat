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

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthro:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# Imports
import logging
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants
MIN_CHAT_HEIGHT = 160
MAX_CHAT_MESSAGE_SIZE = 200


class Gui(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self, hexpand=True, vexpand=True)
        logger.debug("Preparing GUI...")

        # Add Video
        self.attach(self.build_video(), 0, 1, 1, 1)

        # Add Chat
        self.attach(self.build_chat(), 0, 2, 1, 1)

        # Display Grid
        self.show()
        logger.debug("GUI Prepared")

    def build_video(self):
        logger.debug("Building Video...")

        # Create Video Component
        self.video = video = Gtk.DrawingArea(vexpand=True, hexpand=True)
        video.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))
        video.show()

        # Return Video Component
        logger.debug("Built Video")
        return video

    def build_chat(self):
        logger.debug("Building Chat...")

        # Create Chat Components
        self.chat_text_buffer = chat_text_buffer = Gtk.TextBuffer()
        chat_text_view = Gtk.TextView(editable=False, buffer=chat_text_buffer, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD)
        chat_scrollable_history = Gtk.ScrolledWindow(hexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC, min_content_height=MIN_CHAT_HEIGHT)
        chat_scrollable_history.add(chat_text_view)
        chat_entry = Gtk.Entry(hexpand=True, max_length=MAX_CHAT_MESSAGE_SIZE)
        chat_entry.connect("activate", self.send_message)
        chat_send_message_button = Gtk.Button(_("Send"))
        chat_send_message_button.connect("clicked", self.send_message)
        logger.debug("Built Chat Buffer, History, and Input")

        # Create Grid and Append Chat Components
        chat_grid = Gtk.Grid()
        chat_grid.attach(chat_scrollable_history, 0, 0, 2, 1)
        chat_grid.attach(chat_entry, 0, 1, 1, 1)
        chat_grid.attach(chat_send_message_button, 1, 1, 1, 1)
        logger.debug("Built Chat Grid")

        # Add Users List
        self.chat_grid.attach(self.build_user_list(), 2, 0, 1, 1)

        # Create Expander, Add Grid & Display
        chat_expander = Gtk.Expander(expanded=True, label=_("Chat"))
        chat_expander.add(chat_grid)
        chat_expander.show_all()
        logger.debug("Built Chat Expander")

        # Return Attachable Component
        logger.debug("Built Chat")
        return chat_expander

    def build_user_list(self):
        logger.debug("Building User List")
        # Create User List Components
        self.user_list_search_entry = Gtk.Entry(max_length=MAX_CHAT_MESSAGE_SIZE)
        self.user_list_search_button = Gtk.Button(_("Search"))
        # self.user_list_search_entry.connect("clicked", undefined_user_search_function)
        self.user_list_grid = Gtk.Grid()
        # self.user_list_grid.attach(self.user_list, 0, 0, 2, 1)
        self.user_list_grid.attach(self.user_list_search_entry, 0, 1, 1, 1)
        self.user_list_grid.attach(self.user_list_search_button, 1, 1, 1, 1)
        self.user_list_expander = Gtk.Expander(label=_("Users"))
        self.user_list_expander.add(self.user_list_grid)
        self.user_list_expander.show_all()
        logger.debug("Built User List")
        return self.user_list_expander

    def send_message(self, sender):
        # Send a message over the tubes
        return False

    """ Chat Methods """

    # def get_history(self):
    #     return self.chat_text.get_text(
    #             self.chat_text.get_start_iter(),
    #             self.chat_text.get_end_iter(),
    #             True)

    # def chat_write_line(self, line):
    #     self.chat_text.insert(self.chat_text.get_end_iter(), line, -1)

    # def receive_message(self, username, message):
    #     self.chat_text.insert(self.chat_text.get_end_iter(), "%s [%s]: %s\n" % (username, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message), -1)
    #     self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1, False, 0.0, 0.0)

    # def send_message(self, sender):
    #     if self.chat_entry.get_text() != "":
    #         message = self.chat_entry.get_text()
    #         self.receive_message(self.network_stack.username, message)
    #         self.network_stack.send_message(message)
    #         self.chat_entry.set_text("")
    #         self.chat_entry.grab_focus()
