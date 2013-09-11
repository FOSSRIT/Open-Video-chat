
# Incomplete Suggestions for Future

I wanted to document suggested incomplete components of the network stack that I probably won't have time to implement or fine-tune.  By providing references and documentation this will hopefully make it easier for the next developer to come along and handle it.

I am almost certain that these will not be done with the available remaining time.  They are a combination of fine-tuning and enhancements that would be ideal for a modern communication tool (aesthetically).

Doc References:

- [TelepathyGLib Docs](http://telepathy.freedesktop.org/doc/telepathy-glib/)


### Account Status Signal

There is a "status-changed" signal emitted by the account, such as when it is disconnected.  Being able to capture this and handle it accordingly would be wise.

[Telepathy Account Docs](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-account.html#TpAccount-status-changed)

Due to multiple account possibilities it would be wise to add a signal storage dict, if I have not already to disconnect them as needed.  Removing signals from the account when switching active accounts, and adding a new signal to the new account are both important.  Additional logic to determine whether the switched-to account is active would also be important.


### Chat System Extrapolation

For multi-user message handling, tying it to the sugar datastore or a custom datastore system.

Making it possible to attach decorators to messages.

I don't have a strong understanding of the iterator and positioning of characters in the text buffer, otherwise I would certainly do this myself.


### Architecture Cleanup

At time of documentation, many methods are just hashed together in a most incomprehensible manner.

It would be ideal to have some form of architecture in the system that allows callback registration for known key-events.

- Network-Stack Connecting
- Account Manager Displaying
- Chat System Sending/Receiving Messages

For example, when the toolbar button to display the account manager is clicked, it should repopulate the list.  This may be added manually, but would ideally be a registered callback on the toolbar component for that specific event.

Similarly when the network stack is connecting, if it is a sugar connection the callback should be tied to setting up handling for sugar-connection logic, which is inside the sugar ovc file.  Same with account manager logic inside the standard ovc file.  This would also make it possible to add them to the constructor for automatic setup.


### Colors

At time of documentation, there are no color codes for different things.

- Disabled/Unconnected Accounts in Account Manager
- Chat messages such as sent, server-received, and system messages

When a user sends a message there is a [callback](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-text-channel.html#tp-text-channel-send-message-async), which can be provided as an argument.  This captures when it has been received by the server and would be a good way to ensure message is sent.  A color-change using a decorator pattern or similar would be good.

Remember that with the async processing and iterator situation simply capturing the position of the message when it is added is not enough, if two messages are awaiting validation and things change the color-swap on one may affect the iterator position of the second.


### Status Messages

Right now there is no easy way to deliver status messages, such as whether the accounts are working, if they are disconnected, etc...

It would be nice if some type of overlay could be added when needed to be displayed.  Perhaps a modification of the dialog system.


### Multi-User Support

Determine best route for handling multiple open channels for chat:

1. Shared Text Buffer with Selected User as Send Target?
2. Tabs with separated buffers per user?
3. Selected Users dynamically create & swap buffers (stored in ListStore)

**Look at [Sash](https://github.com/FOSSRIT/Sash/) for how to save to datastore to retain message data for multiple accounts.**
