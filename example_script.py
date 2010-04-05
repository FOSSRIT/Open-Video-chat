"""
Example to create a videoconferencing application using Farsight throught
Telepathy

@author: Fabien LOUIS, flouis@viotech.net
@date: December 2009

Copyright (C) 2009 Viotech Communications

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.

@Usage:
Just run two clients, one with "slave" parameter and seconds with "master"
parameter (master account initiate the call or slave accept the call).

@Scenario:
We start by connect each accounts (first the slave and then the master).
    (see function on_status_changed_user)
When accounts are connected, we enable CHANNEL_TYPE_STREAMED_MEDIA capabilities
    (see function function enable_capabilities)
on it and MASTER create a telepathy account.
    (see function function create_telepathy_channel)

When the channel CHANNEL_TYPE_STREAMED_MEDIA is created and ready
(received by each contacts), we create an TfListener. But only the MASTER
offer a stream on it for SLAVE. SLAVE look if some streams already exists
on the telepathy channel and in this case, we accept the stream.

TfListener is a component which encapsulate farsight management (session
creation, stream creation, src pad adding, etc.).

We create a tfChannel linked with the telepathy channel path and connect it
with some farsight signals.

Once the stream is created and accepted, the farsight part started.
First, we get 'session-created' signal which call __on_session_created
    On signal "session-created", we create the pipeline and add conference
    on it. We set pipeline to PLAYING and we transfer all bus message to it.
    
Second, we get 'stream-get-codec-config' signal which call __on_stream_get_codec_config
    On signal "stream-get-codec-config", we returns our codec configuration

Third, we get 'stream-created' which call __on_stream_created
    On signal "stream-created", connect signals on stream and add source.
    Then we link the stream's sink-pad  to source's src-pad.

If all works (codec negotiation and other things), we get 'src-pad-added' which
call __on_src_pad_added.
    On signal "src-pad-added", we display stream's view
"""

##################################################
MASTER_ACCOUNT = "ovc_master@schoolserver.rit.edu"
MASTER_PASSWORD = "ovc_master"

SLAVE_ACCOUNT = "ovc_slave@schoolserver.rit.edu"
SLAVE_PASSWORD = "ovc_slave"
##################################################

import pygst
pygst.require('0.10')

import sys, os
import gobject, dbus.glib
import tpfarsight
import farsight, gst

os.environ["GST_PLUGIN_PATH"] = "/usr/local/lib/gstreamer-0.10"

#autovideosrc should choose v4l2src
VIDEO_SRC = "autovideosrc ! videoscale ! video/x-raw-yuv,width=320,height=240  ! ffmpegcolorspace "
VIDEO_SINK= "autovideosink"
AUDIO_SRC = "autoaudiosrc"
AUDIO_SINK= "autoaudiosink"


##
## Debugging
##
#os.environ["GST_DEBUG"] = "fsrtp*:5"
#os.environ["GST_DEBUG"] = "1,fs*:2,rtp*:1"
#os.environ["GST_DEBUG"] = "*PAD*:5,*bin*:5"

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

##################################################
def debug_callback(self, *args, **kwargs):
    """
    Debug function for unused signal    
    """
    
    print "debug_callback"
    # Print all kwarg
    for arg in args:
        print "\t[arg] %s" % str(arg)       
    # Print all kwarg
    for kwarg in kwargs:
        print "\t[kwarg]%s: %s" % (kwarg, kwargs[kwarg])
        
def on_status_changed_user(state, reason):
    """
    When a user status changed
    """

    if state == CONNECTION_STATUS_CONNECTED:
        print "Connected"
        gobject.timeout_add(2000, enable_capabilities)
        if mode == "master":
            print "Creating channel"
            gobject.timeout_add(5000, create_telepathy_channel)
        else:
            print "Waiting streams..."

