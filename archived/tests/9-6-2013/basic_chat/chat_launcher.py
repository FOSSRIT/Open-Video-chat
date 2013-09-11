#!/usr/bin/env python

# Imports
from gi.repository import Gtk
from chat import Chat


# Create a window to hold the chat system
window = Gtk.Window()
window.set_default_size(800, 600)
window.add(Chat())
window.connect('delete-event', Gtk.main_quit)
window.show()
Gtk.main()
