
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
