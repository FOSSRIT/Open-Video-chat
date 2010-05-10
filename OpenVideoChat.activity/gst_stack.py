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
:mod: `OpenVideoChat/OpenVideoChat.activity/gst_stack` -- Open Video Chat GStreamer Stack
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthro:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import gst

CAPS = "video/x-raw-yuv,width=320,height=240,framerate=15/1"

class GSTStack:
    def __init__(self, link_function):
        self._out_pipeline = None
        self._in_pipeline = None
        self.link_funciton = link_function

        

    def build_outgoing_pipeline(self, ip):
        if self._out_pipeline != None:
            print "WARNING: incoming pipline exists"
            return

        print "Building outgoing pipeline UDP to %s" % ip
        
        # Pipeline:
        # v4l2src -> videorate -> (CAPS) -> tee -> theoraenc -> udpsink
        #                                     \
        #                                      -> queue -> ffmpegcolorspace -> ximagesink
        self._out_pipeline = gst.Pipeline()
        
        # Video Source
        video_src = gst.element_factory_make("v4l2src")
        self._out_pipeline.add( video_src )

        # Video Rate element to allow setting max framerate
        video_rate = gst.element_factory_make("videorate")
        self._out_pipeline.add( video_rate )
        video_src.link( video_rate )

        # Add caps to limit rate and size
        video_caps = gst.element_factory_make("capsfilter")
        video_caps.set_property( "caps", gst.Caps( CAPS ) )
        self._out_pipeline.add( video_caps )
        video_rate.link( video_caps )

        #Add tee element
        video_tee = gst.element_factory_make("tee")
        self._out_pipeline.add( video_tee )
        video_caps.link( video_tee )

        # Add theora Encoder
        video_enc = gst.element_factory_make("theoraenc")
        video_enc.set_property("bitrate", 50)
        video_enc.set_property("speed-level", 2)
        self._out_pipeline.add( video_enc )
        video_tee.link( video_enc )

        # Add udpsink
        udp_sink = gst.element_factory_make("udpsink")
        udp_sink.set_property("host", ip)
        self._out_pipeline.add( udp_sink )
        video_enc.link( udp_sink )

        ## On other side of pipeline. connect tee to ximagesink
        # Queue element to receive video from tee
        video_queue = gst.element_factory_make("queue")
        self._out_pipeline.add( video_queue )
        video_tee.link( video_queue )

        # Change colorspace for ximagesink
        video_colorspace = gst.element_factory_make("ffmpegcolorspace")
        self._out_pipeline.add( video_colorspace )
        video_queue.link( video_colorspace )

        # Send to ximagesink
        ximage_sink = gst.element_factory_make("ximagesink")
        self._out_pipeline.add( ximage_sink )
        video_colorspace.link( ximage_sink )

        # Connect to pipeline bus for signals.
        bus = self._out_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        def on_message(bus, message):
            """
            This method handles errors on the video bus and then stops
            the pipeline.
            """
            t = message.type
            if t == gst.MESSAGE_EOS:
                self._out_pipeline.set_state(gst.STATE_NULL)
            elif t == gst.MESSAGE_ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._out_pipeline.set_state(gst.STATE_NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-xwindow-id":
                # Assign the viewport
                self.link_funciton(message.src, 'PREVIEW')
        
        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)

    def build_incoming_pipeline(self):
        if self._in_pipeline != None:
            print "WARNING: incoming pipline exists"
            return
        
        # Set up the gstreamer pipeline
        print "Building Incoming Video Pipeline"
        
        # Pipeline:
        # udpsrc -> theoradec -> ffmpegcolorspace -> xvimagesink
        self._in_pipeline = gst.Pipeline()

        # Video Source
        video_src = gst.element_factory_make("udpsrc")
        self._in_pipeline.add( video_src )

        # Video decode
        video_decode = gst.element_factory_make("theoradec")
        self._in_pipeline.add( video_decode )
        video_src.link( video_decode )

        # Change colorspace for xvimagesink
        video_colorspace = gst.element_factory_make("ffmpegcolorspace")
        self._in_pipeline.add( video_colorspace )
        video_decode.link( video_colorspace )

        # Send video to xviamgesink
        xvimage_sink = gst.element_factory_make("xvimagesink")
        xvimage_sink.set_property("force-aspect-ratio", True)
        self._in_pipeline.add( xvimage_sink )
        video_colorspace.link( xvimage_sink )

        # Connect to pipeline bus for signals.
        bus = self._in_pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()

        def on_message(bus, message):
            """
            This method handles errors on the video bus and then stops
            the pipeline.
            """
            t = message.type
            if t == gst.MESSAGE_EOS:
                self._in_pipeline.set_state(gst.STATE_NULL)
            elif t == gst.MESSAGE_ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._in_pipeline.set_state(gst.STATE_NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-xwindow-id":
                # Assign the viewport
                self.link_funciton(message.src, 'MAIN')
        
        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)

    def start_stop_outgoing_pipeline(self, start=True):
        if self._out_pipeline != None:
            if start:
                print "Setting Outgoing Pipeline state: STATE_PLAYING"
                self._out_pipeline.set_state(gst.STATE_PLAYING)
            else:
                print "Setting Outgoing Pipeline state: STATE_NULL"
                self._out_pipeline.set_state(gst.STATE_NULL)

    def start_stop_incoming_pipeline(self, start=True):
        if self._in_pipeline != None:
            if start:
                print "Setting Incoming Pipeline state: STATE_PLAYING"
                self._in_pipeline.set_state(gst.STATE_PLAYING)
            else:
                print "Setting Incoming Pipeline state: STATE_NULL"
                self._in_pipeline.set_state(gst.STATE_NULL)
