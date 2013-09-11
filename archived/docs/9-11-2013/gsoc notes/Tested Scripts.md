
## Summary

- Continue to work on Gtk3 Cross Platform Implementation Tests


- Reading:
    - Telepathy Channels, Streams, DBus
    - GStreamer
    - Gtk/GObject Initialization

- Grab Dia Screens for Wire Framing
    - Remake Wireframes in dia


- WPA Supplicant research (want to get it working)

- Continue to hash out WIP Ideas


- Complete Instructions Cleanup
    - Windows Setup
    - Comm Setup
        - Backup Files
    - NGinx Setup
        - Backup Files
    - IPFire Setup
        - Backup Data/Files/Lists

- Research and Test Customized Debian Installer
    - Options:
        - Live
        - Xen
        - NGinx
        - Comm
    - Fully customized iso with:
        - Additional Packages
        - Latest Kernel & Customizations
        - Post Install Scripts according to selection
    - Live Build Ideas:
        - Retain State via writable sub-file
    - Single Final ISO with EFI & traditional compatibility

---


I can then clone the FOSSRIT OVC and Terminal activity, and begin testing!


---

FOSSRIT OVC - Create Dia Files:

    touch docs/diagrams/wire_frames.dia
    touch docs/diagrams/use_cases.dia
    touch docs/diagrams/activity_diagrams.dia
    touch docs/diagrams/sequence_diagrams.dia


---

Seek free creative commons licensed sounds on "freesound" website.

Can potentially set unused keys to play a sound in Linux, would be funny.


---

WPA Supplicant Data: (http://fedoraforum.org/forum/showthread.php?t=100788)

Exists in `/etc/wpa_supplicant/wpa_supplicant.conf`

We need to modify according to RIT components.

A `sudo echo >>` might do the trick



### WIP Ideas

Reading on Telepathy, for alternative Channel communication.

One idea is to use the channel for a text based command system.

Examples:

- chat: <message>
- gstreamer: <action>
- network: <action>

This would be easy to parse and use, but not exactly idea if Telepathy has alternative channels for sending commands through.

This or any other implementation could be used to send a "terminate" action from can_close(), and allow us to define GStreamer operations.

DBus may be an alternative, but the former tube_speak.py was outdated, and supposedly no-longer used by GStreamer 1.0.


Confirmed that GObject/GLib no longer needs to run threads_init() and that is handled automatically.

---

GUI Plans for testing:

- Tie escape key to exit
- Tie delete-event to exit
    window.connect("delete-event", Gtk.main_quit)


Let's just create a basic window and get it to launch in my Debian Live environment.

Key Press Event
Get escape key working.


Test check-resize event.

Awesome, realized my mistake was editing a different file than I was executing.  Duh.

key-press-event working just fine on global.
check-resize also works, IT ALSO triggers when after realize is fired, meaning it can be used in the sugar version too!

Input abstraction to handle ctrl and shift and alt keys being held?

Ah, need to use key-release-event, also there might be a way to check the mask from Gdk:
https://developer.gnome.org/gdk3/stable/gdk3-Events.html
https://developer.gnome.org/gdk3/stable/

Gdk.Event.state.CONTROL_MASK
Gdk.Event.state.SHIFT_MASK

Sweet!

if Gdk.Event.get_state().value_names['GDK_SHIFT_MASK']:
    Shift is being held!


Test Script:

    #!/usr/bin/python2.7

    # External Imports
    from gi.repository import Gtk

    def test(window, event):
    #       print event.get_state().value_names
    #       print event.keyval

            if event.keyval == 116 and "GDK_CONTROL_MASK" in event.get_state().value_names:
                    print "New Tab!"

    #       if event.keyval == 116 and "GDK_CONTROL_MASK" in event.get_state().value_names:
    #               print "Ctrl"

            if event.keyval == 65307:
                    Gtk.main_quit()

    #def resized(window):
    #       print "Resized!"

    # Defacto Test
    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.connect("key-press-event", test)
    #win.connect("check-resize", resized)
    win.show_all()
    Gtk.main()

---

Terminal Activity Additional Code (approx):

    from gi.repository import Gdk


    def catch_hotkeys(self, event):


        if event.keyval == Gdk.KEY_t and "GDK_CONTROL_MASK" in event.get_state().value_names:
            print "New Tab!"

        # Control + Tab
        if event.keyval == Gdk.KEY_Tab and "GDK_CONTROL_MASK" in event.get_state().value_names:
            print "Next Tab"

        # Control + Shift + Tab
        if event.keyval == Gdk.KEY_Tab and "GDK_CONTROL_MASK" in event.get_state().value_names and "GDK_SHIFT_MASK" in event.get_state().value_names:
            print "Previous Tab"

        # Alt+#
        if "GDK_MOD1_MASK" in event.get_state().value_names and event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_0:
            # Handle Numeric Matches (probably an if statement per combination)


[Repository](http://git.sugarlabs.org/projects/terminal)


---

For the fully customized debian installer iso I can look into:

http://wiki.debian.org/Simple-CDD

Apparently it can do a number of cool things:

- Pre-seeding file (answer file)
- Additional packages
- Register post-install executable scripts
- Multiple Profiles?


Otherwise my option is to go through madness:
http://wiki.debian.org/DebianCustomCD


So, ideally I want to create several boot options for my configuration.


Packages for Debian Live CD creation:

http://live.debian.net/

So maybe I can create my custom iso and add live execution to it.
If modified appropriately I can make it so the live install can save state.


