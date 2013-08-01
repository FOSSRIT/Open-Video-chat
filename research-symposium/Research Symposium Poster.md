
# Research Symposium Poster

Key Sections:

- Logos
- Stack Diagram
- Screenshots
- Some text

**Rules/Restrictions:**

- At most 6 paragraphs or titled-lists worth of text
- Original & New UI Screenshots (transitional arrow)
    - If able to get local video working in the UI attach it for this
- Create an Inkscape SVG diagram with the stack components and logos for software being used


## Ideas for Text

**What is Open Video Chat?**

Open Video Chat is a video communication software originally developed in 2010 for the XO laptops as part of the One Laptop per Child program, and was originally intended to aid the hard of hearing.

- FOSS Video Communication Software
- Lightweight source for XO Laptops
- Built for Sign language


**What does it do?**

Open Video Chat uses the webcam on the XO laptops or any system the service is running on that GStreamer can acquire automatically (it will use the default device as configured by the system), and creates a tee to split the video for local and networked viewing.

When the user picks a person to communicate with they are able to establish a video stream over the network with video and audio.  They can turn off either audio or video, local or networked, allowing finer controls for low-bandwidth situations.  They are also able to use text based communication.


**Project Objectives**

The original version was built in 2010, and the code has since deprecated.  My aim is to revise the code, add audio, and make it functional across multiple linux distributions.

- Revise code
- Add audio
- Cross platform


**How does it work?**

OVC is python based, with four major dependencies.  It uses Gtk3 for the User Interface and threading abstraction.  It depends on Telepathy for the network stack, and GStreamer for video.  It bridges the video to the network stack using Farstream.

- Python source
- Telepathy network stack abstraction
- GStreamer Video & Audio
- Farstream bridged audio-video networking
- Gtk3 User Interface


**History**

Open Video Chat's initial development was made possible through funding from NTID/PEN International, focusing on a video-biased ASL friendly application for the Deaf. After the team brought OVC to working prototype, it changed hands twice during the first year of construction through class projects in the Humanitarian Free/Open Source Software (HFOSS) Development course. Lots of testing was done using tools that have since been deprecated upstream

OVC eventually stopped working on the XO's due to changes in the operating system, and sat dormant awaiting porting to modern libraries. Two partners and I picked it up during the 2012 spring session of the HFOSS class at RIT with renewed interest on bringing a video chat service back to the XO community, and working with some seriously complex technologies like GStreamer. We brought the project back to life and worked to migrate the code from Gtk2 to Gtk3, rebuild the network stack, and begin exploring GStreamer.    .
