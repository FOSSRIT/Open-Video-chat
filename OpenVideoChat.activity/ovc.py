from gettext import gettext as _

from sugar.activity.activity import Activity, ActivityToolbox
import gtk
import gst
import gobject

from sugar.graphics.alert import NotifyAlert, Alert

from gui import Gui
from sugar_network_stack import SugarNetworkStack

V_SOURCE = "v4l2src"
#V_SOURCE = "videotestsrc"

V_SIZE = "width=320,height=240"

#GST_PIPE = "v4l2src ! autovideosink"
#GST_PIPE = V_SOURCE  + " ! videoscale ! video/x-raw-yuv," + V_SIZE + " ! ffmpegcolorspace ! ximagesink force-aspect-ratio=true name=xsink"
GST_PIPE = V_SOURCE  + " ! ffmpegcolorspace ! ximagesink force-aspect-ratio=true name=xsink"

class OpenVideoChatActivity(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)
        gobject.threads_init()

        # Set if they started the activity
        self.isServer = not self._shared_activity

        # INITIALIZE GUI
        ################
        self.set_title('OpenVideoChat')

        # Setup Network Stack
        #####################
        self.netstack = SugarNetworkStack(self)
        self._sh_hnd = self.connect('shared', self.netstack.shared_cb)
        self._jo_hnd = self.connect('joined', self.netstack.joined_cb)

        # Setup Gui
        ###########
        self.gui = Gui(self)
        self.gui.show()
        self.set_canvas(self.gui)

        # Setup Pipeline
        #################
        self.setup_gst_pipeline()
        gobject.idle_add( self.start_stop, True )
        #self.start_stop( True )


    def can_close( self ):
        self.start_stop(False)
        return True

    def setup_gst_pipeline(self):
        # Set up the gstreamer pipeline
        self.player = gst.parse_launch ( GST_PIPE )

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)


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

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_xwindow_id(self.gui.movie_window.window.xid)


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
            self._alert( "Message From %s" % str(sender), message  )
            self.gui.add_chat_text( message )

        elif src == "join":
            self._alert( "Net Join from %s" % str(args) )

    def send_chat_text(self, text):
        handle = self.netstack.get_tube_handle()
        if handle:
            handle.send_chat_text( text )
