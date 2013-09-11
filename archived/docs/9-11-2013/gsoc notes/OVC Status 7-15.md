
So there was a new gi repository Telepathy import afterall:

- http://telepathy.freedesktop.org/doc/telepathy-glib/
- http://stackoverflow.com/questions/7671763/error-setting-status-to-empathy-with-dbus
- http://blog.tomeuvizoso.net/2010/05/using-telepathy-glib-in-python-through.html


Contact `tch` & `rgs` regarding Gtk3 and dbus questions.

Contacted jlew and trose regarding FPS for GStreamer on Xo's.

---

Emailed jlew: Jlew.blackout@gmail.com

    Hello,

    I am working with FOSS@RIT on OpenVideoChat to try and bring it back to life.  I was hoping to pick your brain regarding GStreamer.

    GStreamer 1.0 is now available and I was testing framerates on a 1.5 model XO.  The processor can't seem to keep up when I implement a videoscale to tyhe stack, and I was wondering how you managed acceptable framerates with a local and network stream.

    I would appreciate any information you can supply me on this.

    Thank you,

    Casey DeLorme

---

So, it only took me a week and a half of research and reading to find out that gi.repository had a TelepathyGLib extension with modern python bindings needed for my project.


Some new Source Code:

- http://telepathy.freedesktop.org/doc/book/sect.services.glib.html
- http://telepathy.freedesktop.org/doc/book/appendix.source-code.glib_mc5_observer.example-observer.c.html
- http://telepathy.freedesktop.org/doc/book/source-code.html



To create an account manager without any reference material, this is the short and sweet list of references you'll probably go through:

http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-account-manager.html
http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-account-manager.html#tp-account-manager-dup
http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-account-manager.html#tp-account-manager-new
http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-dbus.html#tp-dbus-daemon-dup
http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-dbus.html#tp-dbus-daemon-new
http://dbus.freedesktop.org/doc/dbus-glib/
http://dbus.freedesktop.org/doc/dbus-glib/dbus-glib-DBusGConnection.html
http://dbus.freedesktop.org/doc/dbus-glib/ch02.html
https://developer.gnome.org/gobject/stable/
https://developer.gnome.org/gobject/stable/gobject-The-Base-Object-Type.html
https://developer.gnome.org/gobject/stable/gobject-Type-Information.html#GType
https://developer.gnome.org/glib/stable/
https://developer.gnome.org/glib/stable/glib-Error-Reporting.html
http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-connection-manager.html

Easy right?  Should barely take a few minutes to understand.
Technically it says you should use "dup" in most cases, but it never explains why, or what it does as opposed to "new".  Does it create a new bus, how does it automatically resolve the DBus information, and what if you need more than one telepathy channel?


In any event, getting an Account Manager can be done with dup, or if with new then dup the DBusDaemon and pass as an argument to new.  Again, I don't know what difference either makes, or if having control over anything underneath the account manager is at all necessary.

Despite having an account manager I have no listed accounts.  I need to review where the stack starts in the older docs.

---

