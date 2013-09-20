
# OVC Documentation 9-17-13

Yesterday I figured out the GStreamer stack, and was nearly finished setting it up.

I found some quirks to add to the gstreamer docs under tips & tricks (I also need to figure out how to modify a running pipeline).


Here is my list of things to finish today:

- Getting local video
- Setting up a call channel
- Extracting the channel with farstream to hook up GStreamer
- Testing networked video

---

Package Info:

- [gir list](http://packages.debian.org/search?searchon=contents&keywords=gir&mode=path&suite=testing&arch=i386)

To get GStreamer 1.0 working on Debian I had to add debian backports and install various GStreamer packages.

In the list above I had to grab GstVideo and Gst for pygi (girepository).


The GstVideoOverlay is part of the "Good Plugins" package, and requires GstVideo to be imported for the `set_window_handle` method to exist on the ximagesink element.

I managed to get local video working, next I can try to get the passed webcam working.

Well, webcam isn't passing so I had to test on an XO laptop, and local video worked.  So, the next step is to see if we can enhance the system with alternative caps.

Then change caps at runtime.

We can finalize the GStreamer documentation, then move onto creating a call channel.

Excellent, got changing caps at run-time and finished GStreamer Documentation.


---

Now to setup a call channel.

The source code to review is mixed in telepathyglib's `dialler.py`, and telepart-farstream's `callhandler.py` and `callchannel.py` files.  The farstream code is three versions ago out of date, while the dialler is new but doesn't show modern methods of connecting farstream.

I will be using the pygi Farstream library: `from gi.repository import Farstream`.

Goals:

- sender & receiver code (for this test)
- Call Channel Established
- Signals to setup GStreamer
- Attach GStreamer
- Playback on client

