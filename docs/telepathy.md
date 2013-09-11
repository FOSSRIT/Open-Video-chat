
# TelepathyGLib Documentation

Let's start with reference links:

- [TelepathyGLib Docs](http://telepathy.freedesktop.org/doc/telepathy-glib/)
- [Telepathy Repository](git://git.collabora.co.uk/git/freedesktop.org-mirror/telepathy/telepathy-glib.git)
- [Telepathy Client Example](http://git.enlightenment.org/devs/kuuko/apathy.git/)
- [All of Collabra's Work](http://cgit.collabora.com/git/)

The best resource you will find is the Telepathy Client Example.  It is comprehensive, but not without flaws.  Granted, many of the flaws stem from breaks in TelepathyGLib.

Reading the documentation is the same as approaching Gtk3.  It is all written in C, and has the same quirks.  If you haven't read up on this or are unaware how it works, check the [Gtk3 Documentation](gtk3.md) out first.

## Contents

- Look to the Source
- The Main Loop
- How it Works
- Making Sense of Features
- Tips & Quirks


## Look to the Source

The first step to using TelepathyGLib should be to download their source code.

It is the first, and just about only, set of modern python examples using the TelepathyGLib library.  It is also quite incomplete, though modular so each part is mostly easy to understand.

Thus I found the Apathy program to be quite an excellent read for a more comprehensive coverage, but you might not want to jump into that right away.

The documentation itself differs quite a bit between C and Python due to implementation, but I'll go over that a bit later.


## The Main Loop

Since TelepathyGLib is part of the same GObject introspection library, this library uses [Inversion of Control](), which automatically adds it to any running threaded system.

This means it is fully abstracted, and all you have to do is initiate the loop with `Gtk.main()`, provided you are using a gui.  Without a GUI this can be done by important `GObject` and running `threads_init()`.


## How it Works

TelepathyGLib is highly threaded and depends heavily on asynchronous processing.  A large number of the function calls must be done using asynchronous processing, and it uses a unique method of attaching functionality to these methods that is not well documented.

The actual Telepathy stack sits on the dbus, which is shared with all applications in the system.  Because it is shared, you can have multiple jabber clients open and both will receive messages through the dbus chain if they are listening, which means the client is irrelivant as far as the messages are concerned.  I have not figured out how this effects other channels such as streaming calls with video and audio.

In that same sense messages and actions must be handled through the dbus, which is why it requires asynchronous processing to abstract the communication.  Similarly this is why adding to the feature-set is so unique.


## Making Sense of Features

Feature codes are highly inconsistent and one of the most frustrating parts of the TelepathyGLib library.  Even in the C documentation some exist on objects, others under an enum on the object.  Then you get to python and everything is wildly different.  Many of those enums are not where you expect them, and they replaced some constants randomly with `quarks`, which are methods that pull the value of the constant.

These `quarks` are not in the C documentation where they exist in the python API, and finding the features becomes a challenge, which brings us back to using `bpython`.  The lack of documentation and changed placements makes them hard to find or understand.

Further, when you are intending to use a method you have to read that methods documentation to see if any features are required for it to work.  If you call it without adding the features you won't get an error, just no contents, leading you to believe something entirely different might be the cause.

As if it can't get worse, you have to run an async method before you can access anything that has been requested using feature codes, and feature codes can in fact be requested in two ways with python.

One way is to pass a list of feature codes specific to the object you are calling an asynchronous method on, and this is the first argument.  The other is to pull a "rarely used in C" `TpSimpleClientFactory` from an object, which happens to be a global factory used by all components, and set the features there all at once.


So, now that we're done with the bad news, let's try to make sense of the features.  In some instances a constant will be used.  For example the `TP_CONTACT_FEATURE_ALIAS` feature is required to get the alias of a contact, and it exists under the enum `ContactFeatures` which belongs to the `TpContact` object.  However, in python `ContactFeatures` is a global enum as part of TelepathyGLib.

Then there are quarks like `Tp.Connection.get_feature_quark_contact_list()`, which returns a code that should be a constant.  While it is still attached to the object you expect, this method is not in the C documentation.  You need this feature if you want to pull contacts, and if you forget it you will get an empty list instead of an error.


As for figuring out whether a feature is a `quark` method or a misplaced constant, your guess is as good as mine.

Best way to approach this that I have found:

- Read the documentation of each method you use to see what it depends on.
- Use `bpython` to find feature codes and quark methods.


Now let's go over out to set features on the shared factory which would apply to all async calls going forward.  Here is how you can get the factory:

    am = Tp.AccountManager.dup()
    if am is not None:
        factory = am.get_factory()

Here is how you can apply features:

    factory.add_connection_features([
        Tp.Connection.get_feature_quark_contact_list(),
    ])
    factory.add_contact_features([
        Tp.ContactFeature.ALIAS,
        Tp.ContactFeature.CONTACT_GROUPS,
    ])

Next you have a run at least one asynchronous process, and in this case you already have an account manager object you can use:

    am.prepare_async(None, callback, None)

The first `None` in that method _could_ be used to send features one-time without using the factory, but in this case we already applied them globally.

A final tip, in line with GObject all objects in TelepathyGLib extend from [TpProxy](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-proxy.html), which you should be ready to check for methods that appear to apply globally, including asynchronous function calls.


## Tips, Quirks & Bugs

The Apathy source is an excellent example of using the factory to set requirements easily.

The `contact-list-changed` signal on the TpConnection object apparently doesn't fire, which I believe is a break in the library.  I have tried maintaining a ref-count to the connection object but that did not resolve this.  However I could also be misunderstanding how it is triggered, does the jabber server keep a record of all users connected even after they disconnect and simply mark their status as unavailable or offline?  If so that might be why it never fires, in which case `status-changed` of some sort should be attached to all contacts to monitor them.

Telepathy is ref-counted; if you want objects to continue existing a variable must point to them at all times.  If they loose scope they will disappear along with any connected signals.  Hence why the code keeps class level references to the observer, handler, and all channels.

When using an observer to override messages, you can run claim_with_async to claim it immediately, but if you want it to run through the handler callback then you use handle_with_async instead.  The claim approach is a short-cut that circumvents a lot of processing and is useful, but if you want to go through more natural channels it is possible.
