
# Project Progress & Notes
## 6-24-2013

Today my aim is to swiftly integrate hotkeys to the sugar terminal, and give the a test run on this system.

Afterwards I will perform a "merge request" per gitoreous.

Then I will continue my GUI Prototyping and revisions, possibly updating my repository status.

---

Discovered that the new Sugar development environment stores its live environment packages in a bottled form now, no longer pushing them into the /usr/share.

The path (starting from your sugar-build dir) is: `buid/out/install/share/sugar/activities`.


### Terminal Modifications

**Summarizing my objective:**

- Add New Tab
- Close Current Tab
- Go To Next Tab
- Go To Previous Tab
- Switch To Tab #

I went with a mixed set of conventions used by our RIT FOSS BOX, starting with some conventions set out by [gnome-terminal](http://www.pixelbeat.org/lkdb/gnome-terminal.html).  Exceptions made to these conventions are the next and previous tabs and the go-to-tab by numeric value.

The Hotkeys:

- ctrl+shift+t - New Tab
- ctrl+shift+w - Close Tab
- alt+rarrow - Next Tab
- alt+larrow - Previous Tab
- alt+# - Go to tab #

The `alt+#` hotkey is special, as it needs to check whether the tab exists, and has to identify them by the order they are listed.  The page up and page down keys are not on all keyboards, and are often hard to get to, especially with the XO laptops.  The arrows made more sense.

Terminal code has two main files, terminal.py which is where I need to connect key-press, and widgets.py which contains all the objects I need to know about and methods that may need calling to work.

There are three important components:

- BrowserNotebook - Sub Menu Container ([Gtk.Notebook](https://developer.gnome.org/gtk3/3.0/GtkNotebook.html))
- TabAdd - Add Tab button
- TabLabel - Represent Tab in GUI

Good news is that the terminal.py file already had global events for key-press-event attached to the `__key_press_cb` method.  This means I am able to simply insert my code there, and connect it to the top level methods.

Key Terminal Methods:

- `__open_tab_cb`
- `__close_tab_cb`

The tab-close emit triggers the parents `__close_tab_cb`, whose signal is caught by the tab itself.  This means we need to add logic to check the current tab to trigger its close event.  There should be a `get_current_page` method on the Gtk.Notebook, which will allow us to do just that.

Despite not being called anywhere in the Terminal activity code, these two methods exist and do exactly what I was hoping for:

- `__next_tab_cb`
- `__prev_tab_cb`

I had to create this method though:

- `__go_to_tab_cb`

While I had wanted to use the numbers with alt to go to a tab, it appears this is used as a hotkey already to pass arguments, not sure how it works but I can't overwrite it without breaking that functionality, so I will try ctrl+#.  I managed to implement this with very little trouble.

The final step left is catching the arrow keys.  Again I ran into issues with the alt key being tied to some sort of functionality, so I converted to ctrl arrow keys to navigate tabs.  I was able to detect Right and Left as key press, however I could not capture them in tandem with the ctrl key, so I went with another common standard ctrl+shift+} and ctrl+shift+{.

With the hotkeys fully implemented and tested I was able to push the changes to a fork, and submit a merge request.  Let's hope the maintainer likes hotkeys as much as I do.

---

Finish cleaning up the Repository for cross-platform distributable.

cross_platform
    setup.py
    gtk3

Icons folder for custom icons (include the ovc.svg).

Pushed changes to repo.

Remove the extra files I missed that start with a period and are no-longer related.

Pushed change to repo.

Closed the ticket.


---

Research Symposium?  I am presenting something?  What is it?  Add it to Misc Tickets in tracker?

What am I presenting in Flock exactly?

What should my sense of urgency be, and how can I prepare for these presentations?  I am in week 2 of 15 in my schedule, so I don't know how I fit into this mixture.

Flock is a Halfway Point for me.  Birds of a Feather is a chance to kick down some blockers.

BoaF is an information/formal as desired, open discussion, name tags & introductions, followed by objective sharing.  Can propose lightning talks, such as in my repo and the irc channels, and pinging the sugarlabs folks regarding it.

Ask lmacken and threebean for advice and suggestions.

Research Symposium on August 2nd?  Can I rework my timing to try and get GStreamer ready for lightning talk?  Or should I aim for something different?  It is quite a big history for the project.  The state of open video, and technological limitations?

Symposium: History of Project, experience as researcher from class to GSoC, and the challenges.

Flock worst/best case scenarios.  Worst case I run into a major GStreamer blocker, either hardware or software, and need advice on circumventing it.  Best case
