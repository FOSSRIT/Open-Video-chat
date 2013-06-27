#    This file is part of OpenVideoChat.
#
#    OpenVideoChat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenVideoChat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenVideoChat.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod: `OpenVideoChat.activity/sugar_toolbar` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""

# External Imports
import logging
from gi.repository import Gtk


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Toolbar():
    def __init__(self):
        # Do Something
        return True

    # def build_toolbar(self, activity):
    #     # Prepare Primary Toolbar Container
    #     toolbar_box = ToolbarBox();

    #     # Create activity button
    #     toolbar_box.toolbar.insert(ActivityButton(activity), -1)

    #     # Video Toggle
    #     video_toggle_button = ToolButton()
    #     video_toggle_button.connect("clicked", self.toggle_video)
    #     toolbar_box.toolbar.insert(video_toggle_button, 1)
    #     self.toggle_video(video_toggle_button)

    #     # Audio Toggle
    #     audio_toggle_button = ToolButton()
    #     audio_toggle_button.connect("clicked", self.toggle_audio)
    #     toolbar_box.toolbar.insert(audio_toggle_button, 2)
    #     self.toggle_audio(audio_toggle_button)

    #     # Toggle Preview Display Button
    #     preview_toggle_button = ToolButton()
    #     preview_toggle_button.connect("clicked", self.toolbar_toggle_preview_visibility)
    #     toolbar_box.toolbar.insert(preview_toggle_button, 3)
    #     self.toolbar_toggle_preview_visibility(preview_toggle_button)

    #     # Forced Refresh
    #     reload_video = ToolButton("view-refresh")
    #     reload_video.set_tooltip_text(_("Reload Video"))
    #     reload_video.connect("clicked", self.force_redraw)
    #     toolbar_box.toolbar.insert(reload_video, -1)

    #     # Push stop button to far right
    #     separator = Gtk.SeparatorToolItem()
    #     separator.props.draw = False
    #     separator.set_expand(True)
    #     toolbar_box.toolbar.insert(separator, -1)

    #     # Create Share Button
    #     toolbar_box.toolbar.insert(ShareButton(activity), -1)

    #     # Create stop button
    #     toolbar_box.toolbar.insert(StopButton(activity), -1)

    #     # Add reference to toolbar items
    #     self.toolbar = toolbar_box.toolbar

    #     # Display all components & Return
    #     toolbar_box.show_all()
    #     return toolbar_box
