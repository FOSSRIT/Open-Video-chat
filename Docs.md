This document serves as an outline of the code running OVC. We'll make
note of the methods and areas that may need improvement.

ovc.py
======
The main program behind Open Video Chat.

### \_\_init__
    Initializes the activity. Starts up the GUI, video pipeline, and
    network stackand waits for a partner to join.

### can_close
    Helper function that closes up our pipelines.

### _alert

### _alert_cancel_cb

### net_cb
    Handles messages from the network. There are only a few messages
    that can be received:
    * chat
        Receive a new chat message.
    * join
        Someone wants to chat. Get their IP, send our's and start
        streaming our video.
    * ip
        Partner sent their IP. If we're already in a chat we ignore
        this.

### send_chat_text
    Sends a message over the network.

### write_file/ read_file
    Store or read the chat history

gui.py
======
Controls the OLPC gui.

### \_\_init__
    Initialize the graphical interface.

### get_history
    Load chat history.

### add_chat_text
    Add new messages to the chat window.

### send_chat
    Send a message to our partner.

### build_toolbars
    Builds the sugar specific toolbars for our activity.

### force_redraw
    Forces our video streams to refresh.

### send_video_to_screen
    Sends the video streams to the correct view.

gst_ stack.py
============
Gstreamer bindings

This [manual](http://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&ved=0CDEQFjAB&url=http%3A%2F%2Fgstreamer.freedesktop.org%2Fdata%2Fdoc%2Fgstreamer%2Fhead%2Fmanual%2Fmanual.pdf&ei=QwmXT63yNpGJ0QHJgfG3Dg&usg=AFQjCNEvyaAmY6UX5IHR9XyHr9fdhPjAAQ)
is particularly helpful for understanding Gstreamer. Chapter 3 explains pipelines.

### \_\_init__
    Initialization

### build_outgoing_pipeline
    Creates a udpsink pipeline streaming video.

    v4l2src -> videorate -> (CAPS) -> tee -> theoraenc -> udpsink
    -> queue -> ffmpegcolorspace -> ximagesink

    Higher reliability may be gained by using tcp or rtp sink instead.

### build_incoming_pipeline
    Creates a udpsrc pipeline to receive streaming video.

    udpsrc -> theoradec -> ffmpegcolorspace -> xvimagesink

    Higher reliability may be gained by using tcp or rtp src instead.

