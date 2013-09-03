
# GTK3 Documentation

OVC was ported from Gtk2 to Gtk3 in the Spring of 2013.  All sugar activities are migrating to Gtk3 so going forward you will want to get familiar with the API.  This document will try to help you achieve that.

Let's start with some links to tools, references, and documentation:

- [Paul Friends Gtk3 Presentation](http://www.youtube.com/watch?v=CWcy3sgOWDQ)
- [C Documentation](https://developer.gnome.org/gtk3/3.0/)
- [Python Examples](http://python-gtk-3-tutorial.readthedocs.org/en/latest/)
- [bpython](http://bpython-interpreter.org/)
- [devhelp](http://en.wikipedia.org/wiki/Devhelp)
- [Glade](https://glade.gnome.org/)

Paul's presentation was a beginner level introduction, and used Glade as part of its process.  Unfortunately the slides are not captured during the first hour of the video.  I adopted key tools suggested in his presentation and have added them here.

You will spend a lot of time in the C documentation, so this guide aims to help you understand how to translate it for Python development.


## Contents

- About the GObject Transition
- Recommended Utilities & Resources
- How to read GObject Documentation
- Gtk Main Loop
- GTK Tips, Tricks & Pitfalls


## About the GObject Transition

To begin with I want to discuss GObject and the transition many libraries have been making.

If you haven't already heard, GObject is an Introspection library, which means it's code that describes itself.  In this fashion, the documentation can be generated automatically, which is great because it means there are no human errors or maintenance.

Similarly rules are used to automatically generate API's such as for Python GTK3.  Sadly they don't yet generate documentation for the API's, despite already having the rules and such.

In any event, all of the GObject libraries can be brought into python through `gi.repository`.  The one we are looking for is:

    from gi.repository import Gtk

Among the other GObject libraries used in OVC there is also `Gdk` and `TelepathyGLib`, but this guide focuses on `Gtk`.


## Recommended Utilities & Resources

I recommend always having a tab in your browser open to the C Documentation.  The python examples are great to get you started when tooling around with new components and widgets, but do not cover all objects and do not go into great detail about using each object.

I also recommend [`bpython`](http://bpython-interpreter.org/), especially at the early stages when you are still getting the hang of transcribing C to Python.

If you are on the go a lot, or lack internet I highly recommend using [`devhelp`](http://en.wikipedia.org/wiki/Devhelp).  It was recommended by [Ralph Bean](http://threebean.org/) and takes advantage of GObject's introspective capabilities to allow autocompletion.  Since the C documentation uses a [decorator pattern](http://en.wikipedia.org/wiki/Decorator_pattern) all the python function names are snipped ends of the C functions, and sometimes it can be tough to figure out where the function exists.  With `bpython` you can import Gtk and check objects for their methods with auto-completion.

During Paul Friends presentation he recommended [Glade](https://glade.gnome.org/) and [devhelp](http://en.wikipedia.org/wiki/Devhelp).  **OVC does not use Glade.**  Glade is a UI creation tool that creates entirely separate import files that describe UI components.  It is an alternative to creating all of the objects in the code.  OVC creates it's objects from scratch.

Glade is very reminiscent of early RAD (Rapid Application Development) tools, much like Visual Studio, but it does not appear to have comprehensive coding environment, mostly for rapid UI creation.  It can be very helpful when you are trying to understand how certain components work.

The `devhelp` tool is a documentation browser, and it allows you to download the doc packages for Gtk3 and many other things and have them all locally accessible.  This can be immensely useful if you are on the road often without sustainable or reliable internet.

Installation on Fedora:

    yum -y install bpython glade devhelp gtk3-devel gtk3-devel-docs


## How to read GObject Documentation

Documentation for GObject is generated automatically, and only for C.  If you are not familiar with C or C documentation this will lead to plenty of awkward moments, hence why tools like `glade` and `bpython` can prove to be more helpful than the documentation at times.

This documentation aims at helping you skip the "awkward moment" stage to make sense of this faster.  By the end of this section you should understand how to read the C documentation and then write python code for the Gtk3 API.

Let's start by opening up the documentation for any element (GtkWindow, GtkButton, etc) and checking the menu at the top.  Here is a basic overview of each important section by title:

- Synopsis
    - List of all methods for that object, their arguments, and return values (First item on the page, but not listed in the menu).
- Object Hierarchy
    - An upstream list of which classes this object inherits from.
- Properties
    - The properties that can be set on this object.
- Signals
    - These are names of events that we can attach methods to.

Now for the magic translation, ready?

All of the methods in C are stand-alone functions, not object oriented.  They resemble the [Decorator Pattern](http://en.wikipedia.org/wiki/Decorator_pattern), and accept the object they affect as the first parameter.  This differs from the Python API where the methods extend from the object.  When reading the **Synopsis** be sure to clip off the prefix and you will (usually) find the method name you were seeking.  This is where tools like `bpython` can be very helpful.  It is also a good choice to read the documentation of each method before implementing it.  Often times they mention information that is either required or can help simplify using the method.

The trick with GObject libraries is that they all extend from the GObject class.  As the upstream gets longer and further away it builds what we refer to as an **Object Hierarchy**.  This is really just a list of all parents that our object inherits from, and allows us to find methods that we often wish to use on our object that actually belong to a parent.  For example the signal `check-resize` fires when the user resizes a `GtkWindow`, but the signal exists on its parent's parent element, a  `GtkContainer`.  It is good to build a habit of always checking the parent documentation in the Object Heirarchy when looking for methods, properties, and signals.

You can set **properties** in the constructor when creating an instance of the Gtk widgets.  Anytime you have a property with a hyphen (-), you replace it with an underscore.  For example, GtkWindow `accept-focus` becomes `accept_focus`.

Finally, when using **Signals** you will always want to read the documentation for them.  Often they will list external requirements and settings, potential name changes for the signal under different conditions, and the arguments they will supply to any connected methods.  This habit may save you hours of wasted time trying to figure out why a signal isn't firing.


## Gtk Main Loop

[Good news everyone!](http://www.youtube.com/watch?v=1D1cap6yETA)

All of the threading is handled by a fully abstracted main loop.  You can start and stop this main loop with two methods:

- `Gtk.main()`
- `Gtk.main_quit()`

_You will want to attach the `main_quit` method to the main window destroy signal, this way the software ends when the window is closed, otherwise it will continue executing in the background._

If you want your application to function as an optional widget to another application you can create the object from a launcher and execute `Gtk.main()` and connect `main_quit` to the object from that file as well.


## GTK Tips, Tricks & Pitfalls

When extending a Gtk widget always call the widgets constructor (eg. super).  For example: `Gtk.Window.__init__(self)` where self could be a class extending `GtkWindow`.

Widgets are hidden by default, don't forget to `show()` or `show_all()`.  Avoid using `show_all()` when feasible, it will recursively run `show()` on all child components, which can be inefficient.

All signal connections allow a list of user-defined *args to be supplied, which allows you to send data without needing to store it in a global or class variable.

The HBox and VBox layout components are deprecated, and GtkGrid is apparently the replacement for all GUI Organization.  It is a bit tough to make sense of at first, but GtkGrid is highly flexible and can do pretty much all of the things HBox and VBox used to.

Not everything can have a color and background applied, many widgets are in fact transparent.  If you visit the [FAQ]() in the documentation, apparently GtkEventBox is there go-to container to apply these the "traditional" way.

There exists a Psuedo-CSS based theming engine for Gtk3, which has its own rules making it like yet another browser to develop and tweak for.  It is not very well documentation, but is the only way to heavily customize the UI.  I recommend only looking into this if it is a necessity that you modify the look and feel of your software.

The most complex elements thus far that I have encountered are scrolled text buffers and lists or tree views.  These have so many Gtk components that it hardly feels like an abstraction.  However they are highly flexible.  I recommend reading the python example code in the second resource I linked to earlier if you intend to give them a try.
