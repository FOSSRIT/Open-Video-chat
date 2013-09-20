#!/usr/bin/env python

# Imports
from gi.repository import GLib, Gtk, Gdk, GdkX11, Gst, GstVideo, TelepathyGLib as Tp, TelepathyFarstream as Tf, Farstream as Fs
from pprint import pprint as pp

class Call(Gtk.Grid):

    # Properties
    contact_entry = None
    drawing_area = None
    preview_xid = None
    account_manager = None
    account = None
    call_handler = None
    call_observer = None
    call_channel = None
    farstream_notifier = None
    farstream_channel = None
    pipeline = None
    pipe_bus = None

    def __init__(self):
        Gtk.Grid.__init__(self, expand=True)
        self.create_ui()

    def create_ui(self):
        print "Creating UI..."

        # Contact ID entry
        self.contact_entry = Gtk.Entry(hexpand=True, placeholder_text="contact id...", tooltip_text="ex. `cdelorme@jabber.sugarlabs.org`")

        # Call Button
        contact_button = Gtk.Button(label="Call")
        contact_button.connect("clicked", self.call_contact)

        # Drawing Area for Video Preview
        self.drawing_area = Gtk.DrawingArea(expand=True)
        self.drawing_area.connect("realize", self.preview_realized)

        # Container for Drawing Area
        event_box = Gtk.EventBox(expand=True)
        event_box.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.01, .01, .01, .9))
        event_box.add(self.drawing_area)

        # Attach to UI
        self.attach(event_box, 0, 0, 2, 1)
        self.attach(self.contact_entry, 0, 1, 1, 1)
        self.attach(contact_button, 1, 1, 1, 1)

    def preview_realized(self, drawing_area):
        print "Grabbing XID for previewing GStreamer Stream..."

        # Grab XID for GStreamer Viewing
        self.preview_xid = drawing_area.get_window().get_xid()

        # Grab Account Manager
        self.account_manager = Tp.AccountManager.dup()

        if self.account_manager:
            print "Configuring account manager..."

            # Grab Factory and setup
            factory = self.account_manager.get_factory()
            if factory:
                factory.add_account_features([
                    Tp.Account.get_feature_quark_connection()               # When we ask for accounts, make sure they have connections
                ])
                factory.add_connection_features([
                    Tp.Connection.get_feature_quark_contact_list(),         # Connections should have populated contact lists
                ])
                factory.add_contact_features([
                    Tp.ContactFeature.ALIAS,                                # Contacts will be loaded with user Alias's
                ])
                factory.add_channel_features([
                    Tp.Channel.get_feature_quark_contacts(),                # Make sure we have contacts on the channel
                    Tp.TextChannel.get_feature_quark_chat_states(),         # Gets us additional message info
                    Tp.TextChannel.get_feature_quark_incoming_messages(),   # Yes, we want to know about incoming messages
                ])

            # Async Prepare AM
            self.account_manager.prepare_async(None, self.account_manager_callback, None)

    def account_manager_callback(self, account_manager, status, data):
        print "Creating call channel handler & observer..."

        # Close Async
        account_manager.prepare_finish(status)

        # Grab Account
        accounts = account_manager.dup_valid_accounts()
        for account in accounts:
            if self.account is None and account.get_protocol() == "jabber" and account.is_enabled():
                self.account = account

        # Create a handler for our video calls
        self.call_handler = Tp.SimpleHandler.new_with_am(
            account_manager,
            False,
            False,
            "OVC.Call.Handler",
            False,
            self.incoming_call_channel,
            None
        )

        self.call_handler.add_handler_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_CALL,           # Channel Type (Call)
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),     # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_REQUESTED: False,                                # Don't process channels we ourselves requested
        })
        self.call_handler.add_handler_capabilities(
            Tp.IFACE_CHANNEL_INTERFACE_MESSAGES,                                # Let dbus know we want messages
        )
        self.call_handler.register()

        # Create an Observer for Video Calls
        self.call_observer = Tp.SimpleObserver.new_with_am(
            account_manager,
            False,
            "OVC.Call.Observer",
            False,
            self.observing_call,
            None
        )
        self.call_observer.add_observer_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_CALL,           # Only look for call channels
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),     # Private channels only
        })
        self.call_observer.set_observer_delay_approvers(True)
        self.call_observer.register()

    def observing_call(
        self,
        observer,
        account,
        connection,
        channels,
        operation,
        requests,
        context,
        data
    ):
        # Testing
        pp(channels)

        if account is self.account and self.call_channel is None and operation and len(channels):
            print "Observed a Call!"

            # Claim Channel
            operation.claim_with_async(
                self.call_handler,
                self.claimed_call_channel,
                channels[0]
            )

            # Wait for claim before accepting context
            context.accept()

    def claimed_call_channel(self, operation, status, channel):
        operation.claim_with_finish(status)

        # Prepare Channel
        channel.prepare_async(None, self.call_channel_activated, None)

    def call_contact(self, button):

        # Grab Contact ID
        contact_id = self.contact_entry.get_text()

        # Describe a Call Channel
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_CALL,
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),
            Tp.PROP_CHANNEL_TARGET_ID: contact_id,
            Tp.PROP_CHANNEL_TYPE_CALL_INITIAL_VIDEO: True,
            Tp.PROP_CHANNEL_TYPE_CALL_INITIAL_AUDIO: False,
        }

        # Request Call Channel
        request = Tp.AccountChannelRequest.new(
            self.account,
            channel_description,
            Tp.USER_ACTION_TIME_NOT_USER_ACTION,
        )
        request.create_channel_async(
            self.call_handler.get_bus_name(),
            None,
            self.request_call_channel,
            None
        )

    def request_call_channel(self, request, status, data):
        request.create_channel_finish(status)

    def incoming_call_channel(
        self,
        handler,
        account,
        connection,
        channels,
        requests,
        code,
        context,
        data
    ):
        # Testing
        pp(channels)

        if account is self.account and self.call_channel is None and len(channels):
            print "Incoming Call Channel!"
            channels[0].prepare_async(None, self.call_channel_activated, None)
            context.accept()
        else:
            context.fail()

    def call_channel_activated(self, channel, status, data):
        print "Configuring Call Channel..."
        channel.prepare_finish(status)

        # Grab Copy
        self.call_channel = channel

        # Handle Channel Status
        self.call_channel.connect("invalidated", self.call_channel_invalid)
        self.call_channel.connect("state-changed", self.call_state_changed)

        # Wrap our new channel inside Farstream
        Tf.Channel.new_async(channel, self.convert_to_farstream, None)

    def call_channel_invalid(self, domain, code, message, data):
        print "Call has been Invalidated!"
        print message

    def call_state_changed(self, channel, state, flags, reason, details, data):
        print "Checking state change of Call Channel..."

        # If call has ended close up farstream & GStreamer
        if state == Tp.CallState.ENDED:

            if self.farstream_channel:
                self.farstream_channel = None

            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
                self.pipeline = None

            channel.close_async(None, None, None)

    def convert_to_farstream(self, channel, status, data):
        print "Converting call channel to farstream..."

        # Close Async and Grab our now "TelepathyFarstream" channel (let's just hope we can actually use it as such)
        self.farstream_channel = Tf.Channel.new_finish(channel, status)

        # Prepare GStreamer Pipeline
        self.pipeline = Gst.Pipeline()

        # Grab the bus to configure & connect signals
        self.pipe_bus = self.pipeline.get_bus()
        self.pipe_bus.add_watch(GLib.PRIORITY_DEFAULT, self.watch_farstream_bus, None)
        # self.pipe_bus.add_signal_watch() # There can be ONLY ONE!
        self.pipe_bus.enable_sync_message_emission()

        # Connect Signals
        # self.pipe_bus.connect("message", self.pipe_bus_message)
        self.pipe_bus.connect("sync-message::element", self.connect_video_to_drawing_area)

        # Connect Farstream Notifier
        self.farstream_notifier = Fs.ElementAddedNotifier.new()
        self.farstream_notifier.add(self.pipeline)

        # Connect Handlers
        self.farstream_channel.connect("fs-conference-added", self.farstream_conference_added)
        self.farstream_channel.connect("content-added", self.farstream_content_added)

    # def pipe_bus_message(self, bus, message):

    #     if message.type is Gst.MessageType.STATE_CHANGED:
    #         pass # This can be really noisy, so I have disabled it for now
    #         pp(message.parse_state_changed())

    #     if message.type is Gst.MessageType.EOS:
    #         pp("Stream Ended")

    #     if message.type is Gst.MessageType.ERROR:
    #         try:
    #             pp("Error: %s, %s" % message.parse_error())
    #         except Exception:
    #             pp("Uncatachable Error")

    def connect_video_to_drawing_area(self, bus, message):
        if message.get_structure():
            if message.get_structure().get_name() == "prepare-window-handle":
                print "Attaching ximagesink to XID..."
                message.src.set_window_handle(self.preview_xid)

    def watch_farstream_bus(self, bus, message, data):

        # Deliver Messages to Farstream Channel
        if self.farstream_channel:
            self.farstream_channel.bus_message(message)

    def farstream_conference_added(self, channel, conference):
        print "Ready to begin pipeline playback"

        # Add conference to Gst Pipeline
        self.pipeline.add(conference)

        # Using the Conference as our element, set defaults for our notifier
        self.farstream_notifier.set_default_properties(conference)

        # Ready to start pipeline
        self.pipeline.set_state(Gst.State.PLAYING)

    def farstream_content_added(self, channel, content):
        print "Content Added to Pipeline!"

        # Grab properties for parsing
        sinkpad = content.get_property("sink-pad")
        mtype = content.get_property("media-type")

        # Check media Type
        codecs = []
        if mtype is Fs.MediaType.VIDEO:

            # Set Video Codec
            # codecs.append(
            #    Fs.Codec.new(
            #        Fs.CODEC_ID_ANY,
            #        "THEORA",
            #        Fs.MediaType.VIDEO,
            #        0
            #    )
            # )

            # Create Bin
            bin = Gst.parse_bin_from_description("videotestsrc is-live=1 ! capsfilter caps=video/x-raw,width=320,height=240", True)

        elif mtype is Fs.MediaType.AUDIO:

            # Set Audio Codec
            # codecs.append(
            #    Fs.Codec.new(
            #        Fs.CODEC_ID_ANY,
            #        "SPEEX",
            #        Fs.MediaType.AUDIO,
            #        0
            #    )
            # )

            # Create Bin
            bin = Gst.parse_bin_from_description("audiotestsrc is-live=1 ! queue", True)

        # Second argument in parse_bin_from_description is to "Ghost" unlinked pads, prevents pipeline errors

        # Modern telepathy-farstream auto-negotiates codecs with defaults
        # Apply Codecs
        # try:
        #    content.get_property("fs-session").set_codec_preferences(codecs)
        # except Exception, e:
        #    print "Error setting codecs..."
        #    print e.message

        # Connect src-pad event
        content.connect("src-pad-added", self.farstream_src_pad_added)

        if bin:

            # Add components to our pipeline
            self.pipeline.add(bin)

            # Grab an unlinked pad
            unused_pad = bin.find_unlinked_pad(Gst.PadDirection.SRC)

            if unused_pad:

                # link the new sinkpad to our pipeline
                unused_pad.link(sinkpad)

                # Begin playback
                src.set_state(Gst.State.PLAYING)

    def farstream_src_pad_added(self, content, handle, stream, pad, codec, data):
        print "Setting up incoming gstreamer pipeline"

        # Create bin by type
        mtype = content.get_property("media-type")
        if mtype == Fs.MediaType.AUDIO:
            bin = Gst.parse_bin_from_description("audioconvert ! audioresample ! autoaudiosink", True)
        elif mtype == Fs.MediaType.VIDEO:
            bin = Gst.parse_bin_from_description("videoconvert ! videoscale ! ximagesink", True)

        # Add to pipeline
        self.pipeline.add(bin)

        # Grab Sink
        unused_sink = bin.find_unlinked_pad(Gst.PadDirection.SINK)

        if unused_sink:

            # Link sink to network pad
            pad.link(unused_sink)

            # Begin playback
            bin.set_state(Gst.State.PLAYING)

if __name__ == "__main__":

    # Initialize Gst
    Gst.is_initialized() or Gst.init(None)

    # Create Window
    window = Gtk.Window()

    # Set Size
    window.set_default_size(800, 600)

    # Attach Class for Demo
    window.add(Call())

    # Close on Close
    window.connect("delete-event", Gtk.main_quit)

    # Display
    window.show_all()

    # Begin main Loop
    Gtk.main()