def enable_capabilities():
    """
    Enable CHANNEL_TYPE_STREAMED_MEDIA capabilities
    """
    
    conn[CONNECTION_INTERFACE_CAPABILITIES].AdvertiseCapabilities(
                            [(CHANNEL_TYPE_STREAMED_MEDIA, 15)], [])

def create_telepathy_channel():
    """
    Request the handle for SLAVE and create a telepathy channel between contacts
    """
    
    # Request contact handle
    contact_handle = conn[CONNECTION].RequestHandles(HANDLE_TYPE_CONTACT,
                                                     [SLAVE_ACCOUNT])[0]    
    # Create CHANNEL_TYPE_STREAMED_MEDIA with handle
    conn[CONNECTION_INTERFACE_REQUESTS].CreateChannel({
                "org.freedesktop.Telepathy.Channel.ChannelType":
                    CHANNEL_TYPE_STREAMED_MEDIA,
                "org.freedesktop.Telepathy.Channel.TargetHandleType":
                    HANDLE_TYPE_CONTACT,
                "org.freedesktop.Telepathy.Channel.TargetHandle":
                    contact_handle})
            
def on_new_channel_user(object_path, channel_type, handle_type,
                         handle, suppress_handler):
    """
    When the channel CHANNEL_TYPE_STREAMED_MEDIA is created and ready
    (received by each contacts), we create an TfListener. But only the MASTER
    offer a stream on it for SLAVE. SLAVE look if some streams already exists
    on the telepathy channel and in this case, we accept the stream.
    """
    
    if channel_type == CHANNEL_TYPE_STREAMED_MEDIA:
        print "New %s channel" % (channel_type)
        
        # Get telepathy channel
        channel = telepathy.client.channel.Channel(conn.service_name,
                                                   object_path,
                                                   conn.bus)

        # Create a tf listener
        TfListener(conn, object_path)
        
        if mode == "master":    # Request a stream
            # Get contact handle
            contact_handle = conn[CONNECTION].RequestHandles(
                                                            HANDLE_TYPE_CONTACT,
                                                            [SLAVE_ACCOUNT])[0]
            # Request stream
            channel[CHANNEL_TYPE_STREAMED_MEDIA].RequestStreams(
                                                contact_handle,
                                                [MEDIA_STREAM_TYPE_VIDEO
                                                ,MEDIA_STREAM_TYPE_AUDIO
                                                ])
        else:
            # Regarding if streams are already in, and accepted them
            if channel[CHANNEL_TYPE_STREAMED_MEDIA].ListStreams() != []:
                # Accept the stream by adding  owner
                channel[CHANNEL_INTERFACE_GROUP].AddMembers(
                                        [conn[CONNECTION].GetSelfHandle()],
                                        "")

