from dbus.service import method, signal
from dbus.gobject_service import ExportedGObject

SERVICE = "org.laptop.OpenVideoChat"
IFACE = SERVICE
PATH = "/org/laptop/OpenVideoChat"

# http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
def get_ip_address(ifname):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

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
            self.announce_join(get_ip_address('eth0'))

    @signal(dbus_interface=IFACE, signature='')
    def announce_join(self, ip):
        self.ip = ip

    @signal(dbus_interface=IFACE, signature='s')
    def send_chat_text(self, text):
        self.text = text

    def announce_join_cb(self, ip, sender=None):
        self.cb('join', ip)

    def receive_chat_text_cb(self, text, sender=None):
        # Ignore our own messages
        #if sender == self.tube.get_unique_name():
        #    return

        self.cb('chat', (text, sender) )
