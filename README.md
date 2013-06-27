
# Open Video Chat

Open Video Chat is an open source video conferencing activity for the XO laptop. This project was originally started in March 2010 with funding from the National Technical Institute for the Deaf in Rochester NY, and continues with RIT HFOSS course and Google Summer of Code in 2013.


## Focus

The original focus was to use GStreamer to provide acceptable frame rates for sign language communication (estimated somewhere between 20 and 30).

Current GSoC 2013 objectives are to get it running again on Sugar and porting a pure Gtk3 implementation for cross-platform compatibility.


## Current Features & Status

- Sugar3/Gtk3 Interface
- text chat system on Telepathy channels
- Incomplete GStreamer 1.0 & RTP upgrades


## Planned Features

- Upwards of 30 frames per second
- Cross Platform Gtk3
- Audio
- Higher Resolution or Scaling
- Multi-User Implementation


## IRC

The contributors of Open Video Chat frequent `#rit-foss` on freenode


## Mailing-List

[Fedora Hosted OVC Mailing List](https://fedorahosted.org/mailman/listinfo/ovc)


## Copyright

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


### Linux Cross Platform Instructions

#### Execution

The application can be launched from command line via the launcher script:

    chmod +x launcher
    ./launcher

Alternatively you can run the launcher through python:

    python launcher


#### Installation

Simply download the repository files or unpackage the distributable copy to a folder of your choosing.

An example of proper setup (requires privileged access):

    sudo mv OpenVideoChat.activity /usr/local/ovc
    sudo ln -s /usr/local/ovc/launcher /usr/bin/ovc-launcher

Then you can access OpenVideoChat from anywhere while in command line via `ovc-launcher`.

#### Adding it to Gnome3

To add OpenVideoChat to the Gnome3 graphical environment, you will want to create an `ovc.desktop` file with contents similar to:

    [Desktop Entry]
    Name=Open Video Chat
    Comment=FOSS Video Communication Tool
    TryExec=ovc-launcher
    Exec=ovc-launcher
    Icon=/usr/local/ovc/activity/activity-video_chat.svg
    Type=Application
    Categories=GNOME;GTK;AudioVideo;Video;

Place this file in `/usr/share/applications/` and it will now be accessible from Gnome3 either searching its name or its icon.


##### _Local Installation_

_You will not be able to install a symlink to command line without privielges._

However you can still execute it, and add an `ovc.desktop` file to `~/.local/share/applications/` to make it accessible to only your user.  The path for `TryExec` and `Exec` will need to be changed according to its locally installed location since you have no short-hand command.


- [Gnome3 Reference](https://developer.gnome.org/integration-guide/stable/desktop-files.html.en)
