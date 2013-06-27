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
from toolbar import Toolbar


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Constants
DEFAULT_WINDOW_SIZE = {
    'width': 800,
    'height': 600
}


# OpenVideoChat Cross Platform extends [GtkWindow](https://developer.gnome.org/gtk3/3.0/GtkWindow.html)
class OpenVideoChatActivity(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Open Video Chat")

        # Assume a default size of 800x600
        self.set_default_size(DEFAULT_WINDOW_SIZE['width'], DEFAULT_WINDOW_SIZE['height'])

        # Connect Window Event Signals
        self.connect("delete-event", Gtk.main_quit)
        self.connect('check-resize', self.on_resize)

        """ Setup GUI """
        logger.debug("Preparing GUI")
        # Gui extends [GtkGrid](https://developer.gnome.org/gtk3/3.0/GtkGrid.html)
        self.add(Gui())
        # Toolbar extends [GtkExpander](https://developer.gnome.org/gtk3/3.0/GtkExpander.html)
        self.get_child().attach(Toolbar(), 0, 0, 1, 1)
        logger.debug("Finished Preparing GUI")

        # Display & Begin Main Loop
        self.show()
        Gtk.main()

    def on_resize(self, trigger):
        # On resize adjust displayed components (may not be needed)
        return False
