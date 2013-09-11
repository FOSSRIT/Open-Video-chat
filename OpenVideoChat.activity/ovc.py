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

    gui = None
    network_stack = None
    gstreamer_stack = None

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
        self.network_stack = NetworkStack({
            "get_jabber_accounts": [
                self.accounts.add_accounts,
            ],
            "contacts_changed": [
                self.gui.add_remove_contacts,
            ],
            "setup_active_account": [
                self.accounts.display_active_account,
                self.gui.deactive_chat,
            ],
            "reset_contacts": [
                self.gui.reset_contacts,
            ],
            "new_chat_channel": [
                self.gui.activate_chat,
            ],
            "chat_message_received": [
                self.gui.receive_message,
            ],
        })

        # Register methods to network stack directly onto the ui components
        self.accounts.switch_active_account = self.network_stack.switch_active_account
        self.gui.create_chat_channel = self.network_stack.request_chat_channel
        self.gui.send_chat_message = self.network_stack.send_chat_message

        """ Setup GStreamer Stack """

        # Proceed with Application Loop
        logger.info("Open Video Chat Prepared")

    def can_close(self):
        self.network_stack.shutdown()
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
