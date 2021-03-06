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
    'play': 'icons/ovc_start.svg',
    'stop': 'icons/ovc_stop.svg',
    'unmute': 'icons/ovc_unmute.svg',
    'mute': 'icons/ovc_mute.svg',
    'onwebcam': 'icons/ovc_webcam_on.svg',
    'offwebcam': 'icons/ovc_webcam_off.svg',
    'onmic': 'icons/ovc_mic_on.svg',
    'offmic': 'icons/ovc_mic_off.svg',
    'accounts': 'icons/ovc_account_manager.svg'
}


class Toolbar(Gtk.Expander):
    def __init__(self, swap_gui_method):
        Gtk.Expander.__init__(self, expanded=True, label=_('Toolbar'))
        logger.debug("Preparing Toolbar...")

        # Define Buttons
        self.build_buttons(swap_gui_method)

        # Build Menu
        self.add(self.build_toolbar())

        # Display
        self.show_all()
        logger.info("Toolbar Prepared")

    def build_buttons(self, swap_gui_method):

        # Create Toggles
        logger.debug("Defining Toolbar Buttons...")
        self.toggles = {
            'outgoing-video': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Video", icon_widget=Gtk.Image(file=ICONS['onwebcam'])),
            'outgoing-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Outgoing Audio", icon_widget=Gtk.Image(file=ICONS['onmic'])),
            'incoming-video': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Video", icon_widget=Gtk.Image(file=ICONS['play'])),
            'incoming-audio': Gtk.ToolButton(sensitive=False, tooltip_text="Incoming Audio", icon_widget=Gtk.Image(file=ICONS['unmute'])),
            'manage-accounts': Gtk.ToolButton(tooltip_text="Manage Jabber Accounts", icon_widget=Gtk.Image(file=ICONS['accounts']))
        }
        logger.debug("Defined Toolbar Buttons")

        # Define Signal Events
        self.toggles['manage-accounts'].connect('clicked', swap_gui_method)

    def build_toolbar(self):

        # Create Toolbar
        logger.debug("Building Toolbar...")
        toolbar = Gtk.Toolbar()

        # Add Buttons to Toolbar
        logger.debug("Adding Buttons...")
        toolbar.insert(Gtk.SeparatorToolItem(draw=False), 0)
        toolbar.insert(self.toggles['outgoing-video'], 1)
        toolbar.insert(self.toggles['outgoing-audio'], 2)
        toolbar.insert(Gtk.SeparatorToolItem(draw=True), 3)
        toolbar.insert(self.toggles['incoming-video'], 4)
        toolbar.insert(self.toggles['incoming-audio'], 5)
        spacer = Gtk.SeparatorToolItem(draw=False)
        spacer.set_expand(True)
        toolbar.insert(spacer, 6)
        toolbar.insert(self.toggles['manage-accounts'], 7)
        toolbar.insert(Gtk.SeparatorToolItem(draw=False), 8)
        logger.debug("Buttons Added")

        # Override Background Color
        toolbar.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .8))

        # Return Toolbar
        logger.debug("Built Toolbar")
        return toolbar
