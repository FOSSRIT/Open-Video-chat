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
:mod: `OpenVideoChat.activity/sugar_toolbar` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""

# External Imports
import logging
from gi.repository import Gtk
from gi.repository import Gdk
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton

# from sugar3.graphics.toolbutton import ToolButton
# from sugar3.graphics.toolbarbox import ToolbarBox
# from sugar3.activity.widgets import ActivityButton
# from sugar3.graphics.toolbarbox import ToolbarButton


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants
ICONS = {
    'play': 'icons/media-playback-start-insensitive.svg',
    'stop': 'icons/media-playback-stop-insensitive.svg',
    'unmute': 'icons/speaker-100.svg',
    'mute': 'icons/speaker-000.svg'
}


class Toolbar(Gtk.Toolbar):
    def __init__(self, activity):
        Gtk.Toolbar.__init__(self)
        logger.debug("Preparing Toolbar")

        # Reference to Activity
        self.activity = activity

        # Set Background
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .8))

        # Define Buttons
        self.build_buttons()

        # Build Menu
        self.build_toolbar()

        # Display
        self.show_all()
        logger.debug("Toolbar Prepared")

    def build_buttons(self):

        # Create Toggles
        logger.debug("Defining Toolbar Buttons")
        self.toggles = {
            'outgoing-video': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Video", icon_widget=Gtk.Image(file=ICONS['stop'])),
            'outgoing-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Audio", icon_widget=Gtk.Image(file=ICONS['mute'])),
            'incoming-video': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Video", icon_widget=Gtk.Image(file=ICONS['stop'])),
            'incoming-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Audio", icon_widget=Gtk.Image(file=ICONS['mute']))
        }
        logger.debug("Defined Toolbar Buttons")

        # Define Signal Events

    def build_toolbar(self):

        # Create Toolbar
        # logger.debug("Building Toolbar")
        # toolbar = Gtk.Toolbar()

        # Add Buttons to Toolbar
        # logger.debug("Adding Buttons")
        # toolbar.insert(self.toggles['outgoing-video'], 0)
        # toolbar.insert(self.toggles['outgoing-audio'], 1)
        # toolbar.insert(self.toggles['incoming-video'], 2)
        # toolbar.insert(self.toggles['incoming-audio'], 3)
        # logger.debug("Buttons Added")

        # Activity Specific Buttons
        self.insert(ShareButton(self.activity), -1)
        self.insert(StopButton(self.activity), -1)

        # Return Toolbar
        # logger.debug("Built Toolbar")
        # return toolbar

    # def build_toolbar(self, activity):
    #     # Prepare Primary Toolbar Container
    #     toolbar_box = ToolbarBox();

    #     # Create activity button
    #     toolbar_box.toolbar.insert(ActivityButton(activity), -1)

    #     # Video Toggle
    #     video_toggle_button = ToolButton()
    #     video_toggle_button.connect("clicked", self.toggle_video)
    #     toolbar_box.toolbar.insert(video_toggle_button, 1)
    #     self.toggle_video(video_toggle_button)

    #     # Audio Toggle
    #     audio_toggle_button = ToolButton()
    #     audio_toggle_button.connect("clicked", self.toggle_audio)
    #     toolbar_box.toolbar.insert(audio_toggle_button, 2)
    #     self.toggle_audio(audio_toggle_button)

    #     # Toggle Preview Display Button
    #     preview_toggle_button = ToolButton()
    #     preview_toggle_button.connect("clicked", self.toolbar_toggle_preview_visibility)
    #     toolbar_box.toolbar.insert(preview_toggle_button, 3)
    #     self.toolbar_toggle_preview_visibility(preview_toggle_button)

    #     # Forced Refresh
    #     reload_video = ToolButton("view-refresh")
    #     reload_video.set_tooltip_text(_("Reload Video"))
    #     reload_video.connect("clicked", self.force_redraw)
    #     toolbar_box.toolbar.insert(reload_video, -1)

    #     # Push stop button to far right
    #     separator = Gtk.SeparatorToolItem()
    #     separator.props.draw = False
    #     separator.set_expand(True)
    #     toolbar_box.toolbar.insert(separator, -1)

    #     # Create Share Button
    #     toolbar_box.toolbar.insert(ShareButton(activity), -1)

    #     # Create stop button
    #     toolbar_box.toolbar.insert(StopButton(activity), -1)

    #     # Add reference to toolbar items
    #     self.toolbar = toolbar_box.toolbar

    #     # Display all components & Return
    #     toolbar_box.show_all()
    #     return toolbar_box
