==========
OVC Design
==========

Project Goals
=============
Open Video Chat is a video communication program being developed in the Center for Student Innovation sponsored by PEN International.  The primary goal of this project is to develop a video chat program ( OVC ) for the XO laptop produced by SugarLabs.  This program must provide fast enough frame rate so that deaf and hard of hearing students can communicate using sign language.  This frame rate should be at least 12 FPS.  An ambitious long term goal is to port the software to other platforms and communicate with other communication mediums.

Program Flow
============
The main class is OpenVideoChatActivity.  This extends the sugar activity and acts as the main canvas for the gui.  It loads up the gui file which builds the menus and displays. It also builds a network stack instance and connects the sugar's shared and join calls to the network.

This network stack will set up a tube for the system to communicate which uses tube speak as its dbus protocol.


Class Breakdown
===============
ovc.py
------
Main Program.  This class  connects the gui to the network.

gui.py
------
This class handles the graphical user interface.  It builds the menus and toolbars on the screen.

network_stack.py
----------------
Empty at this time. Will be used to generalize the Sugar network stack.

sugar_network_stack.py
----------------------
Controls the Dbus tubes.  Requests all tubes and filters out ones that are not used by this program.

tube_speak.py
-------------
standard Dbus ExportedGObject 	

