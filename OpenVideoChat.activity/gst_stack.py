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
:mod: `OpenVideoChat/OpenVideoChat.activity/gst_stack` --
        Open Video Chat GStreamer Stack
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthor:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. moduleauthor:: Caleb Coffie <CalebCoffie@gmail.com>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""

# External Imports
import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from gst_bins import VideoOutBin
from gst_bins import AudioOutBin
from gst_bins import VideoInBin
from gst_bins import AudioInBin

#Define the limitations of the device
CAPS = "video/x-raw,width=320,height=240,framerate=15/1"


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GSTStack(object):

    def __init__(self):
        Gst.init(None)
        self._out_pipeline = None
        self._in_pipeline = None
        self._audio_out_bin = None
        self._video_out_bin = None
        self._audio_in_bin = AudioInBin()
        self._video_in_bin = VideoInBin()
        self._incoming_window_xid = None
        self._video_local_tee = Gst.ElementFactory.make("tee", None)

    # Temporary Working Output
    def build_working_preview(self, handle):

        """ Prepare Elements """
        video_source = Gst.ElementFactory.make('autovideosrc', "video-source")
        video_rate = Gst.ElementFactory.make('videorate', None)
        video_scale = Gst.ElementFactory.make("videoscale", None)
        video_scale.set_property('add-borders', True)
        video_caps = Gst.ElementFactory.make("capsfilter", None)
        # "video/x-raw,width=320,height=240,framerate=15/1"
        video_caps.set_property("caps", Gst.caps_from_string(CAPS))
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        ximage_sink = Gst.ElementFactory.make("ximagesink", "video-output")

        """ Create Pipeline """
        self.pipe = Gst.Pipeline()

        """ Add Elements to Pipeline """
        self.pipe.add(video_source)
        self.pipe.add(video_rate)
        self.pipe.add(video_scale)
        self.pipe.add(video_caps)
        self.pipe.add(video_convert)
        self.pipe.add(ximage_sink)

        """ Connect Elements """
        video_source.link(video_rate)
        video_rate.link(video_scale)
        video_scale.link(video_caps)
        video_caps.link(video_convert)
        video_convert.link(ximage_sink)

        # Grab the Bus
        bus = self.pipe.get_bus()

        # Listen to signals (messages) on bus
        bus.add_signal_watch()

        # Synchronously handle video transmission messages
        bus.enable_sync_message_emission()

        # Handler for EOS & Errors
        bus.connect('message', self.on_message)

        # Attach Rendering
        bus.connect("sync-message::element", self.draw_preview)

        """ Begin Playing """
        self.pipe.set_state(Gst.State.PLAYING)

        # External Reference
        self.video_caps = video_caps

        """ Return Pipeline Bus """
        return self.pipe.get_bus()

    # Handle Errors and End of Stream
    def on_message(self, bus, message):

        # logger.debug(message.type)
        if message.type == Gst.MessageType.STATE_CHANGED:
            logger.debug(message.parse_state_changed())

        if message.type == Gst.MessageType.EOS:
            logger.debug("End of Stream, Close Pipeline")
        elif message.type == Gst.MessageType.ERROR:
            try:
                err, debug = message.parse_error()
                logger.debug("Error: %s" % err, debug)
            except Exception:
                logger.debug("Unable to identify message error.")

    def draw_preview(self, bus, message):
        if message.get_structure() is None:
            return

        # Capture the new GStreamer handle request
        if message.get_structure().get_name() == "prepare-window-handle":
            message.src.set_window_handle(self.draw.get_window().get_xid())



    """ Newer Incomplete Code Below """


    #Set incoming window xid
    def set_incoming_window(self, xid):
        self._incoming_window_xid = xid

    #Toggle Video State (args are on or off)
    def toggle_video_state(self, start=True):
        if self._out_pipeline != None:
            if start:
                print "Setting video bin state: STATE_PLAYING"
                self._video_out_bin.set_state(Gst.State.PLAYING)
            else:
                print "Setting video bin state: STATE_NULL"
                self._video_out_bin.set_state(Gst.State.NULL)


    #Toggle Audio State
    def toggle_audio_state(self, start=True):
        if self._out_pipeline != None:
            if start:
                print "Setting audio bin state: STATE_PLAYING"
                self._audio_out_bin.set_state(Gst.State.PLAYING)
            else:
                print "Setting audio bin state: STATE_NULL"
                self._audio_out_bin.set_state(Gst.State.NULL)

    #Build Preview
    def build_preview(self, xid):
         #Checks if there is outgoing pipeline already
        if self._out_pipeline != None:
            print "WARNING: outgoing pipeline exists"
            return

        # Start Outgoing pipeline
        self._out_pipeline = Gst.Pipeline()

        self.xid = xid

        print "BUILDING PREVIEW"

        # Build Video Source (Webcam) and add to outgoing pipeline
        # Video Source
        video_src = Gst.ElementFactory.make("autovideosrc", None)
        self._out_pipeline.add(video_src)

        # Video Rate element to allow setting max framerate
        video_rate = Gst.ElementFactory.make("videorate", None)
        self._out_pipeline.add(video_rate)

        # Add caps to limit rate and size
        video_caps = Gst.ElementFactory.make("capsfilter", None)
        video_caps.set_property("caps", Gst.caps_from_string(CAPS))
        self._out_pipeline.add(video_caps)

        # Add tee element
        self._out_pipeline.add(self._video_local_tee)

        # Link Elements
        video_src.link(video_rate)
        video_rate.link(video_caps)
        video_caps.link(self._video_local_tee)


        # Preview the Video
        # Queue element to receive video from tee
        video_queue = Gst.ElementFactory.make("queue", None)
        self._out_pipeline.add(video_queue)

        # Change colorspace for ximagesink
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        self._out_pipeline.add(video_convert)

        # Send to ximagesink
        ximage_sink = Gst.ElementFactory.make("ximagesink", None)
        self._out_pipeline.add(ximage_sink)

        # Link Elements Again
        self._video_local_tee.link(video_queue)
        video_queue.link(video_convert)
        video_convert.link(ximage_sink)

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
            if t == Gst.MessageType.EOS:
                self._out_pipeline.set_state(Gst.State.NULL)
            elif t == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._out_pipeline.set_state(Gst.State.NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-window-handle":
                # Assign the viewport
                message.src.set_window_handle(xid)

        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)


    #Outgoing Pipeline
    def build_outgoing_pipeline(self, ip):

        print "Building outgoing pipeline UDP to %s" % self.ip

        # Set Bin IPs
        self._video_out_bin = VideoOutBin(ip)
        self._audio_out_bin = AudioOutBin(ip)

        # Add Video/Audio Out Bin to Pipeline
        self._out_pipeline.add(self._video_out_bin)
        self._out_pipeline.add(self._audio_out_bin)

        # Link Video Bin to Tee Element
        self._video_local_tee.link(self._video_out_bin)



    # Incoming Pipeline
    def build_incoming_pipeline(self):
        if self._in_pipeline != None:
            print "WARNING: incoming pipeline exists"
            return

        # Set up the gstreamer pipeline
        print "Building Incoming Video Pipeline"

        # Pipeline:
        # udpsrc -> rtptheoradepay -> theoradec -> ffmpegcolorspace -> xvimagesink
        self._in_pipeline = Gst.Pipeline()

        self._in_pipeline.add(self._video_in_bin)
        self._in_pipeline.add(self._audio_in_bin)

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
            if t == Gst.MessageType.EOS:
                self._in_pipeline.set_state(Gst.State.NULL)
            elif t == Gst.MessageType.ERROR:
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self._in_pipeline.set_state(Gst.State.NULL)

        def on_sync_message(bus, message):
            if message.structure is None:
                return

            if message.structure.get_name() == "prepare-window-handle":
                # Assign the viewport
                message.src.set_window_handle(self._incoming_window_xid)

        bus.connect("message", on_message)
        bus.connect("sync-message::element", on_sync_message)

    def start_stop_outgoing_pipeline(self, start=True):
        if self._out_pipeline != None:
            if start:
                print "Setting Outgoing Pipeline state: STATE_PLAYING"
                self._out_pipeline.set_state(Gst.State.PLAYING)
            else:
                print "Setting Outgoing Pipeline state: STATE_NULL"
                self._out_pipeline.set_state(Gst.State.NULL)

    def start_stop_incoming_pipeline(self, start=True):
        if self._in_pipeline != None:
            if start:
                print "Setting Incoming Pipeline state: STATE_PLAYING"
                self._in_pipeline.set_state(Gst.State.PLAYING)
            else:
                print "Setting Incoming Pipeline state: STATE_NULL"
                self._in_pipeline.set_state(Gst.State.NULL)
