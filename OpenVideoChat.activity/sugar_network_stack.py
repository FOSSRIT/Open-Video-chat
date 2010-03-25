import telepathy
from sugar.presence.tubeconn import TubeConnection
from sugar.presence import presenceservice
from tube_speak import TubeSpeak

SERVICE = "org.laptop.OpenVideoChat"
IFACE = SERVICE
PATH = "/org/laptop/OpenVideoChat"

class SugarNetworkStack:
    def __init__(self, activity):
        self.__activity = activity
        self.controlTube = None

    def add_buddy(self, buddy):
        """
        Passes buddy nick to ovc
        """
        if buddy == presenceservice.get_instance().get_owner():
            return
        if buddy:
            nick = buddy.props.nick
        else:
            nick = '???'
        self.__activity.net_cb('buddy_add', nick)

    def rem_buddy(self, buddy):
        """
        Passes buddy nick to ovc
        """
        if buddy:
            nick = buddy.props.nick
        else:
            nick = '???'
        self.__activity.net_cb('buddy_rem', nick)

    def _buddy_joined_cb(self, activity, buddy):
        """Called when a buddy joins the shared activity."""
        self.add_buddy( buddy )

    def _buddy_left_cb(self, activity, buddy):
        """Called when a buddy leaves the shared activity."""
        self.rem_buddy(buddy)

    def joined_cb(self, activity):
        """
        Called when joining an existing activity
        """
        for buddy in self.__activity.shared_activity.get_joined_buddies():
            self.add_buddy(buddy)

        self.watch_for_tubes()

    def shared_cb(self, activity):
        """
        Called when setting an activity to be shared
        """
        self.watch_for_tubes()

        # Offer DBus Tube
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube( SERVICE, {})

    def watch_for_tubes(self):
        """
        This method sets up the listeners for new tube connections
        """

        self.conn = self.__activity._shared_activity.telepathy_conn
        self.tubes_chan = self.__activity._shared_activity.telepathy_tubes_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube',
            self._new_tube_cb)

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)

        # Register budy join/leave
        self.__activity._shared_activity.connect('buddy-joined', self._buddy_joined_cb)
        self.__activity._shared_activity.connect('buddy-left', self._buddy_left_cb)

    def _list_tubes_reply_cb(self, tubes):
        """
        Loops through tube list and passes it to _new_tube_cb
        """
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        self.__activity._alert('ListTubes() failed: %s' % e)

    def _new_tube_cb(self, id, initiator, type, service, params, state):

        if (type == telepathy.TUBE_TYPE_DBUS and service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

            # Create Tube Connection
            tube_conn = TubeConnection(self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES], id,
                group_iface=self.tubes_chan[telepathy.CHANNEL_INTERFACE_GROUP])

            self.controlTube = TubeSpeak(tube_conn, self.__activity.net_cb)

        #elif (type == telepathy.TUBE_TYPE_STREAM and service == DIST_STREAM_SERVICE):
        #        # Data tube, store for later
        #        _logger.debug("New data tube added")
        #        self.unused_download_tubes.add(id)

    def get_tube_handle(self):
        if self.controlTube:
            return self.controlTube
