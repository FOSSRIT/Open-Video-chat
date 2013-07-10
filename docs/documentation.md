
# Documentation
### 5/19/2013

UI Design and objects are undergoing changes, check the date of this document against the file git log for reference.

---

## File Summary

- launcher
- setup.py
- ovc.py
- sugar_ovc.py
- toolbar.py
- sugar_toolbar.py
- dialog.py
- gui.py
- network_stack.py
- gst_stack.py
- gst_bins.py

Theree are also small & large icons, created for cross-platform consistency.


## What each file does

The launcher is for cross-platform execution, and the setup.py is for sugar.

A top-level setup.py will be modified to install the cross-platform implementation.

There are two ovc and toolbar files to handle sugar dependencies.  Ideally we wish to keep sugar abstracted from the gui, network stack, and gstreamer stack.

At the moment both the network stack and gst files are incomplete and non-functional.

The toolbars both use the new icons for cross-platform consistency.


## A Note on Cross Platform

If patches are made to the code in the future, please keep the sugar specific components inside the sugar prefixed files in order to retain layered abstraction.

---


### Verbose File Descriptions


#### ovc.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This file is the core of the system and acts as a medium between the components.

**References:**

- []()


#### sugar_ovc.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This file is the core for sugar and acts as a medium between the components, and the abstraction for sugar specific requirements.

**References:**

- []()


#### toolbar.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This is the cross-platform toolbar without sugar specific components.

It uses the small icon sizes by default.

**References:**

- []()


#### sugar_toolbar.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This toolbar uses the sugar components for activity icon and closing.

It uses the large icons by default.

**References:**

- []()


#### gui.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This is a multi-platform compatible GUI that has no sugar dependencies and can therefore exist on sugar and on other platforms.

It uses Gtk3.

**References:**

- [Gtk3 Docs](https://developer.gnome.org/gtk3/3.0/)
- [Gtk3 Python Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/)
- [GObject Docs](https://developer.gnome.org/gobject/stable/)
- [GLib Docs](https://developer.gnome.org/glib/stable/)


#### network_stack.py


**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

Network Stack, details incomplete.

**References:**

- [Telepathy Docs](http://telepathy.freedesktop.org/doc/book/index.html)
- [Telepathy DBus](http://telepathy.freedesktop.org/doc/book/sect.basics.dbus.html)
- [Gajim Jabber Client](http://gajim.org/)


#### gst_stack.py

**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

GStreamer Stack, details incomplete.

**References:**

- [GStreamer Official Docs](http://gstreamer.freedesktop.org/documentation/)
- [GStreamer Docs](https://developer.gnome.org/platform-overview/stable/gstreamer)


#### gst_bins.py


**Imports:**

-

**Depends On:**

-

**Classes>Methods:**

-

This file manages bins used to exert simplified control and separate GStreamer components.

Keeping components separated can increase bandwidth consumption but reduces CPU requirements for parsing streams.  This may prove to be a requirement for low-powered machines, like the XO laptops.










---

#### Sugar Structure & Installation Notes

Sugar environment stores the activity information and icon inside /activity.

When installed the entire OpenVideoChat.activity folder is copied over.

Build and Install is handled by the setup.py script.  The standard process for installation is:

    ./setup.py genpot
    ./setup.py build
    ./setup.py dist_xo

Manual installation command:

    sugar-install-build dist_xo/OpenVideoChat.xo

**Note: The sugar setup.py build & dist_xo processes use the git file history when copying the files, and will throw an error if you delete a file without notifying git.  It may also skip files in the directory that have not been added to the git repository.**



#### Generic / All Purpose References

The following list of links are reference materials and reading related to the code.

Most of the code was written using these links and other Sugar activities as reference code.

Keep in mind that due to Introspection libraries many of the docs these days are for C specifically, and some degree of a learning curve is involved with identifying the API according to your language of choice (in our case python).


- [bpython (terminal introspection autocompletion)](http://bpython-interpreter.org/)
- [Developer Blog](http://cxd4280.wordpress.com)
- [distutils](http://docs.python.org/2/library/distutils.html)
- [Distributable](http://guide.python-distribute.org/)
- [C setuputils](http://robotics.usc.edu/~ampereir/wordpress/?p=202)
- [Setup Script](http://docs.python.org/2/distutils/setupscript.html#installing-scripts)
- [One Click Distributable](http://stackoverflow.com/questions/5359581/want-to-use-distutils-to-install-my-python-app-with-a-one-click-launcher-file)







---

**Incomplete Misplaced:**

    # Gui extends [GtkGrid](https://developer.gnome.org/gtk3/3.0/GtkGrid.html)
    # Toolbar extends [GtkExpander](https://developer.gnome.org/gtk3/3.0/GtkExpander.html)
    # OpenVideoChat Cross Platform extends [GtkWindow](https://developer.gnome.org/gtk3/3.0/GtkWindow.html)
    # Create [GtkDrawingArea](https://developer.gnome.org/gtk3/3.0/GtkDrawingArea.html) & [Modify Background](https://developer.gnome.org/gtk3/3.0/gtk-question-index.html)

- [Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/objects.html)
- [GtkGrid](https://developer.gnome.org/gtk3/3.4/GtkGrid.html)
- [Sugar Alerts](http://wiki.sugarlabs.org/go/Development_Team/Almanac/sugar.graphics.alert)
- [Outdated Source](https://github.com/PabloCastellano/telepathy-python)
