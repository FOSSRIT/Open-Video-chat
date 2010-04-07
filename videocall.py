import gobject, dbus.glib

import telepathy
from telepathy.interfaces import (
    CONNECTION,
    CONNECTION_MANAGER,
    CONNECTION_INTERFACE_CAPABILITIES,
    CHANNEL_TYPE_STREAMED_MEDIA,
    CONNECTION_INTERFACE_REQUESTS,
    CHANNEL_INTERFACE_GROUP,
)
from telepathy.constants import (
    CONNECTION_STATUS_CONNECTED,
    HANDLE_TYPE_CONTACT,
    MEDIA_STREAM_TYPE_AUDIO,
    MEDIA_STREAM_TYPE_VIDEO,
)

from TfListener import TfListener

class VideoCall:
    def __init__(self, master, account_info, contact):
        self.master = master
        self.contact = contact
        ##
        ## Telepathy
        ##
        # Get the requested manager
        reg = telepathy.client.ManagerRegistry()
        reg.LoadManagers()    
        manager = reg.GetManager("gabble")

        # Request connection
        conn_bus_name, conn_object_path = manager[CONNECTION_MANAGER].RequestConnection("jabber", account_info)             
        self.conn = telepathy.client.Connection(conn_bus_name, conn_object_path)

        # Listen signals
        self.conn[CONNECTION].connect_to_signal("NewChannel", self.on_new_channel_user)
        self.conn[CONNECTION].connect_to_signal("StatusChanged", self.on_status_changed_user)

        # Connect
        self.conn[CONNECTION].Connect()

    
    def on_status_changed_user(self, state, reason):
        """
        When a user status changed
        """

        if state == CONNECTION_STATUS_CONNECTED:
            print "Connected"
            gobject.timeout_add(2000, self.enable_capabilities)
            if self.master:
                gobject.timeout_add(5000, self.create_telepathy_channel)
            else:
                print "Waiting streams..."

    def enable_capabilities(self):
        """
        Enable CHANNEL_TYPE_STREAMED_MEDIA capabilities
        """
        print "Advertizing Capabilities"
        self.conn[CONNECTION_INTERFACE_CAPABILITIES].AdvertiseCapabilities(
                                [(CHANNEL_TYPE_STREAMED_MEDIA, 15)], [])
    
    
    def create_telepathy_channel(self):
        """
        Request the handle for SLAVE and create a telepathy channel between contacts
        """
        print "Creating channel"
        
        # Request contact handle
        contact_handle = self.conn[CONNECTION].RequestHandles(HANDLE_TYPE_CONTACT, [self.contact])[0]    
        # Create CHANNEL_TYPE_STREAMED_MEDIA with handle
        self.conn[CONNECTION_INTERFACE_REQUESTS].CreateChannel({
                "org.freedesktop.Telepathy.Channel.ChannelType": CHANNEL_TYPE_STREAMED_MEDIA,
                "org.freedesktop.Telepathy.Channel.TargetHandleType": HANDLE_TYPE_CONTACT,
                "org.freedesktop.Telepathy.Channel.TargetHandle": contact_handle})
    
    def on_new_channel_user(self, object_path, channel_type, handle_type, handle, suppress_handler):
        """
        When the channel CHANNEL_TYPE_STREAMED_MEDIA is created and ready
        (received by each contacts), we create an TfListener. But only the MASTER
        offer a stream on it for SLAVE. SLAVE look if some streams already exists
        on the telepathy channel and in this case, we accept the stream.
        """
        
        if channel_type == CHANNEL_TYPE_STREAMED_MEDIA:
            print "New %s channel" % (channel_type)
            
            # Get telepathy channel
            channel = telepathy.client.channel.Channel(self.conn.service_name, object_path, self.conn.bus)

            # Create a tf listener
            TfListener(self.conn, object_path)
            print "MAKE TF LISTENER NOW"
            if self.master:    # Request a stream
                # Get contact handle
                contact_handle = self.conn[CONNECTION].RequestHandles( HANDLE_TYPE_CONTACT, [self.contact] )[0]
                # Request stream
                channel[CHANNEL_TYPE_STREAMED_MEDIA].RequestStreams(
                                                    contact_handle,
                                                    [MEDIA_STREAM_TYPE_VIDEO, MEDIA_STREAM_TYPE_AUDIO])
            else:
                # Regarding if streams are already in, and accepted them
                if channel[CHANNEL_TYPE_STREAMED_MEDIA].ListStreams() != []:
                    # Accept the stream by adding  owner
                    channel[CHANNEL_INTERFACE_GROUP].AddMembers( [self.conn[CONNECTION].GetSelfHandle()], "")


##################################################
MASTER_ACCOUNT = "ovc_master@schoolserver.rit.edu"
MASTER_PASSWORD = "ovc_master"

SLAVE_ACCOUNT = "ovc_slave@schoolserver.rit.edu"
SLAVE_PASSWORD = "ovc_slave"
##################################################


if __name__ == '__main__':
    import sys
    mode = sys.argv[1]    
    print "=== %s ===" % sys.argv[0]
    print "Mode: %s" % mode
    
    # Enable parameters due to mode
    if mode == "master":
        master = True
        parameters = {"account": MASTER_ACCOUNT, "password": MASTER_PASSWORD,
                      "port": dbus.UInt32(5222), "server": MASTER_ACCOUNT.split("@")[-1]}
        contact = SLAVE_ACCOUNT
    else:
        master = False
        parameters = {"account": SLAVE_ACCOUNT, "password": SLAVE_PASSWORD,
                      "port": dbus.UInt32(5222), "server": SLAVE_ACCOUNT.split("@")[-1]}
        contact = None
                      
    VideoCall(master, parameters, contact)
    loop = gobject.MainLoop()
    try:
        loop.run()
    except:
        pass
