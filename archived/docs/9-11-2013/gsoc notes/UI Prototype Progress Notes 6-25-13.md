
# UI Prototype Progress Notes
## 6-25-2013


Primary Configuration:
Gtk.Window, default size of 800x600
Gtk.Grid added to window as only component with h/v expand true to take up full space.

Our Toolbar Process:
Gtk.Expander to hide the Gtk.Toolbar
We then add four Gtk.ToolButton's to it, with icon_widgets and tooltip text etc.

Our Video Area:
We need a black background for the video area, and the method for that is with a Gtk.EventBox
We add a Gtk.DrawingArea to the Gtk.EventBox, and attach the EventBox to the Gtk.Grid layout.
Finally we display the elements

Our Chat Area:
A Gtk.Expander which stores a Gtk.Grid
Our Gtk.Grid storing a Gtk.ScrolledWindow for the Chat History and Gtk.Entry() for user input.
A Gtk.Expander that will allow us to hide the users list, which takes up one corner of the Chat Area.
A Gtk.List of some sort (Gtk object not yet found) to select users, and a GtkEntry to search for connected users.
User list will be a Gtk.TreeView, that will allow us to display selectable users.

---

Concerns with redundancy versus ease of development.

The design of the system currently can be made such that the User Interface, Network Stack, and GStreamer Stack are all reusable between both the Sugar and Cross Platform releases.

Cross Platform files would include an OVC top level class extending window, and a Gtk3 toolbar.

Sugar specifics would include the Sugar OVC top level class extending the Sugar Activity (which extends Gtk Window), and a Sugar Toolbar (which is built into the activity).

It would be possible to create a smart launcher to handle the execution of either version, using a try/except importerror.


**Ideas:**

- Merged Files
- Separated Files

Merged files eliminates code and icon redundancy, at the cost of higher required developer knowledge when editing.  An unwitting developer could edit the shared files and have it work on one end but break the other.

Separating the files creates redundancy of both images and files.  However, it then becomes possible to modify each version of the code independently.


Thoughts & Alternatives?

What is best practice?


---

Confirmed with threebean the benefits of eliminated redundancy are fine, and proper documentation should be plenty to prevent problems going forward.  Just clearly outline that the components must remain independent of their respective environments.

I was able to launch the sugar version by labeling the file appropriately

Verified that simply leaving sugar to its own devices and not even bothering with a try catch in the launcher works great.  The alternative is adding .py on the launcher, which works but adds an extra file into the mix without any need.

I can modify what gets included in the sdist setuptools package from the manifest.in, and I want to see if the same can be done with the sugar bundlebuilder.py (build/out/install/lib/python2.7/site-packages/sugar3/activity/bundlebuilder.py).

If I can get the same sort of effect from a manifest I can totally destroy any problems going forward.

---

[Sugar MANIFEST Example](https://git.sugarlabs.org/projects/physics)

They used sugar, not sugar3.  BundleBuilder changed in sugar3?

Try to change our file structure to match the file structure used by sugar activities.
Create a "smart" setup.py which uses sugar if able, else setuptools.
If setuptools is used should use the Manifest.
Run tests to get manifest working in sugar.



WOW, manifest is no longer used in bundles.  Guess that means I have a bit of work to do.

I guess that means I can keep the top level for cross platform releases, and the .activity folder for its own purposes?

I still have to test the setuptools & Manifest.in.  If those work I am good to continue.

---

**Example Manifests:**

Tahrir MANIFEST.in:

    include *.txt *.ini *.cfg *.rst
    recursive-include tahrir *.ico *.png *.css *.gif *.jpg *.pt *.txt *.mak *.mako *.js *.html *.xml
    include LICENSE

    graft apache



Tahrir API MANIFEST.in:

    include *.rst
    include LICENSE
    include alembic.ini
    recursive-include alembic *
    recursive-include tests *.py


Fedora Packages MANIFEST.in:

    recursive-include production *
    recursive-include fedoracommunity *.mak
    recursive-include fedoracommunity *.js
    recursive-include fedoracommunity *.png *.gif *.svg
    recursive-include fedoracommunity/public/css *.css *.ttf *.png *.gif *.svg *.eot *.woff
    recursive-include initsys *
    include logrotate

    include fedoracommunity_makeyumcache
    include fedoracommunity.spec
    include orbited.cfg
    include README.txt
    include AUTHORS
    include COPYING
    include build.ini
    include bin/fcomm-index-packages
    include bin/fcomm-index-latest-builds


**My MANIFEST.in:**

    recursive-include OpenVideoChat.activity *.py
    recursive-include OpenVideoChat.activity *.svg
    exclude OpenVideoChat.activity/setup.py
    exclude OpenVideoChat.activity/activity/activity.info
    prune OpenVideoChat.activty/dist



---

For now temporarily disable the User List components but distant future plans for adding User List:
[Add TreeView for User List](http://python-gtk-3-tutorial.readthedocs.org/en/latest/treeview.html)
[Gtk Docs](https://developer.gnome.org/gtk3/3.0/)

[Manifest Testing](http://docs.python.org/2/distutils/sourcedist.html)

