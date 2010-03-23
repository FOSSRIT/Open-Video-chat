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

            self.connected = True
            self.announce_join()

    @signal(dbus_interface=IFACE, signature='')
    def announce_join(self):
        pass

    @signal(dbus_interface=IFACE, signature='s')
    def send_chat_text(self, text):
        self.text = text

    def announce_join_cb(self, sender=None):
        self.cb('join', sender)

    def receive_chat_text_cb(self, text, sender=None):
        # Ignore our own messages
        #if sender == self.tube.get_unique_name():
        #    return

        self.cb('chat', (text, sender) )
