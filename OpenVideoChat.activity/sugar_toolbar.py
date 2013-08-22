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
from sugar3.activity.widgets import ActivityButton


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants
ICONS = {
    'play': 'icons/ovc_start_sugar.svg',
    'stop': 'icons/ovc_stop_sugar.svg',
    'unmute': 'icons/ovc_unmute_sugar.svg',
    'mute': 'icons/ovc_mute_sugar.svg',
    'onwebcam': 'icons/ovc_webcam_on_sugar.svg',
    'offwebcam': 'icons/ovc_webcam_off_sugar.svg',
    'onmic': 'icons/ovc_mic_on_sugar.svg',
    'offmic': 'icons/ovc_mic_off_sugar.svg'
}


class Toolbar(Gtk.Toolbar):
    def __init__(self, activity):
        Gtk.Toolbar.__init__(self)
        logger.debug("Preparing Toolbar...")

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
        logger.debug("Defining Toolbar Buttons...")
        self.toggles = {
            'outgoing-video': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Video", icon_widget=Gtk.Image(file=ICONS['onwebcam'])),
            'outgoing-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Audio", icon_widget=Gtk.Image(file=ICONS['onmic'])),
            'incoming-video': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Video", icon_widget=Gtk.Image(file=ICONS['play'])),
            'incoming-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Audio", icon_widget=Gtk.Image(file=ICONS['unmute']))
        }
        logger.debug("Defined Toolbar Buttons")

        # Define Signal Events

    def build_toolbar(self):

        # Apparently set_expand is not the same as expand=True in properties
        # So we need to prepare this to space out the middle
        spacer = Gtk.SeparatorToolItem(draw=False)
        spacer.set_expand(True)

        # Add Buttons to Self
        logger.debug("Building Toolbar...")
        self.insert(Gtk.SeparatorToolItem(draw=False), 0)
        self.insert(ActivityButton(self.activity), 1)
        self.insert(self.toggles['outgoing-video'], 2)
        self.insert(self.toggles['outgoing-audio'], 3)
        self.insert(Gtk.SeparatorToolItem(draw=True), 4)
        self.insert(self.toggles['incoming-video'], 5)
        self.insert(self.toggles['incoming-audio'], 6)
        self.insert(spacer, 7)
        self.insert(ShareButton(self.activity), 8)
        self.insert(StopButton(self.activity), 9)
        self.insert(Gtk.SeparatorToolItem(draw=False), 10)
        logger.debug("Built Toolbar")
