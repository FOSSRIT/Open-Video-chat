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
:mod: `OpenVideoChat.activity/dialog` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""

# Imports
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gettext import gettext as _


class Dialog(Gtk.EventBox):
    """
        Cross Platform Dialog used for confirmation
        Sugar implementation of "alert" was not portable, so we needed a modified version.
    """

    __gtype_name__ = 'OVCDialog'

    __gsignals__ = {
        'response': (GObject.SignalFlags.RUN_FIRST, None, ([object])),
    }

    # Define Properties
    title = GObject.property(type=str, default=None)
    message = GObject.property(type=str, default=None)

    def __init__(self, **kwargs):
        Gtk.EventBox.__init__(self, **kwargs)

        # Set Max Size?
        # self.set_size_request(-1, 50)

        # Background Color
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.1, .1, .1, .75))

        # Dynamic Properties (Will these break?)
        self.buttons = {}

        # Containment
        self.title_label = Gtk.Label(hexpand=True, xalign=0, xpad=5, ypad=2)
        self.title_label.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1, 1, .9))
        self.message_label = Gtk.Label(hexpand=True, xalign=0, xpad=15, ypad=5)
        self.message_label.override_color(Gtk.StateType.NORMAL, Gdk.RGBA(1, 1, 1, .9))
        self.layout = Gtk.Grid()
        self.layout.attach(self.title_label, 0, 0, 1, 1)
        self.layout.attach(self.message_label, 0, 1, 1, 1)
        self.add(self.layout)

        # First-Time Application of Values
        self.apply_title(None, None)
        self.apply_message(None, None)

        # Add Buttons
        self.buttons[Gtk.ResponseType.OK] = Gtk.Button(label=_("Ok"))
        self.buttons[Gtk.ResponseType.OK].connect('clicked', self.button_clicked, Gtk.ResponseType.OK)
        self.buttons[Gtk.ResponseType.CANCEL] = Gtk.Button(label=_("Cancel"))
        self.buttons[Gtk.ResponseType.CANCEL].connect('clicked', self.button_clicked, Gtk.ResponseType.CANCEL)
        self.layout.attach(self.buttons[Gtk.ResponseType.OK], 1, 0, 1, 1)
        self.layout.attach(self.buttons[Gtk.ResponseType.CANCEL], 1, 1, 1, 1)

        # Change UI on update
        self.connect('notify::title', self.apply_title)
        self.connect('notify::message', self.apply_message)

        # Render
        self.show_all()

    def apply_title(self, sender, data):
        self.title_label.set_markup('<b>' + (self.title or '') + '</b>')

    def apply_message(self, sender, data):
        self.message_label.set_markup(self.message or '')

    def button_clicked(self, button, response_id):
        self.emit('response', response_id)
