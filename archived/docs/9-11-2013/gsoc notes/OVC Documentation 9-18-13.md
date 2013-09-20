
# OVC Documentation 9-18-13

[Farstream Docs](http://www.freedesktop.org/software/farstream/apidoc/farstream/)

Todays Tasks:

- Setup Demo Code for Call Channel
- Attach GStreamer with test video source
- Catch channel with separate script
- Extract video and playback

The sender will have a "send" and "close" button.

The receiver will have a drawing area for playback.


---

I have a handler and observer setup that "appear" to be running.

I have a sender that is able to establish the channel successfully.

I have to:

- Add Video
- Receiver channel once data flows

Until sending a message, the text channel never hit the otherside, so I am assuming that until the data-stream hits the other side I won't get the call channel.


---

Great, new imports and more documentation:

    from gi.repository import TelepathyFarstream
    from gi.repository import Farstream

These may not even be the right documentation versions:

- [Farstream Docs](http://www.freedesktop.org/software/farstream/apidoc/farstream/)
- [TelepathyFarstream Docs](http://telepathy.freedesktop.org/doc/telepathy-farstream/)

The goal is to translate the code from the telepthy-farstream source examples, all of the python is of course one or more versions ago dated.


---

Full Docs List:

- [GLib Docs](https://developer.gnome.org/glib/unstable/glib-The-Main-Event-Loop.html)
- [TelepathyGLib Docs](http://telepathy.freedesktop.org/doc/telepathy-glib/)
- [Farstream Docs](http://www.freedesktop.org/software/farstream/apidoc/farstream/)
- [TelepathyFarstream Docs](http://telepathy.freedesktop.org/doc/telepathy-farstream/)
- [GStreamer Core](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/)
- [GStreamer Plugins Core](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer-plugins/html/)
- [GStreamer Plugins Base](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/)
- [GStreamer Plugins Good](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good-plugins/html/)

New **Complete(?)** Imports List:

    from gi.repository import GLib, Gtk, Gdk, GdkX11, Gst, GstVideo, TelepathyGLib as Tp, TelepathyFarstream as Tf, Farstream as Fs

A snippet of old code:

        self.pipeline = gst.Pipeline()
        self.pipeline.get_bus().add_watch(self.async_handler)

        self.notifier = notifier = farstream.ElementAddedNotifier()
        notifier.set_properties_from_file("element-properties")
        notifier.add(self.pipeline)

Translation:

        self.pipeline = Gst.Pipeline()
        self.pipeline.get_bus().add_watch(self.handle_message)

        self.notifier = Farstream.ElementAddedNotifier.new()
        self.notifier.add(self.pipeline)

From the [add_watch docs](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstBus.html#gst-bus-add-watch) it appears to catch messages and allow them to be forwarded.  The old source indiciates that these messages need to be fired through the TelepathyFarstream channel using the [bus_message](http://telepathy.freedesktop.org/doc/telepathy-farstream/TfChannel.html#tf-channel-bus-message) method in order to work with the stream changes.  So in a sense it may be like a link method if Farstream was a proper GStreamer element?

The "element-properties" it loads appear as:

    # Put the desired properties in the style of
    #
    # [element name]
    # prop1=val1

    [gstrtpbin]
    latency=100

    [x264enc]
    byte-stream=1
    bframes=0
    b-adapt=0
    cabac=0
    dct8x8=0
    bitrate=256
    # tuned for zero latency
    tune=0x4
    profile=1
    speed-preset=3
    sliced-threads=false

    [ffenc_h263]
    rtp-payload-size=1

    [theoraenc]
    bitrate=256

    [vp8enc]
    bitrate=256000
    max-latency=1
    speed=2
    error-resilient=true

    # Work around bug in the re-timestamp slaving method in
    # GStreamer (2 is skew)
    [alsasrc]
    slave-method=2

    [osssrc]
    slave-method=2

    [oss4src]
    slave-method=2

    [sunaudiosrc]
    slave-method=2

    [rtph264pay]
    config-interval=5

    [rtppcmupay]
    ptime-multiple=20000000

    [rtppcmapay]
    ptime-multiple=20000000

    [gstrtpjitterbuffer]
    do-lost=1

    [ewh264enc]
    profile=baseline
    quality=5

I am not versed enough in the various plugin properties to understand exactly what all of that is doing, so decyphering this could take a long time.

As I understand it, we create the pipeline, add it to the Farstream Notifier.

The next bit of code is:

        tpfarstream.tf_channel_new_async (connection.service_name,
            connection.object_path, object_path, self.tpfs_created)

So, this indicates that we are using TelepathyFarstream to create a new channel, not TelepathyGLib, and not a "call" channel (at least that I can tell).

Well, that was scary, the python api appears incomplete since I have to build in C-Style, which may not be possible without type definitions.

Listing some bugs next...

---

Test creating channel to user:

bed143950e44089a123773f0265e24c1aabae5a2@jabber.sugarlabs.org


---

Python API is perhaps incomplete?

I have to follow the C development path, which is in some ways not feasible.

For example, in C you can do:

    TpChannel *proxy

There is no such thing in python, so I have to run create/ensure to get a TpCallChannel, then send that through the TelepathyFarstream Channel constructor?

Similarly when I try to run new_finish, I have to pass the channel as the first argument.  It either looks like this `channel.new_finish(channel, result)`, or this `Tf.Channel.new_finish(channel, result)`.  Both work, but clearly the first feels redundant since the python-way generally extends from the object.


---

Given that I cannot get anyone to answer in #telepathy, I will see if I can't just move forward and get this thing working.

Next Segment of Old Code:

        tfchannel.connect ("fs-conference-added", self.conference_added)
        tfchannel.connect ("content-added", self.content_added)

Converted to:

    self.call_channel.connect("fs-conference_added", self.call_conference_added)
    self.call_channel.connect("content-added", self.call_content_added)

The [FsConference](http://www.freedesktop.org/software/farstream/apidoc/farstream/FsConference.html) is a key element, effectively we add it to the Gst Pipeline, and are ready to begin playback.

The content-added signal appears to catch all of the elements that are connected to the pipeline.

---

Good news!

I just checked back up in the code, and I think they were actually creating a TelepathyCallChannel object (since back then it did not exist), as I noticed this:

        self.obj = self.bus.get_object (self.conn.service_name, object_path)
        self.obj.connect_to_signal ("CallStateChanged",
            self.state_changed_cb, dbus_interface=CHANNEL_TYPE_CALL)

The callback for that checks "CALL_STATE" constants, so I am going to assume I may have done this the correct way.


---

This section of code, while easy enough to translate, is difficult to understand:

        sinkpad = content.get_property ("sink-pad")

        mtype = content.get_property ("media-type")
        prefs = self.get_codec_config (mtype)
        if prefs != None:
            try:
                content.set_codec_preferences(prefs)
            except GError, e:
                print e.message

        content.connect ("src-pad-added", self.src_pad_added)

        if mtype == farstream.MEDIA_TYPE_AUDIO:
            src = gst.parse_bin_from_description("audiotestsrc is-live=1 ! " \
                "queue", True)
        elif mtype == farstream.MEDIA_TYPE_VIDEO:
            src = gst.parse_bin_from_description("videotestsrc is-live=1 ! " \
                "capsfilter caps=video/x-raw-yuv,width=320,height=240", True)

        self.pipeline.add(src)
        src.get_pad("src").link(sinkpad)
        src.set_state(gst.STATE_PLAYING)

I cannot tell if this is code that executes on incoming call channels, or outgoing.  I still do not know whether Farstream is bi-directional.

I get that we are grabbing the media type to check whether it is an audio or video component.  We are also extracting the pad.  I am curious as to where this information comes from though.

Next comes the Codec Parser:

        if media_type == farstream.MEDIA_TYPE_VIDEO:
            codecs = [ farstream.Codec(farstream.CODEC_ID_ANY, "H264",
                farstream.MEDIA_TYPE_VIDEO, 0) ]
            if self.conn.GetProtocol() == "sip" :
                codecs += [ farstream.Codec(farstream.CODEC_ID_DISABLE, "THEORA",
                                        farstream.MEDIA_TYPE_VIDEO, 0) ]
            else:
                codecs += [ farstream.Codec(farstream.CODEC_ID_ANY, "THEORA",
                                        farstream.MEDIA_TYPE_VIDEO, 0) ]
            codecs += [
                farstream.Codec(farstream.CODEC_ID_ANY, "H263",
                                        farstream.MEDIA_TYPE_VIDEO, 0),
                farstream.Codec(farstream.CODEC_ID_DISABLE, "DV",
                                        farstream.MEDIA_TYPE_VIDEO, 0),
                farstream.Codec(farstream.CODEC_ID_ANY, "JPEG",
                                        farstream.MEDIA_TYPE_VIDEO, 0),
                farstream.Codec(farstream.CODEC_ID_ANY, "MPV",
                                       farstream.MEDIA_TYPE_VIDEO, 0),
            ]

Since we are only going to be using theora, we may as well set it like so:

    codecs = [
        Fs.Codec.new(
            Fs.CODEC_ID_ANY,
            "THEORA",
            Fs.MediaType.VIDEO,
            0
        )
    ]

They connect the pad to a src-pad-added signal triggers on content, and is used to identify when new data is coming in (???).

        type = content.get_property ("media-type")
        if type == farstream.MEDIA_TYPE_AUDIO:
            sink = gst.parse_bin_from_description("audioconvert ! audioresample ! audioconvert ! autoaudiosink", True)
        elif type == farstream.MEDIA_TYPE_VIDEO:
            sink = gst.parse_bin_from_description("ffmpegcolorspace ! videoscale ! autovideosink", True)

        self.pipeline.add(sink)
        pad.link(sink.get_pad("sink"))
        sink.set_state(gst.STATE_PLAYING)

This only serves to convince me further that this chain detects incoming pipelines.  I am also now thinking it may not be bi-directional, but perhaps you can add multiple TfContent's to a single Farstream?

Alright, so maybe this is bi-directional.  The src-pad-added might be waiting on incoming pipeline and will parse it, while the content-added process is actually preparing and playing a pipeline from local video!

Well, I got it working, I had to get the fs-session off of content to run `set_codec_preferences`, as it no-longer exists as part of the TfCallContent object.

Everything appears to be working, except the recipient doesn't appear to be getting any notice of an incoming call channel.

---

Awesome, ocrete began chatting me up in irc, and I am on the right track.

    16:17:02   CDeLorme | Current Source: http://paste.fedoraproject.org/40605/13795353/
    16:17:26   CDeLorme | I am creating a call channel, then "turning it into a telepathy farstream" channel, though I don't know if that is a valid approach
    16:17:48   CDeLorme | I can get as far as attaching the pipeline and playing it, but I am not seeing anything at the other-end of the channel
    16:18:26   CDeLorme | Anyone with Farstream knowledge who might be able to help me figure out the rest?
    16:21:58     ocrete | CDeLorme: do you need special codec prefere3nces ?
    16:22:09     ocrete | in newer tp-farstrema, it sets the default
    16:23:15   CDeLorme | just theora, only doing video
    16:23:38   CDeLorme | I got the codecs to work (I think), no errors anyways.
    16:24:00   CDeLorme | but I don't know whether I created the TfChannel correctly?  Also, how the other end will receive the channel
    16:24:53   CDeLorme | if it auto-detects codecs and will work with theora video, I can omit that code then?
    16:25:35     ocrete | yea, tp-fs uses the default from farstream.. which should work fine on a PC type platform
    16:25:50     ocrete | unless you have some embedded stuff or somethign special in your app you shouldnt have to do anything
    16:26:04   CDeLorme | excellent, going from Sugar to Sugar, or Sugar to Fedora, so nothing "special".
    16:26:55     ocrete | you dont even need to set codec prefs in content_added
    16:27:18     ocrete | it will negotiate with the other side .. and the defaults we have prefer free codecs
    16:27:41   CDeLorme | yep, going to remove that now that I know.  We like theora because it's open-source, but auto-resolve works just fine
    16:27:54     ocrete | vp8 is open and also better
    16:27:59     ocrete | (for audio, opus is better than speex)
    16:28:38   CDeLorme | oh nice, I'll have to remember that.
    16:30:32     sjoerd | the vp8 codec configuration might need some tweaking though ? just to tune it better
    16:30:45     sjoerd | but if it's done right it works way better then theory ever did in my experience
    16:31:45   CDeLorme | ocrete: do I need a FsElementAddedNotifier with a settings file?
    16:32:54     ocrete | sadly, you still do.. and get the keyfile using fs_utils_get_default_element_properties()
    16:33:20   CDeLorme | so there are defaults I can load, without having to write one?
    16:33:39     ocrete | Farstream.utils_get_default_element_properties(element) for you ... in fs-conference-added signal handler
    16:33:51     ocrete | yea, this will pick the farstrem defaults
    16:34:14   CDeLorme | ok, so I set the notifier inside fs-conference-added with those defaults?
    16:36:01   CDeLorme | ocrete: I only see two utils_get methods, for codec and rtp_header_extension_preferences, nothing with element_properties
    16:36:34     ocrete | arg, it's because it uses a GKeyfile, I guess that's not in the bindings
    16:37:01     ocrete | there is a fs_element_added_notifier_set_default_properties() for that
    16:37:39   CDeLorme | ok, so I can use that instead?
    16:37:41   CDeLorme | awesome
    16:39:39   CDeLorme | ocrete: Did I create the TfChannel correctly?
    16:40:29     ocrete | that looks fine
    16:40:51   CDeLorme | alright, and at the other-end should it be the same, a handler to catch the call-channel and then turn it into a farstream channel?
    16:41:08     ocrete | yep, that part is symmetrical
    16:41:46     ocrete | handling received and sent calls is almost the same
    16:43:45   CDeLorme | I noticed that I was unable to run new_finish() without passing the channel, I wasn't sure which format is the correct format
    16:44:09   CDeLorme | channel.new_finish(channel, result) or Tf.Channel.new_finish(channel, result), or if it doesn't matter?
    16:46:28     ocrete | I'm not sure either what the bindings do.. whichever works ;)
    16:48:41   CDeLorme | awesome, also, is the 'src-pad-added' is for incoming streams?  If so should I have two separate gstream pipelines?
    16:48:57   CDeLorme | or is it acceptable to use a single pipeline for incoming and outgoing data?
    17:10:43     ocrete | CDeLorme: they have to be in the same pipeline
    17:11:01     ocrete | the src-pad-added is actually from the fsrtpconference element.. the same one that's used for sending
    18:11:49   CDeLorme | ocrete: [latest source](http://paste.fedoraproject.org/40618/54215313), running on two machines, when I click call it seems to work (no
                        | errors), but both my handler and observer see the same channel, and my recipient never sees any incoming channel.

Apparently, it must be on the same pipeline (according to ocrete).


---

For PIP look into [GstVideoBox](http://wiki.oz9aec.net/index.php/Gstreamer_cheat_sheet).

Once we get to a stage where adding audio is feasible, investe a [GstFunnel](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer-plugins/html/gstreamer-plugins-funnel.html), should allow us to merge audio and video streams.

If we used a pip preview we could simply modify the alpha to hide local video (since stopping it over the network without closing the call may not be possible, or at least a lot harder).

If I want to use local video I may need to use a [tee](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer-plugins/html/gstreamer-plugins-tee.html).


---

So at this point I have to finish implementing the two-way channel in a single client file.

This means each client should have a contact id entry, a button, and a drawing area.

After I get this "working", I want to expand on it and create a set of radio buttons.  These allow test video with snow and standard patterns, plus autovideosrc.  This way it will setup the service according to the selected radio button.

Then I could even test it on the XO laptops if desired.  From there I would know for certain that it would work in OVC.

Still testing with user-id entry, but I may add the contact list since copying this is getting old.

bed143950e44089a123773f0265e24c1aabae5a2@jabber.sugarlabs.org

---

Alright, so now I have my code updated and it "Should" be both listening for and able to request call channels.

Latest Source: http://paste.fedoraproject.org/40618/54215313

It is not working, and I do not yet know why.  I need to call it a night though.

Going to post it in channel and state the problems:

- Both observer and handler see the same channel, Way to stop that?
- Recipient running same code does not catch any incoming channels
- No local video displayed (probably because the recipient never responds)
