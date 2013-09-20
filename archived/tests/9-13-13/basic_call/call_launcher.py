#!/usr/bin/env python

# Imports
from gi.repository import Gtk, Gst
from call import Call

# Create a Window to hold our chat system, and initialize our GStreamer Elements
Gst.is_initialized() or Gst.init(None)
window = Gtk.Window()
window.set_default_size(800, 600)
window.add(Call())
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
