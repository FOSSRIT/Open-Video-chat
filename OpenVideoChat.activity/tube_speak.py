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
:mod: `OpenVideoChat/OpenVideoChat.activity/tube_speak` -- Open Video Chat TubeSpeak
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthro:: Remy DeCausemaker <remyd@civx.us>
"""

from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

SERVICE = "org.laptop.OpenVideoChat"
IFACE = SERVICE
PATH = "/org/laptop/OpenVideoChat"

class TubeSpeak(ExportedGObject):
    def __init__(self, tube, cb):
        super(TubeSpeak, self).__init__(tube, PATH)

        self.connected = False
        self.cb = cb
        self.tube = tube
        self.tube.watch_participants(self.participant_change_cb)

    def participant_change_cb(self, added, removed):
        if not self.connected:
            self.tube.add_signal_receiver(self.receive_chat_text_cb,
                'send_chat_text', IFACE, path=PATH, sender_keyword='sender')

            self.tube.add_signal_receiver(self.announce_join_cb, 'announce_join', IFACE,
                path=PATH, sender_keyword='sender')

            self.tube.add_signal_receiver(self.announce_ip_cb, 'announce_ip', IFACE,
                path=PATH, sender_keyword='sender')

            self.connected = True
            self.announce_join()

    @signal(dbus_interface=IFACE, signature='')
    def announce_join(self):
        pass

    @signal(dbus_interface=IFACE, signature='s')
    def announce_ip(self, ip):
        self.ip = ip

    @signal(dbus_interface=IFACE, signature='s')
    def send_chat_text(self, text):
        self.text = text

    def announce_join_cb(self, sender=None):
        self.cb('join', None)

    def announce_ip_cb(self, ip, sender=None):
        if sender != self.tube.get_unique_name():
            self.cb('ip', ip)

    def receive_chat_text_cb(self, text, sender=None):
        # Ignore our own messages
        #if sender == self.tube.get_unique_name():
        #    return

        self.cb('chat', (text, sender) )
