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
        if self.connected:
            self.tube.add_signal_receiver(self.receive_chat_text_cb,
                'send_chat_text', IFACE, path=PATH, sender_keyword='sender')


    @signal(dbus_interface=IFACE, signature='s')
    def send_chat_text(self, text):
        self.text = text

    def receive_chat_text_cb(self, text, sender=None):
        # Ignore our own messages
        #if sender == self.tube.get_unique_name():
        #    return

        self.cb('chat', (text, sender) )
