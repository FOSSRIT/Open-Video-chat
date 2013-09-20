
# Farstream Documentation

Reference Links:

- [Repository](http://cgit.collabora.com/git/freedesktop.org-mirror/telepathy/telepathy-farstream.git/)
- [Farstream Docs](http://www.freedesktop.org/software/farstream/apidoc/farstream/)
- [TelepathyFarstream Docs](http://telepathy.freedesktop.org/doc/telepathy-farstream/)
- [GLib Docs](https://developer.gnome.org/glib/unstable/glib-The-Main-Event-Loop.html)

The Farstream Library allows you to begin a GStreamer Pipeline, and connect it to Telepathy.

The [TelepathyFarstream Channel](http://telepathy.freedesktop.org/doc/telepathy-farstream/TfChannel.html) wraps a [Telepathy CallChannel](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-call-channel.html).

The libraries can be imported to python with:

    from gi.repository import Farstream
    from gi.repository import TelepathyFarstream
    from gi.repository import GLib


The GLib library is necessary in combination with the GStreamer library to listen to the pipeline bus by setting a priority (although supposedly you could just pass 0 to bas_watch first argument).


I won't have enough time to cleanup these notes as much as the other sections, so this area may be left in disarray to some extent.  I will do my best to keep things readable.


