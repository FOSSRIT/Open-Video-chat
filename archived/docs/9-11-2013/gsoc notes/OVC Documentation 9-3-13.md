
# OVC Documentation 9-3-13

Catching incoming messages appears to be impossible.  Long live the ever mysterious TelepathyGLib!  I will never be able to merge and close this branch at this rate.

Left some questions in channel and through email, waiting on responses is the best I can do now.

---

Perhaps request can_close in sugar be made async friendly going forward?

Where should I suggest this, in channel?

---

Issues to create:

"Account Switch Conditions": Add conditions to prevent changing accounts if video communication is active.

"View Password Icon": Add to account_manager.py for the GtkEntry used for the password.  Icons can be added to either side with tooltip text and click functionality, this should be used to create a way to show the password.

"Active Account Indicator (Aesthetic)": Non-Functional enhancement add an indicator field with an icon to depict which account is currently active, OR find a way to select the active account in the list from code without triggering the callback recursively.

"Sugar datastore multi-user": Multi-User data-store process should store TextBuffer for each user independently and reload them accordingly.

"Incoming Chat Indicators (Aesthetic)": Like the active account, it would be nice to have indicators for any Contact's who've send us (unread) messages.  Perhaps even adding a filter to display only Contacts with a TextBuffer.

**Created!**

---

Created templates for gstreamer & farstream documentation.
Upload to repo.
Fix logging in repo to be specific types (error/warning/debug/info)
Open farstream feature branch

Fix log messages to use appropriate debug/info/error/warning types as needed.

Create farstream Feature Branch.
Begin reading the example source and create a test software.

Clean & upload all personal project documentation into archives (the dated files).
Update Readme.
Update Primary Documentation.
