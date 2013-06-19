==========
OVC Design
==========

Project Goals
=============
Open Video Chat is a video communication program being developed in the Center for Student Innovation sponsored by PEN International.  The primary goal of this project is to develop a video chat program ( OVC ) for the XO laptop produced by SugarLabs.  This program must provide fast enough frame rate so that deaf and hard of hearing students can communicate using sign language.  This frame rate should be at least 12 FPS.  An ambitious long term goal is to port the software to other platforms and communicate with other communication mediums.

Program Flow
============
The main class is OpenVideoChatActivity.  This extends the sugar activity and acts as the main canvas for the gui.  It loads up the gui file which builds the menus and displays. It also builds a network stack instance and connects the sugar's shared and join calls to the network.

This network stack is used for the text chat as well as passing ip addresses to the ohter machine. It uses the tube speak class to act as its dbus protocol.

When a user joins the activity, they announce themselves over the network connection. Then the other computer responds to the announce with their ip address.  Once the joining system gets the other's ip, it sends its ip back and starts to stream its video using udp to the other machine.


Class Breakdown
===============
ovc.py
------
Main Program.  This class  connects the gui, gstreamer, and the network.

gui.py
------
This class handles the graphical user interface.  It builds the menus, toolbars, and the main display.

network_stack.py
----------------
Empty at this time. Will be used to generalize the Sugar network stack.

sugar_network_stack.py
----------------------
Controls the Dbus tubes.  Requests all tubes and filters out ones that are not used by this program.

tube_speak.py
-------------
standard Dbus ExportedGObject 	

gst_stack.py
------------
This is the gstreamer stack.  This file builds the gstreamer pipeline that will be used by the activity.
