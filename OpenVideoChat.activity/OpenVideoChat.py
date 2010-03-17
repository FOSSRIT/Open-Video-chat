from gettext import gettext as _

from sugar.activity.activity import Activity, ActivityToolbox
import gtk
import gst

from sugar.graphics.alert import NotifyAlert, Alert

V_SOURCE = "v4l2src"
#V_SOURCE = "videotestsrc"

V_SIZE = "width=320,height=240"

#GST_PIPE = "v4l2src ! autovideosink"
GST_PIPE = V_SOURCE  + " ! videoscale ! video/x-raw-yuv," + V_SIZE + " ! autovideosink"

class OpenVideoChatActivity(Activity):
    def __init__(self, handle):
        Activity.__init__(self, handle)

        # Set if they started the activity
        self.isServer = not self._shared_activity


        # INITIALIZE GUI
        ################
        self.set_title('OpenVideoChat')

        # Build Toolbars
        ################
        self.toolbox = ActivityToolbox(self)
        self.toolbox.show()
        self.set_toolbox(self.toolbox)


        vbox = gtk.VBox()

        self.movie_window = gtk.DrawingArea()
        vbox.add(self.movie_window)

        hbox = gtk.HBox()
        vbox.pack_start(hbox, False)
        hbox.set_border_width(10)
        hbox.pack_start(gtk.Label())
        self.button = gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        hbox.pack_start(self.button, False)
        hbox.add(gtk.Label())

        # Connect to shared and join calls
        self._sh_hnd = self.connect('shared', self._shared_cb)
        self._jo_hnd = self.connect('joined', self._joined_cb)

        self.setup_gst_pipeline()

        self.set_canvas(vbox)
        self.show_all()

    def setup_gst_pipeline(self):
        # Set up the gstreamer pipeline
        self.player = gst.parse_launch ( GST_PIPE )

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)


    def start_stop(self, w):
        if self.button.get_label() == "Start":
            self.button.set_label("Stop")
            self.player.set_state(gst.STATE_PLAYING)
        else:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.movie_window.window.xid)


    def _alert(self, title, text=None, timeout=5):
        alert = NotifyAlert(timeout=timeout)
        alert.props.title = title
        alert.props.msg = text
        self.add_alert(alert)
        alert.connect('response', self._alert_cancel_cb)
        alert.show()

    def _alert_cancel_cb(self, alert, response_id):
        self.activity.remove_alert(alert)

    def _shared_cb(self, activity):
        self._alert("Activity Shared", "The activity has been shared")

    def _joined_cb(self, activity):
        self._alert("Activity Joined", "Someone has joined the activity")
