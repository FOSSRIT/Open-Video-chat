
# Work Documentation 7-24-13


Start by getting a GtkTreeView working with a GtkListStore.

- Adding the GtkListStore to the GtkTreeView
- Adding items to the GtkListStore (which should update the TreeView)



GtkListStore implements the GtkTreeModel interface, which allows us to attach it to the GtkTreeView using `set_model`.

`set_search_entry` exists as a method on the GtkTreeView, if all goes well I can apply that and the `set_search_column` to the names, for quickly filtering the contents of the list!  Excellent!

So, for a quick test let's try adding three items to our ListStore, and adding it to our GtkTreeView.  Hopefully no casting will be required.  Then we can try adding the search components to the mix.

---

Alrighty, I have attached the search entry and model.  Now I need to test adding data to a ListStore!  For this I will defer to the [python gtk3 docs](http://python-gtk-3-tutorial.readthedocs.org/en/latest/).

Well, I want to figure out what data is in the Contacts before I create my list then.  I need to figure out how to hide certain columns in the list as well.




---

We need to get two columns of data from the Contacts.  The account reference AND the nick name.  The nick names should be shown in the list, but the accounts are what the backend uses.

Contacts is in fact just a list of contact objects.  If I can figure out a way to tie the contacts list to the GtkListStore I will be all set for handling the updates.

As for the GtkTreeIter I might be able to make this work by defining a system that adds a Telepathy Contact object as one of the two types in the List Store.  Then it can store the whole class, and the raw user nick, making it easy to pull out any of the data we need.

If I cannot make that work then I need to create a translation system, with its own signals to emit when changes to the contact list are made.  I will then be storing the contact list, and running through the changed objects to modify matches in the List Store.  This is most undesirable as it is a whole lot of extra work, but it may be the only "correct" way to go about it, as I see no way to tie directly to a list object.

Alrighty, I verified that I need more quarks to get contact information.  This means adding another quark and testing the `dup_contact_info` to find their nickname (or something similar?).

Awesome, so I can acquire contact alias and use that with the contact itself to store important data.  I can remove the groups and contact info from the pulled info probably.

---


So, I need to use farstream and "Calls" not streamedmedia tubes.  A single chat text channel, and farstream should obfuscate the rest.

Tie the buttons to farstream's bits and hopefully it will all work.

So for now, just get the chat working, and build an account management screen.  Work on new icons with Jenn.
