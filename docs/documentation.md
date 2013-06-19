
# Documentation
### 5/19/2013

UI Design and objects are undergoing changes, check the date of this document against the file git log for reference.


---

### ovc.py

Primary Executable; contains the class referenced by activity.info for execution.


#### `establish_activity_sharing`

Handles setup for sharing and joining conditionally according to whether the activity has been shared or joined.


#### `share_activity_internals`

Creates the network stack and establishes connection between components.


#### `get_buddy`

Use Sugar components from the activity and Telepathy components from the Network Stack to derive a buddy name.


#### `can_close`

Handles deconstruction of objects in-use (if needed).

_Will be used to notify other users of disconnection._


#### `alert`

Display alert message.

_This may not be needed, so some tests should be performed._


#### `cancel_alert`

Close the displayed alert


#### `write_file`

Save chat log to journal entry for restoring session.

_Needs additional testing._


#### `read_file`

Restore previous session chat log.


---

### gui.py

UI extending Sugar Activity and using Gtk3.

Ideally if we can separate the Network Stack and GStreamer Stack from Sugar dependencies, we can make them portable, pushing the only need for changes off to the gui.

Still requires some serious cleanup to reduce length and verbosity where able.


#### `set_network_stack`

Connect network_stack for handling.


#### `set_gstreamer_stack`

Connect gst_stack for handling.


#### `build_video`

Prepare video GUI components and container.


#### `build_chat`

Prepare chat GUI components and container.


#### `build_toolbar`

Build Sugar Toolbar buttons and tie toggles to methods.


#### `toggle_video`

Toggle Incoming Video.


#### `toggle_audio`

Toggle Audio (incoming/outgoing?)


#### `toolbar_toggle_preview_visibility`

Toggle button display and label text, connects to toggle_preview_visibility method.


#### `enable_net_options`

Enable Network processes and related toggles.

Called when connected.


#### `disable_net_options`

Disable Network processes and related toggles.

Called if connection lost?


#### `enable_gst_options`

Enable GStreamer components.


#### `disable_gst_options`

Disable GStreamer components.


#### `toggle_preview_visibility`

Toggle video preview, notifies GStreamer Stack to stop using webcam and notifies any connected users to cease listening for theirs.


#### `toggle_incoming_visibility`

Turn off incoming video.

Should notify connected user over network stack to cease their output.


#### `render_preview`

Tie GtkDrawingArea Gdk window id to GStreamer Stack output.


#### `render_incoming`

Tie GtkDrawingArea Gdk window id to GStreamer Stack output.


#### `set_preview_size`

Sets the preview GtkDrawingArea size according dynamically.


#### `set_incoming_size`

Set incoming video GtkDrawingArea size dynamically.


#### `toggle_preview_size`

Adjust dynamic preview sizes.


#### `resized`

Handle resize event (does not apply to Sugar and can probably be removed).


#### `get_history`

Retreives chat log from stored history in journal session, if able.


#### `chat_write_line`

Writes a custom message to chat history (such as system messages).


#### `receive_message`

Handles message received over chat dialog.


#### `send_message`

Sends message over network.


#### `buddy_joined`

Posts buddy-joined message.


#### `buddy_left`

Posts buddy-left message.

_Sugar does not appear to be working._


#### `connect_incoming_movie`

_Currently not in use._


#### `disconnect_incoming_movie`

_Currently not in use._


#### `force_redraw`

Method tied to component used to resolve formerly logged video frame locking problem.


---

### gst_stack.py

GStreamer Stack, handles video (and soon audio) protocols and streaming.

Currently working on 1.0 and 0.10 cross-compatible code.


#### `build_working_preview`

_Temporary method to test preview video._


#### `on_message`

Global on_message handler tied to `build_working_preview`.


#### `draw_preview`

Temporary method to tie video output to a supplied window id.


#### `set_incoming_window`

**Documentation Incomplete**


#### `toggle_video_state`

**Documentation Incomplete**


#### `toggle_audio_state`

**Documentation Incomplete**


#### `build_preview`

**Documentation Incomplete**


#### `build_preview` > `on_message`

**Documentation Incomplete**


#### `build_preview` >  `on_sync_message`

**Documentation Incomplete**


#### `build_outgoing_pipeline`

**Documentation Incomplete**


#### `build_incoming_pipeline`

**Documentation Incomplete**


#### `build_incoming_pipeline` > `on_message`

**Documentation Incomplete**


#### `build_incoming_pipeline` > `on_sync_message`

**Documentation Incomplete**


#### `start_stop_outgoing_pipeline`

**Documentation Incomplete**


#### `start_stop_incoming_pipeline`

**Documentation Incomplete**


---

### gst_bins.py

Simple Bin Class Storage used to managed entire constructed streams and grouped by type.

- Incoming Video
- Incoming Audio
- Outgoing Video
- Outgoing Audio

Implementation is still incomplete and experimental.


---

### network_stack.py

Handles network activity.

Attempts have been made to extrapolate Sugar dependencies from the code, resulting in a smaller and lighter weight stack.


#### `setup`

Setup network stack and connect to activity without directly referencing or depending on Sugar design.


#### `close`

Close the Telepathy channels.

_Should first send a message to connected users regarding disconnection for graceful shutdown._


#### `connect`

Establishes Telepathy Channel for communication.


#### `send_message`

Send chat message over Telepathy Channel.


#### `receive_message`

Handle received messages over channel.

_Possibility of using parsed string command format would turn this into a much more complex utility method._


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


#### Latest Reference Materials

The following list of links are reference materials and reading related to the code.

Most of the code was written using these links and other Sugar activities as reference code.

Keep in mind that due to Introspection libraries many of the docs these days are for C specifically, and some degree of a learning curve is involved with identifying the API according to your language of choice (in our case python).


- [Gtk3 Docs](https://developer.gnome.org/gtk3/3.0/)
- [Gtk3 Python Tutorial](http://python-gtk-3-tutorial.readthedocs.org/en/latest/)
- [bpython (terminal introspection autocompletion)](http://bpython-interpreter.org/)

- [Telepathy Docs](http://telepathy.freedesktop.org/doc/book/index.html)
- [Telepathy DBus](http://telepathy.freedesktop.org/doc/book/sect.basics.dbus.html)

- [GStreamer Official Docs](http://gstreamer.freedesktop.org/documentation/)
- [GStreamer Docs](https://developer.gnome.org/platform-overview/stable/gstreamer)

- [GObject Docs](https://developer.gnome.org/gobject/stable/)
- [GLib Docs](https://developer.gnome.org/glib/stable/)

- [distutils](http://docs.python.org/2/library/distutils.html)
- [Distributable](http://guide.python-distribute.org/)
- [C setuputils](http://robotics.usc.edu/~ampereir/wordpress/?p=202)
- [Setup Script](http://docs.python.org/2/distutils/setupscript.html#installing-scripts)
- [One Click Distributable](http://stackoverflow.com/questions/5359581/want-to-use-distutils-to-install-my-python-app-with-a-one-click-launcher-file)

- [Developer Blog](http://cxd4280.wordpress.com)