##################################################        
class TfListener(object):
    """
    TfListener is a component which encapsulate farsight management (session
    creation, stream creation, src pad adding, etc.).
    
    We create a tfChannel linked with the telepathy channel path and connect it
    with some farsight signals.
    """
    
    def __init__(self, connection, chan_object_path):
        """
        Init
        
        @param connection: current connection
        @type connection: Telepathy Connection
        
        @param chan_object_path: Object path of the StreamedMedia channel
        @type chan_object_path: String
        """
        
        super(TfListener, self).__init__()        
        self.pipeline = None
        self.conn = connection
        
        # We create a tfChannel linked with the telepathy channel path.
        self.tf_channel = tpfarsight.Channel(
                                     connection_busname=self.conn.service_name,
                                     connection_path=self.conn.object_path,
                                     channel_path=chan_object_path)
        # Connect to several signals
        print "connecting to channel", self.tf_channel
        self.tf_channel.connect('session-created', self.__on_session_created)
        self.tf_channel.connect('stream-created', self.__on_stream_created)
        self.tf_channel.connect('stream-get-codec-config',
                                self.__on_stream_get_codec_config)

    def __on_session_created(self, channel, conference, participant):
        """
        On signal "session-created", we create the pipeline and add conference
        on it. We set pipeline to PLAYING and we transfer all bus message to it.
        """
        
        print
        print "=== %s __on_session_created ===" % self
        print
       
        self.pipeline = gst.Pipeline()        
        self.pipeline.add(conference)
        self.pipeline.set_state(gst.STATE_PLAYING)
        
        # Transfer all bus message
        self.pipeline.get_bus().add_watch(self.__async_handler)

    def __on_stream_get_codec_config(self, channel, stream_id, media_type,
                                     direction):
        """
        On signal "stream-get-codec-config", we returns our codec configuration
        """
        
        print
        print "=== %s __on_stream_get_codec_config ===" % self
        print
        
        if media_type == farsight.MEDIA_TYPE_VIDEO:
            codecs = [farsight.Codec(farsight.CODEC_ID_ANY, "H264",
                                     farsight.MEDIA_TYPE_VIDEO, 0)]
            
            if self.conn.GetProtocol() == "sip" :
                codecs += [ farsight.Codec(farsight.CODEC_ID_DISABLE, "THEORA",
                                        farsight.MEDIA_TYPE_VIDEO, 0) ]
            else:
                codecs += [ farsight.Codec(farsight.CODEC_ID_ANY, "THEORA",
                                        farsight.MEDIA_TYPE_VIDEO, 0) ]
            
            codecs += [
                farsight.Codec(farsight.CODEC_ID_ANY, "H263",
                                        farsight.MEDIA_TYPE_VIDEO, 0),
                farsight.Codec(farsight.CODEC_ID_ANY, "JPEG",
                                        farsight.MEDIA_TYPE_VIDEO, 0),
                farsight.Codec(farsight.CODEC_ID_ANY, "MPV",
                                        farsight.MEDIA_TYPE_VIDEO, 0),
                farsight.Codec(farsight.CODEC_ID_DISABLE, "DV",
                                        farsight.MEDIA_TYPE_VIDEO, 0),
            ]

            return codecs
        else:
            return None

    def __on_stream_created(self, channel, stream):
        """
        On signal "stream-created">, connect signals on stream and add source.
        Then we link the stream's sink-pad  to source's src-pad.
        """
        
        print
        print "=== %s __on_stream_created ===" % self
        print
        
        stream.connect('src-pad-added', self.__on_src_pad_added)
        stream.connect('closed', debug_callback, "closed")          # Not used
        stream.connect('error', debug_callback, "error")            # Not used
        stream.connect('free-resource', debug_callback, "free")     # Not used
        
        # creating src pipes
        type = stream.get_property ("media-type")
        if type == farsight.MEDIA_TYPE_AUDIO:
            source = gst.parse_bin_from_description (AUDIO_SRC, True) 
        
        elif type == farsight.MEDIA_TYPE_VIDEO:
            if mode == "master":
				source = gst.parse_bin_from_description ( VIDEO_SRC, True)
    
        self.pipeline.add(source)        
        source.get_pad("src").link(stream.get_property("sink-pad"))        
        source.set_state(gst.STATE_PLAYING)
    
    def __on_src_pad_added (self, stream, pad, codec):
        """
        On signal "src-pad-added", we display stream view
        """
        
        print
        print "=== %s __src_pad_added ===" % self
        print
        
        type = stream.get_property ("media-type")
        if type == farsight.MEDIA_TYPE_AUDIO:
            queue_sink = gst.parse_bin_from_description( AUDIO_SINK, True)
            
            audioadder = gst.element_factory_make("liveadder")
            tee = gst.element_factory_make("tee")
            
            # Add & Link
            self.pipeline.add(audioadder, tee, queue_sink)
            gst.element_link_many(audioadder, tee, queue_sink)            
            pad.link(audioadder.get_pad("sink%d"))            
            
            queue_sink.set_state(gst.STATE_PLAYING)
            tee.set_state(gst.STATE_PLAYING)
            audioadder.set_state(gst.STATE_PLAYING)
                
        elif type == farsight.MEDIA_TYPE_VIDEO:
            queue_ff = gst.parse_bin_from_description("queue ! ffmpegcolorspace", True)

            if USE_CLUTTER_TO_DISPLAY:
                sink = cluttergst.VideoSink(video_texture)
            else:
                sink = gst.parse_bin_from_description( VIDEO_SINK, True)
            
            videofunnel = gst.element_factory_make("fsfunnel")
            tee = gst.element_factory_make("tee")
            
            # Add & Link
            self.pipeline.add(videofunnel, tee, queue_ff,  sink)
            gst.element_link_many(videofunnel, tee, queue_ff, sink)
            pad.link(videofunnel.get_pad("sink%d"))    
                        
            sink.set_state(gst.STATE_PLAYING)
            queue_ff.set_state(gst.STATE_PLAYING)
            tee.set_state(gst.STATE_PLAYING)
            videofunnel.set_state(gst.STATE_PLAYING)
            self.pipeline.set_state(gst.STATE_PLAYING)
           
    def __async_handler (self, bus, message):
        """
        Check all bus message and redirect them to tf_channel (obligatory)
        """
        
        if self.tf_channel != None:
            self.tf_channel.bus_message(message)
        return True
    
