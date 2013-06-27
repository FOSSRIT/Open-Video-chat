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


class OpenVideoChatActivity(Activity):

    def __init__(self, handle):
        Activity.__init__(self, handle)

        # Self-Enforced max_participants
        self.max_participants = SUGAR_MAX_PARTICIPANTS

        # Define Empty Properties
        self.network_stack = None
        self.gstreamer_stack = None

        # Set Owner
        self.owner = presenceservice.get_instance().get_owner()

        """ Setup GUI """
        self.set_canvas(Gui())
        self.attach(Toolbar(activity), 0, 0, 1, 1)
        self.show()

    #     logger.debug("Preparing GUI")
    #     self.set_title(_("OpenVideoChat"))
    #     self.set_canvas(Gui(self))
    #     self.set_toolbar_box(Toolbar())
    #     # activity.set_toolbar_box(self.build_toolbar(activity))

    #     # Setup GStreamer Stack
    #     logger.debug("Setting up GSTStack")
    #     self.gststack = GSTStack()
    #     self.get_canvas().set_gstreamer_stack(self.gststack);

    #     # Setup Network Stack
    #     logger.debug("Connect Event to Setup Network Stack on Demand")
    #     self.establish_activity_sharing(handle)

    # """ Networking & Network Stack Setup """

    # def establish_activity_sharing(self, handle=None):
    #     if self.shared_activity:
    #         self.sharing_handler = self.connect("joined", self.share_activity_internals)
    #     elif handle.uri:# XMPP Logic
    #         logger.debug("XMPP Connection Requested")
    #     else:
    #         self.sharing_handler = self.connect("shared", self.share_activity_internals)

    # def share_activity_internals(self, sender):
    #     # Create Network Stack
    #     sender.network_stack = NetworkStack()

    #     # Disconnect Sharing Handler
    #     sender.disconnect(sender.sharing_handler)

    #     # Setup Network Components
    #     sender.network_stack.setup(sender, sender.get_buddy)

    #     # Supply Network Stack to GUI
    #     sender.get_canvas().set_network_stack(sender.network_stack)

    # def get_buddy(self, handle):
    #     pservice = presenceservice.get_instance()
    #     tp_name, tp_path = pservice.get_preferred_connection()
    #     return pservice.get_buddy_by_telepathy_handle(tp_name, tp_path, handle)

    # """ Tear-Down Handling """

    # def can_close(self):
    #     logger.debug("Shutting down Network and GST")
    #     if self.network_stack is not None:
    #         self.network_stack.close()
    #     # self.gststack.start_stop_incoming_pipeline(False)
    #     # self.gststack.start_stop_outgoing_pipeline(False)
    #     return True

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
