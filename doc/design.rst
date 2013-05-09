==========
OVC Design
==========

Project Goals
=============
Open Video Chat is a video communication program being developed in the Center for Student Innovation sponsored by PEN International.  The primary goal of this project is to develop a video chat program ( OVC ) for the XO laptop produced by SugarLabs.  This program must provide fast enough frame rate so that deaf and hard of hearing students can communicate using sign language.  This frame rate should be at least 12 FPS.  An ambitious long term goal is to port the software to other platforms and communicate with other communication mediums.

Program Flow
============
The main class, ovc, sets up the components of OpenVideoChat: the GUI, the Network Stack, and GStreamer.

The GUI builds the menus and displays using GTK3.

This network stack is used for the chat service overall.

GStreamer operations are broken in to multiple bins for organization. Outbound video is taken, tee'd so the local user can see their own video preview, and the other end is sent over the network. The inbound part simply takes the video and displays it.

When the system starts up, it starts a listener for anyone joining the shared activity (over telepathy and the accounts system). When the activity is marked as shared, sugar creates what is essentially a "joined listener" to start communication.


Class Breakdown
===============
ovc.py
------
Main Program.  This class connects the gui, gstreamer, and the network.

gui.py
------
This class handles the graphical user interface.  It builds the menus, toolbars, and the main display.

network_stack.py
----------------
Handles networking, using Telepathy. Presence is used more as an accounts system, rather than relying on Presence and tubes separately.

gst_stack.py
------------
This is the GStreamer stack.  This file builds the gstreamer pipeline that will be used by the activity.

gst_bins.py
-----------
Handles the grouping of GStreamer elements.

test_ovc.py
-----------
A simple testing script for OVC.
