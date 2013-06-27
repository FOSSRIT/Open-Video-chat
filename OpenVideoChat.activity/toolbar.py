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
:mod: `OpenVideoChat.activity/toolbar` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# External Imports
import logging
from gi.repository import Gtk
from gi.repository import Gdk
from gettext import gettext as _


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


class Toolbar(Gtk.Expander):
    def __init__(self):
        Gtk.Expander.__init__(self, expanded=True, label=_('Toolbar'))
        logger.debug("Preparing Toolbar")

        # Define Buttons
        self.build_buttons()

        # Build Menu
        self.add(self.build_toolbar())

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
        logger.debug("Building Toolbar")
        toolbar = Gtk.Toolbar()

        # Add Buttons to Toolbar
        logger.debug("Adding Buttons")
        toolbar.insert(self.toggles['outgoing-video'], 0)
        toolbar.insert(self.toggles['outgoing-audio'], 1)
        toolbar.insert(self.toggles['incoming-video'], 2)
        toolbar.insert(self.toggles['incoming-audio'], 3)
        logger.debug("Buttons Added")

        # Override Background Color
        toolbar.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .8))

        # Return Toolbar
        logger.debug("Built Toolbar")
        return toolbar
