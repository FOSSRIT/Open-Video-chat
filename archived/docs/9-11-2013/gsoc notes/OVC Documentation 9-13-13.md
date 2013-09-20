
# OVC Documentation 9-13-13

Since sugar3 does not use TelepathyGLib and depends on the former telepathy import the channels and contacts supplies are incompatible.

Therefore we need a way to grab information from the sugar "buddy" (contact) objects and establish a new channel.


---

Todays plans are to:

- Debug Chat System
- Test Cross Platform (Sugar to Fedora)
- Begin GStreamer Implementation

I will temporarily enable the contacts list in the sugar edition to test cross platform, until I have time to test Sugar's telepathy to TelepathyGLib conversion.

It should be a simple matter of extracting the contact's id and sending a fresh connection request.


---

Sugarlabs jabber server is down this morning so I am going to continue working on the GStreamer Pipeline demo to be implemented later.

Mapping out the pipeline:

Input from video first.

Tee output to preview window.

Finally second output to Call Stream.

_Figuring out how to attach GStreamer to a CallStream may prove channeling._

TelepathyGLib has a StreamTube example in which they use the python Gio library to attach a generic data object.  This might be something I have to investigate.

There is a [giosink](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-giosink.html) and [giostreamsink](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-giostreamsink.html) elements I might be able to use.

I can also checkout the old OVC code to see how they used to do it.  As I recall they used the IP Address to send it over the network directly, so that probably isn't my goal.

Local chain of components will have:

- autovideosrc
- theoraenc
- tee
- giostreamsink

There are more but I don't yet know which ones I will be using.

If we want to be able to stop video and audio independently, we will need a way to notify the pipeline to temporarily halt if the video and audio are merged.

I will have to checkout the methods needed to dynamically change settings of the pipeline.


http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/chapter-pads.html
http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/chapter-pads.html#section-pads-dynamic
http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-data-spoof.html
http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-dynamic-pipelines.html
http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-dynamic-pipelines.html#section-dynamic-changing