##################################################
##################################################
if __name__ == '__main__':
    # Manage parameters
    if len(sys.argv) < 2:
        print "Usage: %s {master|slave} [--enable clutter]" % sys.argv[0]
        exit(1)
    
    if len(sys.argv) == 4 and sys.argv[2] == "--enable" and sys.argv[3] == "clutter":               
        USE_CLUTTER_TO_DISPLAY = True
    else:
        USE_CLUTTER_TO_DISPLAY = False
    
    
    if USE_CLUTTER_TO_DISPLAY:
        import clutter
        import cluttergst
        clutter.threads_init()
        clutter.init()
    
    ##
    ## Mode
    ##
    mode = sys.argv[1]    
    print "=== %s ===" % sys.argv[0]
    print "Mode: %s" % mode
    
    # Enable parameters due to mode
    if mode == "master":
        parameters = {"account": MASTER_ACCOUNT, "password": MASTER_PASSWORD,
                      "port": dbus.UInt32(5222), "server": MASTER_ACCOUNT.split("@")[-1]}
    else:
        parameters = {"account": SLAVE_ACCOUNT, "password": SLAVE_PASSWORD,
                      "port": dbus.UInt32(5222), "server": SLAVE_ACCOUNT.split("@")[-1]}
    
    ##
    ## Clutter
    ##
    if USE_CLUTTER_TO_DISPLAY:
        stage = clutter.Stage(default=True)
        stage.set_size(320, 240)
        stage.set_color(clutter.color_from_string('DarkSlateGrey'))
        
        video_texture = clutter.Texture()
        video_texture.show()
        stage.add(video_texture)
    
    ##
    ## Telepathy
    ##
    # Get the requested manager
    reg = telepathy.client.ManagerRegistry()
    reg.LoadManagers()    
    manager = reg.GetManager("gabble")
    
    # Request connection
    conn_bus_name, conn_object_path = manager[CONNECTION_MANAGER].\
                                            RequestConnection("jabber", parameters)             
    conn = telepathy.client.Connection(conn_bus_name, conn_object_path)
    
    # Listen signals
    conn[CONNECTION].connect_to_signal("NewChannel", on_new_channel_user)
    conn[CONNECTION].connect_to_signal("StatusChanged", on_status_changed_user)
    
    # Connect
    conn[CONNECTION].Connect()
    
    ##
    ## Test
    ##
    if USE_CLUTTER_TO_DISPLAY:
        stage.show_all()
        clutter.main()
    else:
        loop = gobject.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            print 'interrupted'
