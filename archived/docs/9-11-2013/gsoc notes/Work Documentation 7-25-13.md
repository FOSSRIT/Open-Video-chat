
# Work Documentation 7-25-13

Todays goals are as follows:

- Initiate chat channels on double-click of usernames
    - Activate the send button and GtkEntry for chat
    - Test sending & receiving messages

- Create an account management screen/gui
    - Implement a placeholder config GtkToolButton
    - Test swapping GUI components with `clicked` signal

- Begin investigating Farstream examples and attempting to integrate.
    - If abstraction is complete, we should be able to just attach the buttons
    - Initiate a call etc from them

---

If I can have chat working by tonights end I will be happy.

Some references:

- [Text Channels](http://telepathy.freedesktop.org/doc/book/sect.channel.text.html)
- [Text Messaging](http://telepathy.freedesktop.org/doc/book/chapter.messaging.html)


---

When I get to farstream tests, here are important keys:

- [Calls](http://telepathy.freedesktop.org/doc/book/sect.calls.requesting.html)
- [Python Exmaples](http://cgit.freedesktop.org/telepathy/telepathy-farstream/tree/examples/python)


---

Well, for the contact list updates I am back to reading C it seems.

I cannot find a python equivalent method, so I need to understand the process of their code and see if I can tap into it somehow.

Their method `tp_base_contact_list_contacts_changed_internal` is called when `tp_base_contact_list_contacts_changed` is executed.  It accepts HandleSet's for the two arguments of changed and removed.  These appear to be callback methods then?

After a bit more reading of the [docs](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-connection-contact-list.html#tp-cli-connection-interface-contact-list-signal-callback-contacts-changed) it may be possible to use the Connection and a listener for ContactsChanged.  The method description represents the callback, or the arguments received not sent.

So, can we try `ContactsChanged`, or more appropriately `ContactsChangedWithID` which is the recommended signal (the other is deprecated?).


---

After a number of tests I was unable to attach those to the Connection object.  I thought perhaps the ConnectionManager might use it, [according to some docs](http://cgit.freedesktop.org/telepathy/telepathy-glib/tree/NEWS?id=telepathy-glib-0.20.2), which state "It's automatically emitted by TpBaseContactList, so CMs don't need to make any changes to take advantage of it".

The problem is, I cannot find any TpBaseContactList object.

Alrighty, well after failing to find it for a while I found [a link to the specifications](http://telepathy.freedesktop.org/spec/Connection_Interface_Contact_List.html#Signal:ContactsChangedWithID) being tossed about, which shows it as part of Connection.Interfaces.ContactList.

So perhaps it is part of the connection object?

One thing I have not figured out is what the various quarks actually do to the connection object.  So I have decided to run a series of tests.  I am assuming the core and capabilities are important components that maybe house the parts I need, in addition to `contact_list`.

If I add all of them, does what my Connection object "can-do" change?

We will continue this investigation later, for the time being I really should focus on working chat.  So let's get the click-to-activate tied to the network stack and enabling the chat system.


---

So, I cleaned up the chat and gui, and supplied several components to the gui from the network and vice versa.

Ideally I should document these in a cleaner way.

I have also tested the chat buffer and begun integrating channel establishment.

My next goal is to actually establish the chat channel and test it with a second machine with received and sent messages.


---

Ran into huge unexpected problems.

Creating or ensuring a channel results in a new popup window, which I have not yet figured out how to prevent (we want direct control, not an independent window).  Will ask in channel perhaps, how to prevent opening popup on channel.

Wow, so after a large amount of sillyness I finally figured out how it works.  I have the send_message operation going through, but I have not tested anything from a second client.  Just error-free processing on one-side so far.

Very impressed with the message system.  Need to document my findings tomorrow.


---

Fridays Tasks:

- Document all the cool things I am figuring out in Telepathy regarding channel establishment
- Create a second networked environment /w jabber account to run these tests from
- Begin creating the account management screen and testing Grid swaps


I am still investigating:

- Abstract channel-closing method for graceful shutdown AND chat switching
- Live Updates to contacts list
- Stateful Multi-User Implementation
- Confirmation dialogs for establishing channels/communication

The ability to nofity via a final-message when a user has disconnected would be important.

Live updates would be ideal for keeping track of available users (and this same code could be used to improve the Sugar UI as well).

A stateful implementation would track every opened user conversations independently, keeping all of their channels open, and displaying an indicator when new messages are received for off-screen users.

One option is to use tabs in the chat, but there could be others.

Confirmation dialogs might be overly complex at this point.
