THE DOCS
========
This document serves as an outline of the code running OVC. We'll make
note of the methods and areas that may need improvement.

ovc.py
------
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
------
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
