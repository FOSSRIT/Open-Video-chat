
The documentation is confusing as always.
Apparently offering a connection is secondary to receiving.
Which is more accurately "listening for incoming".
Also I cannot use self as target for contact.
I need to create a second account and VM for testing.

---

My next series of tests will hopefully lead to vast improvements:

- Populate list of users using their contact names.
    - This will be the first communication between components
- Test selection of user (double click ideally)
- Test opening a channel with the selected user
- Test opening two independent channels via reverse handler
- We need a way to handle a list of dicts for channel handling
- Video Streams will (probably) not be in the dict
- A clear method of establishing video with a user
    - And not multiples in the event that the user already has one session running

_I clearly need to diagram the connection process for this to make sense._
If cannot establish two text channels, may consider dbus channel for comamnds.
Establishing two should be possible with create, the question is the order of operations.
Two way handshakes?


- Account Management
- We need a new gui that allows the user to manage their jabber accounts
    - Registration
    - Selection
- By default the program only uses the first available, but we want this to be optional
- We need a toolbar button that swaps the configuration GtkGrid in place of the Gui GtkGrid


- Finally comes Multi-User management.
- We need to determine whether we can generate a Text Buffer per user.
- If we can swap them on selection we can store and swap chat history & channels
- We need to handle multiple channels, which means the network will need a similar array
    - Only populate established channels with contents (late-loading)
- Consider a contact object that is used purely for storing `established` contacts
    - Would contain the contact name
    - The text buffer
    - The channels
- Shared list between Network Stack & Gui
- This might make it overly complex, as we would need a manager to handle events.
