
# OVC Documentation 9-11-13

With the chat demo code completed and functional, my goal today is implementing these changes to the network stack and closing the feature branch.

I can then upload this demo file, and update my telepathy documentation, and add new documentation files to the mix.

Afterwards I will begin building a GStreamer Pipeline Demo to be implemented.


---

Content merged but untested.

Pushed documentation and chat example.


I need to cleanup my personal docs and add them to the archives.

Also still need to review and fix logger.debug into info/debug/warning/error as appropriate.

Then I can create the gstreamer example.

Then a call channel example with gstreamer.

Finally I can create a gstreamer feature branch.

Implement the gstreamer and call code, test, and merge & close to be done.


---

Confirmed that even sugar3 still uses the old non-glib telepathy system.

As such I cannot depend on buddy objects for cross-platform compatibility without creating two entirely separate network stacks (more to code and maintain is a negative).

So I am looking at methods to extract the contact id from the buddy object to identify them in the contact list.

I have made the contact list invisible, and updated the setup process for the sugar implementation.

Both OVC and Sugar OVC need testing, and then cross-platform communication testing .

