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
:mod: `OpenVideoChat.activity/ovc` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


#External Imports
import logging
from gi.repository import Gtk


#Local Imports
from gui import Gui
from account_manager import AccountManager
from toolbar import Toolbar
from network_stack import NetworkStack


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants
DEFAULT_WINDOW_SIZE = {
    'width': 1200,
    'height': 900
}


class OpenVideoChat(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Open Video Chat")
        logger.debug("Preparing Open Video Chat...")

        # Assume a default size of 1200x900
        self.set_default_size(DEFAULT_WINDOW_SIZE['width'], DEFAULT_WINDOW_SIZE['height'])

        # Connect Internal Window Event Signals
        self.connect('check-resize', self.on_resize)

        """ Setup GUI """
        self.add(Gtk.Grid(expand=True, visible=True))
        self.get_child().attach(Toolbar(self.swap_grids), 0, 0, 1, 1)
        self.gui = Gui()
        self.accounts = AccountManager()
        self.get_child().attach(self.gui, 0, 1, 1, 1)
        self.show()

        """ Setup Network Stack """
        self.network_stack = NetworkStack()

        # Supply network stack with callbacks
        self.network_stack.register_callback("get_jabber_accounts", self.accounts.add_accounts)
        self.network_stack.register_callback("contacts_changed", self.gui.add_remove_contacts)
        self.network_stack.register_callback("reset_contacts", self.gui.reset_contacts)

        # Supply other components with callback methods (until the callback system can be expanded)
        self.accounts.switch_active_account = self.network_stack.switch_active_account
        self.gui.create_text_channel = self.network_stack.create_text_channel


        # self.network_stack.populate_accounts_callback(self.accounts.add_account_to_list)
        # self.network_stack.setup()

        # Supply network stack with user population method to add to list
        # self.network_stack.set_populate_users(self.gui.add_a_contact)

        # Supply network stack with gui chat enabled callback on channel activation
        # self.network_stack.set_chat_activation(self.gui.activate_chat)

        # Supply gui with network channel establishment callback
        # self.gui.set_chat_channel_initializer(self.network_stack.setup_chat_channel)

        # Supply gui with send_message network callback
        # self.gui.set_send_chat_message(self.network_stack.send_chat_message)

        """ Setup GStreamer Stack """

        # Proceed with Application Loop
        logger.info("Open Video Chat Prepared")

    def can_close(self):
        # self.network_stack.close_chat_channel()  # Close Chat Channel(s)
        # **FIXME** Does not wait for async closures
        return True

    def on_resize(self, trigger):
        # Logic for resize, probably unnecessary but could be tied to
        # GStreamer for scaling if feasible, but scaling eats more CPU
        return False

    def swap_grids(self, *args):
        logger.debug("Swapping gui to accounts...")
        if self.gui in self.get_child().get_children():
            self.get_child().remove(self.gui)
            self.get_child().attach(self.accounts, 0, 1, 1, 1)
        else:
            self.get_child().remove(self.accounts)
            self.get_child().attach(self.gui, 0, 1, 1, 1)
