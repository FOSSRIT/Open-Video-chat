
# Work Documentation 8-5-13

Added logic to network stack:

- Grab jabber accounts using `dup_valid_accounts` (not `get_valid_accounts`)
- Added logic to parse valid jabber accounts
- Added logic to check that at least one account existed
- Added logic to check whether an account was enabled and connected

**Temporarily** auto-force connecting the first valid account, but future iterations will need to pop open the account management menu to do the rest.

This will allow the user to force the connection of the accounts
Future iterations will simply open up the account manager if no accounts or active account sare found.

Connecting and disconnecting an account is order-specific but involves enabling and setting presence, and the reverse setting presence to OFFLINE then enable to false.

Had problems with constant reconnections to the server, so I created a feature branch for the account management GUI which we will need to test and upgrade the toolbar for next.


---

Toolbar modifications should enter first.
I need to export the two sizes of each of the updated icons, and one clashing icon.
Name them appropriately & place them into the icons folder.

I have to try to space the account management icon to the far corner?
    Or make it the first icon.

I need to test that I can swap the GUI without breaking anything.
    Active video will disable the account management page
    Similarly active account management page will disable the other buttons


The account management page will be a GtkGrid, like the gui.
A list on one size with a plus and minus button below for adding and removing accounts.
Enable/disable minus button on account selection.

Active account needs to be listed in bold.
Double click to set default
    Tooltip text to explain this

Single click should change the values on the side.
Gtk entry for username and password.
GtkEntry with:
    caps-lock-warning true
    visibility false

Add an apply and close button to the bottom corners.
Apply should only be enabled when:
    New account and both fields have content
    Old account and changes to either field


---

When I am able to connect again I need to try to test chat channel messages both receiving and sending.  I believe I got sending working, but receiving was being a tad silly.

If I can catch and interpret messages then I will be all set to move onto the call processing logic, which will certainly take me the rest of the time available.

If I can get just basic message handling working that'll be a good start.


---


Feature Branch GUI Enhancements:

Add tooltip text to explain click to chat to the UI.

Create a wrapper system for messages as transactions that handles adding tags.
Wrapping system messages in say "bold"
Changing sent messages from grey to black on server-received callback
