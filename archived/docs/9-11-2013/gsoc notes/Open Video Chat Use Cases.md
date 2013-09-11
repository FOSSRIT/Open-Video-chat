
# Open Video Chat
## Use Case Diagrams


**User:**

- Selects User from Jabber List
- Sends Message to User over Jabber
- Requests Video Communication over Jabber
- Requests Audio Communication over Jabber
- Mute Local Outgoing Audio
- Mute Incoming Networked Audio
- Stop Local Outgoing Video
- Stop Incoming Networked Video
- Exit Program


**Program Actions:**

- Close Message Channel on Exit
- Pull users from jabber server


**Design Concepts:**

Either string based command system OR DBUS implementation to send requests such as:

- Start Audio
- Start Video
- Stop Audio
- Stop Video
- Private/PM

If implementation uses "/" prefix it would be very easy to make it possible to send commands through the chat message system, very slick like.


Implement Alerts for:

- Start Video
- Start Audio

This allows a user to open communication with another person (via chat) and clicking the buttons to start will display an alert to allow or deny audio or video communication.

