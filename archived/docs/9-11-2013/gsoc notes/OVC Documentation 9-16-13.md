
# OVC Documentation 9-16-13

This is intended to be the pencils down date, however the project I am working on is incomplete, so I'm going to put in a few more days of extra cycles.

On my list of incomplete tasks:

- Getting a local video demo setup
- Finishing GStreamer documentation for our project
- Getting a demo with a Call Channel working
- Identifying how to connect Farstream to GStreamer
- Extracting a GStreamer pipeline from a Telepathy Call Channel

So, that's a lot of work, and I don't expect that I will be able to finish it with only 4 extra days, but I'm going to try.


---

I started by asking in #telepathy, and got several responses on the subject:

    14:29:43 CDeLorme | smcv: Any idea how to connect a stream to a call channel?  I saw an example in the source with tube stream but nothing for a call yet.
    14:30:06     smcv | StreamTube and Call streams are not the same thing
    14:30:12     smcv | a StreamTube is TCP-over-IM
    14:30:19      <-- | aalex (aalex@pasanda.collabora.co.uk) has quit (Disconnected by services)
    14:30:27      --> | aalex (aalex@pasanda.collabora.co.uk) has joined #telepathy
    14:30:28     smcv | a Call is audio/video (using UDP behind the scenes)
    14:30:36     smcv | CDeLorme: ^
    14:30:43     smcv | look at Empathy or kde-call
    14:31:00     smcv | (or, preferably, use one of those rather than reimplementing it)
    14:31:09 CDeLorme | Building for Sugar
    14:31:22 CDeLorme | Was going to attach GStreamer to a Call
    14:31:33     smcv | telepathy-farstream is how you do that
    14:31:47     smcv | you might have to write C to do so in a reliable way, though
    14:32:09 CDeLorme | Yeah, except I haven't seen any examples that were readable and used TelepathyGLib
    14:32:11     smcv | audio/video calling is actually quite complicated (understatement of the day)
    14:33:03 CDeLorme | I started reading the C code for the Call Example, but I can't make heads or tails of how the stream is setup...
    14:33:40     smcv | the Call example CM is the connection manager side, which won't help you much
    14:33:50     smcv | it doesn't actually stream anything, it just pretends to
    14:33:58     smcv | and it's the (fake) protocol implementation, not the UI
    14:34:12     smcv | you want the UI side, for which the examples are, er, Empathy and kde-call
    14:35:26 CDeLorme | any idea what it uses for the video?  GStreamer, or something different?
    14:36:04     smcv | Empathy and kde-call both use telepathy-farstream, which is how you hook up Telepathy calls to GStreamer in a call UI
    14:36:30 CDeLorme | hmm, where can I find the latest telepathy-farstream source?
    14:36:50     smcv | freedesktop.org git, the same place as the rest of Telepathy
    14:37:03 CDeLorme | I saw over a dozen repositories with the same name, wasn't sure which to grab
    14:37:46     smcv | the ones in telepathy/telepathy-* are "the real version"
    14:37:58     smcv | the ones in ~someone/telepathy-* are various people's unreviewed branches
    14:38:23 CDeLorme | ah alright, I will grab it and take another look
    14:42:18     smcv | CDeLorme: for your information, http://cgit.freedesktop.org/telepathy/telepathy-farstream/tree/examples/python/callhandler.py is a trap - it
                      | uses telepathy-python, which is old and not very good
    14:42:21 CDeLorme | smcv: only seeing "import telepathy*" not the glib library, does farstream use the older telepathy libraries?
    14:42:33        * | smcv opens a bug
    14:42:42   ocrete | CDeLorme: which farstream version ?
    14:43:02   ocrete | oh we did that, we should fix that
    14:43:05 CDeLorme | I just downloaded the telepathy/telepathy-farstream git repo
    14:43:32     smcv | ocrete: I'll cc you
    14:43:32 CDeLorme | and I am noticing all the python examples import telepathy.constants/interfaces etc
    14:43:51     smcv | oh you're the default assignee anyway. nm
    14:44:26     smcv | https://bugs.freedesktop.org/show_bug.cgi?id=69435
    14:46:12     smcv | CDeLorme: adapting callhandler.py to be a TelepathyGLib.SimpleHandler shouldn't be rocket science - it'd mostly be code deletion?
    14:46:34     smcv | you'd have to make callchannel.py use TelepathyGLib.CallChannel too
    14:46:48     smcv | and probably upgrade to gstreamer 1.0
    14:46:51     smcv | ...
    14:46:58     smcv | not the world's most exemplary examples
    14:48:20      <-- | scummos (~sven@p4FDCF875.dip0.t-ipconnect.de) has quit (Ping timeout: 245 seconds)
    14:50:36 CDeLorme | yeah I am not sure how to translate from the old to the new way, especially since I haven't really learned the new way yet
    14:51:06     smcv | examples/client/python/dialler.py in telepathy-glib supersedes callui.py in telepathy-farstream
    14:51:11     smcv | so that's a start
    14:52:21      <-- | dvratil (~Dan@ip4-95-82-187-209.cust.nbox.cz) has quit (Quit: I quit!)
    14:56:01 CDeLorme | so, the callui or dialler are the front-end to the handler?
    14:56:21     smcv | dialler.py/callui.py just says "start a call"
    14:56:52     smcv | the handler is what actually "runs" the call once it's going - does the streaming (using tp-farstream and Gst)
    14:57:13     smcv | in Empathy, the equivalent of dialler.py is part of the contact list process
    14:57:41     smcv | and the handler is its own executable ("empathy-call")
    14:58:11     smcv | you can also initiate calls via gnome-contacts, which, again, does something similar to dialler.py
    14:59:34     smcv | (dialler.py also looks through running processes for possible "preferred handlers" - in real life you'd usually hard-code the name of your
                      | own Handler)
    14:59:43 CDeLorme | hmm, now sure where the call is initiated from, still reading the dialler code
    15:00:24 CDeLorme | Gtk.Application run method probably starts everything I take it?

So, once again it was suggested that I use farstream and directed to the latest source.

Thinking perhaps I had downloaded the wrong one previously I grabbed it again, and explained that none of the python examples used the modern TelepathyGLib or pygi release of Farstream.

They said translating it should be a relatively easy task, but that they clearly hadn't updated them in quite some time.

I am still **assuming** that the pygi release of Farstream is the one I should be using with TelepathyGLib but I have no way of knowing for sure without running tests sadly.

Going further into conversation I was told to start with callui from farstream and dialler from telepathyglib repositories.  However, neither use farstream, they only demonstrate creating a call channel, which I though was very similar to the text channel procedure.

So, I am still left with questions on whether call channels are bi-directional, and how to connect and extract streams from them.

ocreate explained that Farstream is really just a GStreamer element, which bridges the gap to TelepathyGLib (eg. a sink pad).  He suggested that I review the callhandler.py and callchannel.py files, despite having dated code they are the processes by which I would use a call channel.

This finally begins to make sense, except now I'm left with yet again more questions on how TelepathyGLib Call Channels work.


---

With that discussion out of the way I proceeded to work at setting up a GStreamer pipeline.

I got quite a ways, then realized I was having trouble getting my webcam working on Gnome3 on Fedora.

To confirm whether this was a fedora issue I booted a Debian Wheezy VM to run the same test.

On this platform I proceeded to debug the GStreamer issues.


---

Also checked package availability, while GStreamer 1.0 is backported in Debian Wheezy, gir1.2-farstream-0.2 is not available until Debian Jessie, which may not release for another two years.

Ubuntu 13 (raring) and onward _should_ have the right packages to run this software.

