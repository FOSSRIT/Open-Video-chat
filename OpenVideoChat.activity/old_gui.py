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
:mod: `OpenVideoChat.activity/gui` -- Open Video Chat Gui
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthor:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# External Imports
import logging
import datetime
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.graphics.toolbarbox import ToolbarButton


# Constants
MAX_MESSAGE_SIZE = 200
MIN_CHAT_HEIGHT = 180
DEFAULT_PREVIEW_SIZE = 0.25


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Gui(Gtk.Grid):
    def __init__(self, activity):
        Gtk.Grid.__init__(self)

        # Disable GUI Components until network connections established
        self.disable_net_options()
        self.disable_gst_options()

        # Display GUI
        self.show()

        # Status Message
        logger.debug("Finished Preparing GUI")

    """ Resource Methods """

    def set_network_stack(self, network_stack):
        logger.debug("Network Stack has been supplied.")

        # Apply Network Stack for Local Use
        self.network_stack = network_stack
        self.buddy_handler = None

        # Establish Network Channel Connection
        network_stack.connect(self.receive_message)

        # Connect to Buddies
        if len(network_stack.shared_activity.get_joined_buddies()) > 0:
            self.buddy_joined(network_stack.shared_activity, network_stack.shared_activity.get_joined_buddies()[0])
        else:
            self.buddy_handler = network_stack.shared_activity.connect("buddy-joined", self.buddy_joined)

    def set_gstreamer_stack(self, gstreamer_stack):
        logger.debug("GST Stack has been supplied.")

        # Set local GST Access
        self.gstreamer_stack = gstreamer_stack

        # Supply preview window when able
        if self.movie_window_preview.get_realized():
            self.render_preview()
        else:
            self.movie_window_preview.connect('realize', self.render_preview)

        # Supply incoming window when able
        # if self.movie_window_incoming.get_realized():
        #     self.render_incoming()
        # else:
        #     self.movie_window_incoming.connect('realize', self.render_incoming)

    def toggle_video(self, sender=None):
        # Grab Button if not supplied
        if sender is None:
            self.toolbar.get_nth_item(1)

        # Update Button Icon & Process Change to Video
        if (sender.get_icon_name() == "activity-stop"):
            sender.set_icon_name("activity-start")
            sender.set_tooltip_text(_("Start Video"))
            # Call to start incoming GStreamer to restart video
        else:
            sender.set_icon_name("activity-stop")
            sender.set_tooltip_text(_("Stop Video"))
            # Call to stop incoming GStreamer to end video

        # Toggle Incoming Visibility & Preview Size
        self.toggle_incoming_visibility()
        self.toggle_preview_size()

    def toggle_audio(self, sender=None):
        # Grab Button if not supplied
        if sender is None:
            self.toolbar.get_nth_item(2)

        # Update Button Icon & Process Change to Audio
        if sender.get_icon_name() == "speaker-000":
            sender.set_icon_name("speaker-100")
            sender.set_tooltip_text(_("Turn on Sound"))
            # Call to start GStreamer to restart audio
        else:
            sender.set_icon_name("speaker-000")
            sender.set_tooltip_text(_("Mute Sound"))
            # Call to stop GStreamer to end audio

    def toolbar_toggle_preview_visibility(self, sender=None):
        # Grab Button if not supplied
        if sender is None:
            self.toolbar.get_nth_item(3)

        # Update Button Icon
        if sender.get_icon_name() == "list-add":
            sender.set_icon_name("list-remove")
            sender.set_tooltip_text(_("Hide Preview Video"))
        else:
            sender.set_icon_name("list-add")
            sender.set_tooltip_text(_("Show Preview Video"))

        # Call Preview Visibility Toggle
        self.toggle_preview_visibility()

    def enable_net_options(self):
        self.chat_send_button.set_sensitive(True)
        self.chat_entry.set_sensitive(True)
        self.chat_entry.grab_focus()

    def disable_net_options(self):
        self.chat_send_button.set_sensitive(False)
        self.chat_entry.set_sensitive(False)

    def enable_gst_options(self):
        self.toolbar.get_nth_item(1).set_sensitive(True)
        self.toolbar.get_nth_item(2).set_sensitive(True)

    def disable_gst_options(self):
        self.toolbar.get_nth_item(1).set_sensitive(False)
        self.toolbar.get_nth_item(2).set_sensitive(False)

    def toggle_preview_visibility(self):
        if self.movie_window_preview.get_visible():
            self.movie_window_preview.hide()
        else:
            self.movie_window_preview.show()

    def toggle_incoming_visibility(self):
        logger.debug("Temporarily Stairs")
        # if self.movie_window_incoming.get_visible():
        #     self.movie_window_incoming.hide()
        # else:
        #     self.movie_window_incoming.show()
        #     self.movie_window_preview.hide()
        #     self.movie_window_preview.show()

    """ Video Methods """

    def render_preview(self, sender):
        self.gstreamer_stack.build_working_preview(self.movie_window_preview.get_window().get_xid())
        # self.movie_window_preview.get_allocation().width,
        # self.movie_window_preview.get_allocation().height

    def render_incoming(self, sender):
        logger.debug("Temporarily Stairs")
        # self.gstreamer_stack.set_incoming_window(self.movie_window_incoming.get_window().get_xid())

    def set_incoming_size(self):
        logger.debug("Temporarily Stairs")
        # self.movie_window_incoming.set_size_request(
        #         self.movie_window_incoming.get_parent().get_parent().get_allocation().width,
        #         self.movie_window_incoming.get_parent().get_parent().get_allocation().height)

    def toggle_preview_size(self):
        if self.movie_window_preview.get_size_request()[0] == -1:
            self.movie_window_preview.set_size_request(1, 1)
        else:
            self.movie_window_preview.set_size_request(-1, -1)

        # Execute Resize Logic
        self.set_preview_size()

    """ Event Connected Methods """

    def buddy_joined(self, shared_activity, buddy):
        # Disconnect Handler if exists
        if self.buddy_handler is not None:
            shared_activity.disconnect(self.buddy_handler)

        # Post message about connected buddy
        self.receive_message(buddy.props.nick, _("connected to service."))

        # Enable Chat GUI Components
        self.enable_net_options()

        # Send Buddy our IP

        # Connect Disconnect Handler
        self.buddy_handler = shared_activity.connect('buddy-left', self.buddy_left)

    def buddy_left(self, shared_activity, buddy):
        # Disconnect Handler
        if self.buddy_handler is not None:
            shared_activity.disconnect(self.buddy_handler)

        # Message that buddy left
        self.receive_message(buddy.props.nick, _("has disconnected."))

        # Disable GUI
        self.disable_net_options()

        # Add Buddy Joined Listener
        self.buddy_handler = shared_activity.connect('buddy-joined', self.buddy_left)
