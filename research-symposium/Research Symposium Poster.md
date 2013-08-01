
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

Open Video Chat started with funding as an ASL project for the deaf, and was launched around the time FOSS@RIT was created.  It was one of the first major projects they worked with.  It changed hands twice during the first year of construction, lots of testing was done using tools that have since been deprecated.

It had a dry spell for over two years, and stopped working on the XO's due to changes in the operating system.  Two partners and I picked it up during a Humanitarian Free and Open Source Software class at RIT with renewed interest on bringing a video chat service back to the XO community, and working with some seriously complex technologies, like GStreamer.  We brought the project back to life and worked to migrate the code from Gtk2 to Gtk3, an attempt to rebuild the network stack, and had just enough time to begin exploring GStreamer.

Since the course ended I wanted to take the project further, and made a proposal for Google Summer of Code to bring the software to multiple linux platforms.  Sugarlabs accepted the proposal, which has given me a chance to learn a whole lot more about Gtk3, the Telepathy GLib library, and soon GStreamer.