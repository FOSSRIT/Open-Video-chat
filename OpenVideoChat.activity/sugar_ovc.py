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
:mod: `OpenVideoChat.activity/sugar_ovc` -- Open Video Chat
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthor:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


#External Imports
import logging
from gettext import gettext as _
from sugar3.presence import presenceservice
from sugar3.activity.activity import Activity
from sugar3.graphics.alert import NotifyAlert


#Local Imports
from gui import Gui
from gst_stack import GSTStack
from sugar_toolbar import Toolbar
from network_stack import NetworkStack


# Constants
SUGAR_MAX_PARTICIPANTS = 2


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class OpenVideoChatActivity(Activity):  # Sugar Activity Extends GtkWindow

    network_stack = None
    gstreamer_stack = None
    sharing_handler = None

    def __init__(self, handle):
        Activity.__init__(self, handle)
        logger.debug("Preparing Open Video Chat...")

        # Self-Enforced max_participants
        self.max_participants = SUGAR_MAX_PARTICIPANTS

        """ Setup GUI """
        self.set_toolbar_box(Toolbar(self))
        self.set_canvas(Gui())
        self.show()

        # Sugar OVC uses it's own method of user connectivity
        # To alleviate confusion we can disable the user-list in-app
        self.get_canvas().hide_contacts()

        # Sugar network logic implementation
        # Will require connecting signals for joined/shared depending on shared state
        # Store the signals to disconnect after first-run
        # Also, logical changes involve establishing
        if self.shared_activity:
            if self.get_shared():
                self.sugar_joined(None)
            else:
                self.sharing_handler = self.connect('shared', self.sugar_joined)
        else:
            self.sharing_handler = self.connect('shared', self.sugar_shared)

        """ Setup Network Stack """
        self.network_stack = NetworkStack({
            "contacts_changed": [
                self.get_canvas().add_remove_contacts,
            ],
            "setup_active_account": [
                self.get_canvas().deactive_chat,
            ],
            "reset_contacts": [
                self.get_canvas().reset_contacts,
            ],
            "new_chat_channel": [
                self.get_canvas().activate_chat,
            ],
            "chat_message_received": [
                self.get_canvas().receive_message,
            ],
        })

        # Register methods to network stack directly onto the ui components
        self.get_canvas().create_chat_channel = self.network_stack.request_chat_channel
        self.get_canvas().send_chat_message = self.network_stack.send_chat_message
        self.get_canvas().get_username = self.network_stack.get_username

        logger.info("Open Video Chat Prepared")

    """ Sugar Logic """

    def sugar_shared(self, sender):
        logger.debug("Shared from Sugar")

        # Remove Signal
        self.disconnect(self.sharing_handler)

        # Listen for invited buddies
        self.connect('buddy_joined', self.buddy_joined)

    def sugar_joined(self, sender):
        logger.debug ("Joined from Sugar")

        # Remove Signal
        self.disconnect(self.sharing_handler)

        # Grab our buddy and send to joined process
        buddy = self.shared_activity.get_joined_buddies()[0]
        self.buddy_joined(sender, buddy)

    def buddy_joined(self, sender, buddy):
        logger.debug("Processing new contact...")

        # Extract buddy contact id to identify or create new contact and establish channel

        # TESTING
        print buddy
        print dir(buddy)

        # Post message about user joining us in channel?

    # """ Automated Alert Handling """

    # def alert(self, title, text=None, timeout=5):
    #     if text != None:
    #         alert = NotifyAlert(timeout=timeout)
    #         alert.props.title = title
    #         alert.props.msg = text
    #         self.add_alert(alert)
    #         alert.connect('response', self.cancel_alert)
    #         alert.show()

    # def cancel_alert(self, alert, response_id):
    #     self.remove_alert(alert)

    """ Tear-Down Handling """

    def can_close(self):
        self.network_stack.shutdown()
        return True

    """ Journal Save and Restore """

    def write_file(self, file_path):
        file = open(file_path, 'w')
        try:
            file.write(self.get_canvas().get_history())
        except Exception:
            logger.debug("Unable to save activity.")
        finally:
            file.close()

    def read_file(self, file_path):
        file = open(file_path, 'r')
        try:
            for line in file:
                self.get_canvas().chat_write_line(line)
        except Exception:
            logger.debug("Unable to restore activity.")
        finally:
            file.close()
