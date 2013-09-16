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
import datetime
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
        Gtk.Grid.__init__(self, expand=True)
        logger.debug("Preparing GUI...")

        # Add Video
        self.attach(self.build_video(), 0, 0, 1, 1)

        # Add Chat
        self.attach(self.build_chat(), 0, 1, 1, 1)

        # Display Grid
        self.show()
        logger.info("OVC GUI Prepared")

    def build_video(self):
        logger.debug("Building Video...")

        # Create Video Component
        self.video = video = Gtk.DrawingArea(expand=True)
        video.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))
        video.show()

        # Return Video Component
        logger.debug("Built Video")
        return video

    def build_chat(self):
        logger.debug("Building Chat...")

        # Create Chat Components
        self.chat_text_view = chat_text_view = Gtk.TextView(editable=False, cursor_visible=False, wrap_mode=Gtk.WrapMode.WORD)
        chat_scrollable_history = Gtk.ScrolledWindow(hexpand=True, hscrollbar_policy=Gtk.PolicyType.NEVER, vscrollbar_policy=Gtk.PolicyType.AUTOMATIC, min_content_height=MIN_CHAT_HEIGHT)
        chat_scrollable_history.add(chat_text_view)
        self.chat_entry = chat_entry = Gtk.Entry(hexpand=True, max_length=MAX_CHAT_MESSAGE_SIZE, sensitive=False, placeholder_text="message...")
        chat_entry.connect("activate", self.send_message)
        self.chat_send_message_button = chat_send_message_button = Gtk.Button(_("Send"), sensitive=False)
        chat_send_message_button.connect("clicked", self.send_message)
        logger.debug("Built Chat Buffer, History, and Input")

        # Create Grid and Append Chat Components
        chat_grid = Gtk.Grid()
        chat_grid.attach(chat_scrollable_history, 0, 0, 2, 1)
        chat_grid.attach(chat_entry, 0, 1, 1, 1)
        chat_grid.attach(chat_send_message_button, 1, 1, 1, 1)
        logger.debug("Built Chat Grid")

        # Add Users List
        chat_grid.attach(self.build_user_list(), 2, 0, 1, 2)

        # Create Expander, Add Grid & Display
        chat_expander = Gtk.Expander(expanded=True, label=_("Chat"))
        chat_expander.add(chat_grid)
        chat_expander.show_all()
        logger.debug("Built Chat Expander")

        # Return Attachable Component
        logger.debug("Built Chat")
        return chat_expander

    def build_user_list(self):
        logger.debug("Building User List...")

        # Create Buffer for user storage
        self.user_list_store = Gtk.ListStore(
            str,        # Contact Alias
            object,     # TpContact Object
            object,     # Gtk3 TextBuffer
            object      # TpTextChannel
        )

        # Missing fields for new messages in contacts no-longer selected
        # dialog system should also supply messages about new contact attempts

        # Create a Tree View and supply it the List Store
        user_list_tree_view = Gtk.TreeView(self.user_list_store)

        # Define the columns of the Tree View to render the data
        user_tree_view_column = Gtk.TreeViewColumn(
            "User Alias",            # Column Title (is displayed)
            Gtk.CellRendererText(),  # Renderer Component
            text=0                   # Column Index
        )

        # Sort by the alias column
        user_tree_view_column.set_sort_column_id(0)

        # Add the column to the Tree View
        user_list_tree_view.append_column(user_tree_view_column)

        # Create a scrollbox for user list
        user_list_scrolled_window = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            min_content_height=(MIN_CHAT_HEIGHT - 20)
        )
        user_list_scrolled_window.add(user_list_tree_view)

        # Add a click handler to the tree view for user selection
        user_list_tree_view.connect('row-activated', self.user_selected)

        # Build Search Entry
        self.user_list_search_entry = user_list_search_entry = Gtk.Entry(max_length=MAX_CHAT_MESSAGE_SIZE, placeholder_text="username...")
        user_list_search_entry.set_tooltip_text(_("Search for contacts..."))

        # Apply the search entry to the Tree View
        user_list_tree_view.set_search_entry(user_list_search_entry)

        # Define Storage Container & Attach Components
        user_list_grid = Gtk.Grid()
        user_list_grid.attach(user_list_scrolled_window, 0, 0, 1, 1)
        user_list_grid.attach(user_list_search_entry, 0, 1, 1, 1)

        # Create an expander to show the users on-demand & display all components
        self.user_list_expander = user_list_expander = Gtk.Expander(label=_("Users"))
        user_list_expander.add(user_list_grid)
        user_list_expander.show_all()
        user_list_expander.connect('notify::expanded', self.find_user_set_focus)

        logger.debug("Built User List")

        # Return the top-level container
        return user_list_expander

    def find_user_set_focus(self, expander, data):
        if expander.get_expanded():
            self.user_list_search_entry.grab_focus()

    """ Contact Methods """

    def hide_contacts(self):
        self.user_list_expander.hide()

    def reset_contacts(self, callback, event, parent):

        # Clear the list
        self.user_list_store.clear()

        # Remove the text buffer
        self.chat_text_view.set_buffer(Gtk.TextBuffer())

    def add_remove_contacts(self, callback, event, parent, add_contacts, remove_contacts):

        # Add Contacts
        if add_contacts:
            for contact in add_contacts:
                self.user_list_store.append([
                    contact.get_alias(),    # Alias
                    contact,                # TpContact
                    None,                   # GtkTextBuffer (if/when activated)
                    None                    # TpTextChannel (if/when connected to)
                ])

        # Remove contacts
        if remove_contacts:
            for row in self.user_list_store:
                if row[1] in remove_contacts:
                    self.user_list_store.remove(row)

    def user_selected(self, tree_view, selected_index, column_object):
        logger.debug("Identifying selected user to initiate communication...")

        # We can pull the contact object from our store
        contact = self.user_list_store[selected_index][1]

        # If no GtkTextBuffer for this contact create & add to row
        if self.user_list_store[selected_index][2] is None:
            self.user_list_store[selected_index][2] = Gtk.TextBuffer()

        # Set GtkTextBuffer to main window
        self.chat_text_view.set_buffer(self.user_list_store[selected_index][2])

        # If no channel exists try to establish one
        if self.user_list_store[selected_index][3] is None:

            # Local message notifying chat is being enabled with selected user
            self.chat_write_line("\tSYSTEM: [Establishing channel with " + contact.get_alias() + "(" + contact.get_identifier() + ")...]")

            # Run method to create a chat channel
            self.create_chat_channel(contact)

    def activate_chat(self, callback, event, parent, channel):
        logger.debug("Chat services enabled on first-channel established...")

        # Enable Chat GtkButton & GtkEntry
        self.chat_entry.set_sensitive(True)
        self.chat_send_message_button.set_sensitive(True)

        # Grab Contact from channel
        contact = channel.get_target_contact()

        # Search for row
        active_row = None
        for row in self.user_list_store:

            # If contact is in our list set the row
            if contact is row[1]:
                active_row = row

        # Set it or Create it
        if active_row:
            active_row[3] = channel

        else:
            active_row = [
                contact.get_alias(),
                contact,
                Gtk.TextBuffer(),
                channel
            ]
            self.user_list_store.append(active_row)

        # Add text that user has joined channel
        self.chat_write_line("\tSYSTEM: [Established a channel with " + contact.get_alias() + "(" + contact.get_identifier() + ")...]")

        # Close user list if matching selected
        if self.chat_text_view.get_buffer() is active_row[2]:

            # Shrink users list
            self.user_list_expander.set_expanded(False)

            # Set focus into chat entry
            self.chat_entry.grab_focus()

    def deactive_chat(self, callback, event, parent, account):
        self.chat_entry.set_sensitive(False)
        self.chat_send_message_button.set_sensitive(False)

    """ Chat Methods """

    def send_message(self, sender):
        if self.chat_entry.get_text() != "":
            message = self.chat_entry.get_text()

            # Get Channel
            channel = None
            for row in self.user_list_store:
                if row[2] is self.chat_text_view.get_buffer():
                    channel = row[3]

            if channel:

                # Post Local Copy
                self.chat_write_line("%s [%s]: %s" % (self.get_username(), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))

                # Send Message
                self.send_chat_message(channel, message)

            self.chat_entry.set_text("")      # Empty Chat Entry
            self.chat_entry.grab_focus()      # Set focus back to chat entry

    def chat_write_line(self, line):

        # Write a message
        self.chat_text_view.get_buffer().insert(self.chat_text_view.get_buffer().get_end_iter(), line + "\n", -1)

        # Scroll to bottom
        self.chat_text_view.scroll_to_iter(self.chat_text_view.get_buffer().get_end_iter(), 0.1, False, 0.0, 0.0)

    def receive_message(self, callback, event, parent, message, contact):
        self.chat_write_line("%s [%s]: %s" % (contact.get_alias(), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message.to_text()[0]))
