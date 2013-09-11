
# OVC Documentation 9-9-13

Continuing from the last notes, I had worked out the details of text channels with smcv over irc.

He explained the basic workings and purposes of the observer, approver, and handler as such.

The handler is registered with the dbus service, and if no other handlers are running it will work.

If other handlers are registered it goes to the first-best.

The actual order dbus processes is observers, then approvers, then handlers.

This allows observers the ability to log, as an example, and also to override other services.

The approver allows a dialog to be displayed to the user before processing the channel.

To override other services you must use an observer, and one of the parameters received is a dispatch operation, which you can claim and supply it your applications handler (or handler string name?).

---

At this stage I am working at building a very basic implementation for the chat with no features except an entry box and message box.

I really need to see how it handles storing the channels after (to keep them alive), and whether I need to wait for the handler to register/store them.

I also have to test whether initiating the channel will register it with my own handler, or if I have to do that separately.

HAHA, figured out handling requested channels.  Apparently because ensure will try to re-use an existing (potentially claimed) channel it can fail.  We should instead go with `create_new_channel` and supply it the string name of our preferred handler.

After that I can begin implementation into OVC, and start working on the GStreamer pipeline.


---

I just finished the chat client test.

My next goal is a call channel test.

Then a gstreamer test.

Finally, merging these features into the core branch will be required.


---

Telepathy Tips:

When using an observer to override messages, you can run claim_with_async to claim it immediately, but if you want it to run through the handler callback then you use handle_with_async instead.  The claim approach is a short-cut that circumvents a lot of processing and is useful, but if you want to go through more natural channels it is possible.

Telepathy components are ref-count objects, and require a reference to exist to them at all times, or they and any connected signals to them will disappear.  Therefore channels, observers, handlers, etc must all be stored in variables.
