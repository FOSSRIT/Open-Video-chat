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
:mod: `OpenVideoChat/OpenVideoChat.activity/gui` -- Open Video Chat Gui
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

        # Set Activity Title
        activity.set_title(_("OpenVideoChat"))

        # Add Video & Chat Containers
        self.add(self.build_video())
        self.attach(self.build_chat(), 0, 1, 1, 1)

        # Create & Apply Toolbar to Activity
        activity.set_toolbar_box(self.build_toolbar(activity))

        # Add Resize Event
        self.connect('check-resize', self.resized)

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

    """ GUI Component Establishment """

    def build_video(self):
        # Prepare Video Display
        self.movie_window_preview = Gtk.DrawingArea()
        # self.movie_window_incoming = Gtk.DrawingArea()

        # Use Fixed to append overlays to an overlay
        # video_fixed = Gtk.Fixed()
        # video_fixed.put(self.movie_window_incoming, 0, 0)
        # video_fixed.put(self.movie_window_preview, 0, 0)
        # video_fixed.set_halign(Gtk.Align.START)
        # video_fixed.set_valign(Gtk.Align.START)
        #self.movie_window_preview.show()
        #video_fixed.show()


        # Use event box for background coloring
        video_eventbox = Gtk.EventBox()
        video_eventbox.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01,.01,.01,.8))
        video_eventbox.set_hexpand(True)
        video_eventbox.set_vexpand(True)
        # video_eventbox.add(video_fixed)
        video_eventbox.add(self.movie_window_preview)
        video_eventbox.show_all()

        # Return Overlay Container
        return video_eventbox

    def build_chat(self):
        # Prepare Chat Text Container
        self.chat_text = Gtk.TextBuffer()
        self.text_view = Gtk.TextView()
        self.text_view.set_buffer(self.chat_text)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Prepare Scrollable History
        chat_history = Gtk.ScrolledWindow()
        chat_history.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        chat_history.set_min_content_height(MIN_CHAT_HEIGHT)
        chat_history.add(self.text_view)
        chat_history.set_hexpand(True)

        # Send button to complete feel of a chat program
        self.chat_entry = Gtk.Entry()
        self.chat_entry.set_max_length(MAX_MESSAGE_SIZE)
        self.chat_entry.connect("activate", self.send_message)
        self.chat_entry.set_hexpand(True)
        self.chat_send_button = Gtk.Button(_("Send"))
        self.chat_send_button.connect("clicked", self.send_message)

        # Wrap expanded Entry and normal-sized Send buttons into Grid Row
        chat_grid = Gtk.Grid()
        chat_grid.attach(chat_history, 0, 0, 2, 1)
        chat_grid.attach(self.chat_entry, 0, 1, 1, 1)
        chat_grid.attach(self.chat_send_button, 1, 1, 1, 1)

        # Chat expander allows visibly toggle-able container for all chat components
        chat_expander = Gtk.Expander()
        chat_expander.set_label(_("Chat"))
        chat_expander.set_expanded(True)
        chat_expander.add(chat_grid)

        # Display all chat components
        chat_expander.show_all()

        # Return entire expander
        return chat_expander

    def build_toolbar(self, activity):
        # Prepare Primary Toolbar Container
        toolbar_box = ToolbarBox();

        # Create activity button
        toolbar_box.toolbar.insert(ActivityButton(activity), -1)

        # Video Toggle
        video_toggle_button = ToolButton()
        video_toggle_button.connect("clicked", self.toggle_video)
        toolbar_box.toolbar.insert(video_toggle_button, 1)
        self.toggle_video(video_toggle_button)

        # Audio Toggle
        audio_toggle_button = ToolButton()
        audio_toggle_button.connect("clicked", self.toggle_audio)
        toolbar_box.toolbar.insert(audio_toggle_button, 2)
        self.toggle_audio(audio_toggle_button)

        # Toggle Preview Display Button
        preview_toggle_button = ToolButton()
        preview_toggle_button.connect("clicked", self.toolbar_toggle_preview_visibility)
        toolbar_box.toolbar.insert(preview_toggle_button, 3)
        self.toolbar_toggle_preview_visibility(preview_toggle_button)

        # Forced Refresh
        reload_video = ToolButton("view-refresh")
        reload_video.set_tooltip_text(_("Reload Video"))
        reload_video.connect("clicked", self.force_redraw)
        toolbar_box.toolbar.insert(reload_video, -1)

        # Push stop button to far right
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)

        # Create Share Button
        toolbar_box.toolbar.insert(ShareButton(activity), -1)

        # Create stop button
        toolbar_box.toolbar.insert(StopButton(activity), -1)

        # Add reference to toolbar items
        self.toolbar = toolbar_box.toolbar

        # Display all components & Return
        toolbar_box.show_all()
        return toolbar_box

    def toggle_video(self, sender=None):
        # Grab Button if not supplied
        if sender == None:
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
        if sender == None:
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
        if sender == None:
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

    def set_preview_size(self):
        # Resize Preview
        if self.movie_window_preview.get_size_request()[0] == -1:
            self.movie_window_preview.set_size_request(
                    self.movie_window_preview.get_parent().get_parent().get_allocation().width,
                    self.movie_window_preview.get_parent().get_parent().get_allocation().height)
        else:
            self.movie_window_preview.set_size_request(
                    self.movie_window_preview.get_parent().get_parent().get_allocation().width * DEFAULT_PREVIEW_SIZE,
                    self.movie_window_preview.get_parent().get_parent().get_allocation().height * DEFAULT_PREVIEW_SIZE)

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

    def resized(self):
        logger.debug("Resizing Video to match Display")

        # Execute resize methods
        self.set_incoming_size()
        self.set_preview_size()


    """ Chat Methods """

    def get_history(self):
        return self.chat_text.get_text(
                self.chat_text.get_start_iter(),
                self.chat_text.get_end_iter(),
                True)

    def chat_write_line(self, line):
        self.chat_text.insert(self.chat_text.get_end_iter(), line, -1)

    def receive_message(self, username, message):
        self.chat_text.insert(self.chat_text.get_end_iter(), "%s [%s]: %s\n" % (username, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message), -1)
        self.text_view.scroll_to_iter(self.chat_text.get_end_iter(), 0.1, False, 0.0, 0.0)

    def send_message(self, sender):
        if self.chat_entry.get_text() != "":
            message = self.chat_entry.get_text()
            self.receive_message(self.network_stack.username, message)
            self.network_stack.send_message(message)
            self.chat_entry.set_text("")
            self.chat_entry.grab_focus()


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

    def connect_incoming_movie(self):
        # Handle Incoming Construction
        return False

    def disconnect_incoming_movie(self):
        # Handle Incoming Deconstruction
        return False


    """ Hacky Solutions Below This Point """

    def force_redraw(self, sender):
        # With fixed for overlay order of show() matters
        # This method may not be necessary with GSTStreamer 1.0 and was formerly marked as "FIXME:"
        self.toggle_incoming_visibility()
        self.toggle_incoming_visibility()
        self.toggle_preview_visibility()
        self.toggle_preview_visibility()
