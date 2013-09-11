
# Work Documentation 7-26-13

Today I have to attend the sugar-meeting at 1PM (EST).  I should be updating the Sugar Project Wiki as well.

My primary objectives today are to document what I learned in Telepathy regarding channel establishment for a blog post.  **DONE**

I will also be creating a Wheezy clone, not a jessie clone, to test the software in.  This will help me build my list of dependencies and verify truly whether or not the software can be made to work properly on Debian.

---

Using the second account will help me test that the chat actually works properly, with both sending and receiving messages (and channels).

Once the chat channel is working we can close this feature from git-flow and move onto the next.

I will also pose some additional questions to the Telepathy team in IRC, such as "How do I prevent Gnome3 from creating entirely separate widgets when I request a channel?"

---

The next feature is creating an account management screen for selecting, creating, and removing jabber accounts.  This will allow us to use a more robust system.

The network stack will be modified to store a list of valid_accounts that are "jabber" accounts.

The account management gui will be a GtkGrid that we will be swapping out with the Gui component.

This means we will need the ovc object to have a reference (if only temporarily) to the Gui while we swap the display components.

It also requires a new configuration button.

After we get the account management working, with selection, indication of the selected account, and tested/working account registration with the sugarlabs jabber server, we will be good to move onto the next git-flow feature.

---

Since it was suggested that I pursue telepathy farstream I will be doing that.  I have a batch of excellent examples that I was linked to that will help me with implementation.

I believe this will allow me to dramatically reduce the code required to build the system.  It **may** will also abstract the GStreamer start and stop processes, but that has yet to be researched.

Worst case scenario if farstream works but the controls do not exist I can create them using alternative message types (thanks to TelepathyGLib Client Messages).

If we can get basic video streaming and add audio after that would be excellent.

Besides that upgrading the icons in the GUI is also a goal.  We want the local video and audio to be represented by a mic and webcam icon, with a slightly different version in the sugar toolbar.

Once these changes have been made and basic functionality exists I will close this feature and merge it in.  Then I can move onto what should be the final stage of the project.

---

A new git flow feature, optimizations, which will cover a wide range of things that we just want to add to improve overall functionality and aesthetics.

Some examples:

- Confirmation dialogs on channel initialization to accept or decline
- Graceful channel closure, sending a final system-message and closing the channel
- Live Updated Contacts List
- Proper Multi-User Management
- Making use of all the awesome telepathy features
- Video tuning

Asking the telepathy irc group what the best practice is for dialogs, whether telepathy has its own built-in feature for declining them or not, would be cool.

[Documentation](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-channel.html#tp-cli-channel-call-close) about closing channels helps, but also context acceptance, what do?  A `close_chat_channel` method should be added and called from the `create_chat_channel` and shutdown process for the software.

Live updates to the contact lis would be great, but I have found very little in the way of related documentation for python.  Signals supposedly exist on the connection, but not when I attempt to run it, but this could just be a problem with missing quarks.  Which is its own problem since I have no reference about what the quarks add either.

A proper implementation of multi-user management would have several separate text buffers per user.  When a channel is opened it is added to the same data-store.  This allows us to retain, connect, and update each of them separately and add indicators on the usernames when chat has occured.  It may require adding tabs or a secondary list of some sort.

Awesome features in telepathy include the confirmation and callacks.  Proper placement of callback methods would allow a much improved aesthetic design, for example sending the channel message from a callback when running the request.  The same for closing channels.  Changing the color of received vs unreceived messages, may also be a really good idea.  Slightly grey on-send, and blackened server delivery confirmed.

Obviously tuning the video system would be important, but I haven't reached a stage where I can speak on how that might be done.
