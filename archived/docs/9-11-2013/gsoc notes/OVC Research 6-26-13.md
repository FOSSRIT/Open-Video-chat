
# Open Video Chat
## DBUS & Telepathy Research
### 6-26-2013


Revised Network Design will be made up of three channels or "Tubes":

- Channel for Messages
- Channel for Commands / DBUS
- Channel for Streams


The channel for messages already exists in the latest version, but some modifications may be made to simplify it.

The DBUS commands afford the most discrete custom message sending process.

Stream channels will eliminate the need for shared IP's and extrapolate network handling to Telepathy.


---

A command from DBUS tube should be sent to close the connection on-exit.




---

**References:**


- [Creating Tubes](http://telepathy.freedesktop.org/doc/book/sect.tubes.setup.html)
- [DBus Implementation](http://telepathy.freedesktop.org/doc/book/sect.services.python.html)


DBUS:

[Telepathy DBUS Specification](http://telepathy.freedesktop.org/spec/)
[Telepathy Using DBUS](http://telepathy.freedesktop.org/doc/book/sect.basics.dbus.html)


Tubes:

[Telepathy Tubes](http://telepathy.freedesktop.org/doc/book/chapter.tubes.html)
[Telepathy StreamTube](http://telepathy.freedesktop.org/spec/Channel_Type_Stream_Tube.html)
[Telepathy DBUSTube](http://telepathy.freedesktop.org/spec/Channel_Type_DBus_Tube.html)


Source:

[Old Github](https://github.com/FOSSRIT/Open-Video-chat/tree/051a4a544122748112277665bb52063f87274136/OpenVideoChat.activity)

