from gettext import gettext as _

from sugar.activity.activity import Activity, ActivityToolbox
import gtk
import gst
import gobject

from sugar.graphics.alert import NotifyAlert, Alert

from gui import Gui
from sugar_network_stack import SugarNetworkStack
from sugar import profile

GST_INPIPE = "udpsrc ! theoradec ! ffmpegcolorspace ! xvimagesink force-aspect-ratio=true"
GST_OUTPIPE_BASE = "v4l2src ! videorate ! video/x-raw-yuv,width=320,height=240,framerate=15/1 ! tee name=t ! theoraenc bitrate=50 speed-level=2 ! udpsink host=%s t. ! queue ! ffmpegcolorspace ! ximagesink"

class OpenVideoChatActivity(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)
        gobject.threads_init()

        # Set if they started the activity
        self.isServer = not self._shared_activity

        # INITIALIZE GUI
        ################
        self.set_title('OpenVideoChat')

        # Setup Gui
        ###########
        self.gui = Gui(self)
        self.gui.show()
        self.set_canvas(self.gui)

        # Setup Network Stack
        #####################
        self.netstack = SugarNetworkStack(self)
        self._sh_hnd = self.connect('shared', self.netstack.shared_cb)
        self._jo_hnd = self.connect('joined', self.netstack.joined_cb)

        # Setup Pipeline
        #################
        self.setup_gst_pipeline()
        gobject.idle_add( self.start_stop, True )
        #self.start_stop( True )

        self.gui.add_chat_text( _("Activity Started") )

    def can_close( self ):
        self.start_stop(False)
        return True

    def setup_gst_pipeline(self):
        # Set up the gstreamer pipeline
        self.gui.add_chat_text( _("Starting Listen Video Pipeline") )
        self.player = gst.parse_launch ( GST_INPIPE )

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def setup_outgoing_pipeline(self, ip):
        self.gui.add_chat_text( "Pipeline UDP to %s" % ip )
        self.out = gst.parse_launch ( GST_OUTPIPE_BASE % ip )

        bus = self.out.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message_prev)
        bus.connect("sync-message::element", self.on_sync_prev_message)
        
        # FIXME
        gobject.timeout_add(5000, self.start_outgoing_pipeline)

    def start_outgoing_pipeline(self):
        self.gui.add_chat_text( _("Starting Video Pipeline") )
        self.out.set_state(gst.STATE_PLAYING)
        return False


    def start_stop(self, start=True):
        if start:
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)

    def on_message_prev(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.out.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.out.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_xwindow_id(self.gui.movie_window.window.xid)

    def on_sync_prev_message(self, bus, message ):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_xwindow_id(self.gui.movie_window_preview.window.xid)


    def _alert(self, title, text=None, timeout=5):
        alert = NotifyAlert(timeout=timeout)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()

    def _alert_cancel_cb(self, alert, response_id):
        self.remove_alert(alert)

    def net_cb(self, src, args):
        """
        Callback for network commands
        """
        if src == "chat":
            message, sender = args
            self.gui.add_chat_text( message )

        elif src == "join":
            handle = self.netstack.get_tube_handle()
            if handle:
                import socket
                import fcntl
                import struct
                import array
                # http://code.activestate.com/recipes/439094-get-the-ip-address-associated-with-a-network-inter/
                def get_ip_address(ifname):
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    return socket.inet_ntoa(fcntl.ioctl(
                        s.fileno(),
                        0x8915,  # SIOCGIFADDR
                        struct.pack('256s', ifname[:15])
                    )[20:24])

                #http://code.activestate.com/recipes/439093-get-names-of-all-up-network-interfaces-linux-only/
                def all_interfaces():
                    max_possible = 128  # arbitrary. raise if needed.
                    bytes = max_possible * 32
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    names = array.array('B', '\0' * bytes)
                    outbytes = struct.unpack('iL', fcntl.ioctl(
                        s.fileno(),
                        0x8912,  # SIOCGIFCONF
                        struct.pack('iL', bytes, names.buffer_info()[0])
                    ))[0]
                    namestr = names.tostring()
                    return [namestr[i:i+32].split('\0', 1)[0] for i in range(0, outbytes, 32)]


                for interface in all_interfaces():
                    if interface != 'lo':
                        try:
                            ip = get_ip_address(interface)
                            handle.announce_ip(ip)
                            break
                        except:
                            print "Interface %s did not give ip" % interface
                else:
                    print "Could not find ip address"
                    
        elif src == "ip":
            self.setup_outgoing_pipeline( args )

        elif src == "buddy_add":
            self.gui.add_chat_text(_("%s has joined the chat") % args)

        elif src == "buddy_rem":
            self.gui.add_chat_text(_("%s has left the chat") % args)

    def send_chat_text(self, text):
        handle = self.netstack.get_tube_handle()
        prof = profile.get_nick_name()

        if handle:
            handle.send_chat_text( "<%s> %s" % (prof, text) )
            
    #
    # Save Chat Log
    #
    
    def write_file(self, file_path):
        file = open(file_path, 'w')
        file.write( self.gui.get_history() )
        file.close()
        
    #
    # Load Chat Log
    #
    
    def read_file(self, file_path):
        file = open(file_path, 'r')
        
        self.gui.add_chat_text(file.read())
            
        file.close()
