#!/usr/bin/env python
# gst-launch-1.0 videotestsrc ! videorate ! capsfilter ! video/x-raw,width=800,height=400,framerate=30/1 ! videoconvert ! ximagesink


# Imports
from gi.repository import Gtk, Gdk, GdkX11, Gst, GstVideo
from pprint import pprint as pp


# Constants
CAPS = "video/x-raw,width=320,height=240,framerate=15/1"


# Class Extension
class Stream(Gtk.Grid):

    def __init__(self):
        Gtk.Grid.__init__(self, expand=True)

        # Create Event Box and set dark BG
        event_box = Gtk.EventBox()

        # Make the BG Dark
        event_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))

        # Create the drawing area
        self.drawing_area = Gtk.DrawingArea(expand=True)

        # Connect realize event for xid availability (xid is not available until "realized")
        self.drawing_area.connect("realize", self.drawing_area_realized)

        # Attach to Event Box
        event_box.add(self.drawing_area)

        # Create Width and Height Settings
        self.width_entry = Gtk.Entry(hexpand=True, tooltip_text="Video Width", text="320", placeholder_text="width...")
        self.height_entry = Gtk.Entry(hexpand=True, tooltip_text="Video Height", text="240", placeholder_text="height...")
        self.fps_entry = Gtk.Entry(hexpand=True, tooltip_text="Frames Per Second", text="15", placeholder_text="fps...")

        # Create Change Button
        settings_button = Gtk.Button(label="Apply", tooltip_text="Change Video Settings")

        # Connect Button to Dynamically Change Settings
        settings_button.connect("clicked", self.change_settings)

        # Add to Grid
        self.attach(event_box, 0, 0, 4, 1)
        self.attach(self.width_entry, 0, 1, 1, 1)
        self.attach(self.height_entry, 1, 1, 1, 1)
        self.attach(self.fps_entry, 2, 1, 1, 1)
        self.attach(settings_button, 3, 1, 1, 1)

    def drawing_area_realized(self, drawing_area):
        pp("Setting up GStreamer")

        # Grab DrawingArea XID
        self.preview_xid = drawing_area.get_window().get_xid()

        """ Prepare Elements """
        #video_source = Gst.ElementFactory.make('autovideosrc', "video-source")
        video_source = Gst.ElementFactory.make('videotestsrc', "video-source")
        video_rate = Gst.ElementFactory.make('videorate', None)
        self.video_caps = video_caps = Gst.ElementFactory.make('capsfilter', None)
        video_caps.set_property("caps", Gst.caps_from_string(CAPS))
        video_convert = Gst.ElementFactory.make("videoconvert", None)
        ximage_sink = Gst.ElementFactory.make("ximagesink", "video-preview")

        """ Create the Pipeline """
        self.pipe = Gst.Pipeline()

        """ Add Elements to Pipeline (Remember: Order Matters) """
        self.pipe.add(video_source)
        self.pipe.add(video_rate)
        self.pipe.add(video_caps)
        self.pipe.add(video_convert)
        self.pipe.add(ximage_sink)

        """ Chain together the Elements (Order also matters) """
        video_source.link(video_rate)
        video_rate.link(video_caps)
        video_caps.link(video_convert)
        video_convert.link(ximage_sink)

        # Acquire pipe bus
        self.pipe_bus = self.pipe.get_bus()

        # Make sure it knows we want to listen for signals
        self.pipe_bus.add_signal_watch()

        # Tell the bus we want to handle video messages synchronously
        self.pipe_bus.enable_sync_message_emission()

        # Connect Signals
        self.pipe_bus.connect("message", self.pipe_bus_message)
        self.pipe_bus.connect("sync-message::element", self.connect_video_to_drawing_area)

        # Start Pipeline
        self.pipe.set_state(Gst.State.PLAYING)

        # The above pipeline can be manually written and tested with gst-launch as a string:
        # videotestsrc ! videorate ! capsfilter ! video/x-raw,width=320,height=240,framerate=15/1 ! videoconvert ! ximagesink
        # If we want to avoid creating all of the elements individually we can also use the `Gst.Parse.bin_from_description` method and supply it the above string to create a "bin"
        # If we add a "name=" to the above elements, we can then extract them if we need to use them.

    def pipe_bus_message(self, bus, message):
        #if message.type is Gst.MessageType.STATE_CHANGED:
        #    pp(message.parse_state_changed())

        if message.type is Gst.MessageType.EOS:
            pp("Stream Ended")

        if message.type is Gst.MessageType.ERROR:
            try:
                pp("Error: %s, %s" % message.parse_error())
            except Exception:
                pp("Uncatachable Error")

    def connect_video_to_drawing_area(self, bus, message):
        if message.get_structure():
            if message.get_structure().get_name() == "prepare-window-handle":
                message.src.set_window_handle(self.preview_xid)

    def change_settings(self, button):

        # Build new Caps String
        new_caps = "video/x-raw,width=" + self.width_entry.get_text() + ",height=" + self.height_entry.get_text() + ",framerate=" + self.fps_entry.get_text() + "/1"

        # Set New Caps
        self.video_caps.set_property("caps", Gst.caps_from_string(new_caps))

# If executed stand-alone, this will demo itself
if __name__ == "__main__":

    # Initialize Gst
    Gst.is_initialized() or Gst.init(None)

    # Create a window to hold the chat system
    window = Gtk.Window()
    window.set_default_size(800, 600)
    window.add(Stream())
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
