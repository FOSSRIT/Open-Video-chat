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

GST_INPIPE = "udpsrc ! theoradec ! ffmpegcolorspace ! xvimagesink force-aspect-ratio=true"
GST_OUTPIPE_BASE = "v4l2src ! videorate ! video/x-raw-yuv,width=320,height=240,framerate=15/1 ! tee name=t ! theoraenc bitrate=50 speed-level=2 ! udpsink host=%s t. ! queue ! ffmpegcolorspace ! ximagesink"

class GSTStack:
    def __init__(self, link_function):
        self._out_pipeline = None
        self._in_pipeline = None
        self.link_funciton = link_function

        

    def build_outgoing_pipeline(self, ip):
        if self._out_pipeline != None:
            print "WARNING: incoming pipline exists"
            return

        print "Starting outgoing pipeline UDP to %s" % ip 
        self.out = gst.parse_launch ( GST_OUTPIPE_BASE % ip )

        bus = self.out.get_bus()
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
        print "Starting Incoming Video Pipeline"
        self._in_pipeline = gst.parse_launch( GST_INPIPE )

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
