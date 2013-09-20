
# GStreamer Documentation


This document aims to quickly get you familiar with GStreamer by explaining the architecture sensibly without delving into great detail about the components and their interactions.

It is highly recommended that you give the "Manual" a brief run through, as it goes into detail where this documentation may not.  This documentation will use terminology mentioned in the documentation as well.

As per the default format, here are a series of links to referance material:

- [Manual](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/index.html)
- [All GStreamer Documentation](http://gstreamer.freedesktop.org/documentation/)
- [GStreamer Core](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/)
- [GStreamer Plugins Core](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer-plugins/html/)
- [GStreamer Plugins Base](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/)
- [GStreamer Plugins Good](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good-plugins/html/)

**There are multiple "sets" of separated plugins, and OVC uses a few from them.  Be sure to check the documentation page for more links to the other elements.**

## Contents

- What is GStreamer
- The GStreamer Library
- Controlling the Elements
- A Look at a Raw GStreamer Pipeline
- Building a Pipeline
- Turning on the Pipeline
- Changing Settings at RunTime


## What is GStreamer

GStreamer is a lego-library.  It has a simple architectural structure where you are given building blocks to assemble the things you need for your application.

The "Manual" describes the foundations of the library:

- [Elements](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstElement.html)
- [Pads](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstPad.html)
- [Bins](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstBin.html) & [Pipelines](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstPipeline.html)
- Communication

The goal is generally to create a `Pipeline`.  A Pipeline is a string of `Elements` from a start to finish.

The start and finish are `Pads`, but often you will have more than two endpoints in a pipeline.  _Pads generally come in two flavors, sources and sinks, but there are exceptions._

`Bins` are containers into which you can throw related elements to simplify controls over a segment of a pipeline.

The `Elements` are generally plugins, and each is used to perform a specific task on a pipeline, much akin to the unix philosophy.


## The GStreamer Library

GStreamer actually extends the GObject library, which means everything inside it stems from GObject.

You can import it in python using:

    from gi.repository import Gst

As a part of the GObject introspection library, all elements extend from GObject, including the plugins.

All GStreamer components extend from [GstObject](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstObject.html) giving them a set of common functionality, and most (if not all) plugins extend [GstElement](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstElement.html), giving them also a set of shared functionality.


## Controlling the Elements

The base components of a pipeline are elements, and understanding them is going to be a pivotal part of being able to use GStreamer.

Things to keep in mind:

- Order matters
- Many elements have their own settable properties
- Cannot change elements in an active pipeline

This means that during construction you need the forsight to know what you want to achieve before the pipeline is activated.

_There are ways to change the pipeline at run-time, but these are not as easy to do as planning ahead and are best reserved for scenarios without an alternative._

Creating elements with GStreamer could not be easier.  The GStreamer library has an [ElementFactory](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/GstElementFactory.html) that abstracts the entire process, which means you don't need separate imports or anything else.

Simply name the element you want to create:

    video_input = Gst.ElementFactory.make("autovideosrc", None)


## A Look at a Raw GStreamer Pipeline

GStreamer can be run manually using the `gst-launch` command.

This is great for debugging, and also gives us a great way to easily see a pipeline in action:

    gst-launch-1.0 videotestsrc ! videorate ! capsfilter ! video/x-raw,width=800,height=400,framerate=30/1 ! videoconvert ! ximagesink

**This pipeline will show us a test video source with several elements commonly used for streaming input such as a webcam, and display it in a window.**

The next section covers building the same pipeline in python.


## Building a Pipeline

As mentioned, `Pads` make up the end points of a GStreamer, often titled streams and sources.  While generally used for input and output they can serve other purposes as well.  Each pad will likely have it's own special signals you can catch, so be sure to read the documentation for each element you use.

Also, a pad does not have to be at the beginning or the end of a pipeline.  Some pads will happen in the middle, others may require that you `tee` the pipeline.  Similarly if you are merging sources you will need an element capable of handling that merge as well as an encoder capable of handling those sources.

In the below example, I have an `autovideosrc` which is an input `Pad`, and it will automatically find video inputs (a webcam probably), or fail if nothing is available (For testing you can always use the `videotestsrc` `Pad` as well).

The source connects to a `videorate` which smoothens the input frames into a video, and a `capsfilter` which allows us to specify the size and frame rate, then `videoconvert` to handle color tones.  These are `Plugins`, each doing one specific thing.

**Note: Caps height and width can only work within the allowable range of the web-cam's hardware, if you set a size too-large it will fail.  If you need a size that may be outside the range of the hardware's capabilities you can use a `videoscale` `Plugin`.**

Finally I attach it to an `ximagesink`, which has a special signal `prepare-window-handle` which stems off the Pipeline Bus.  So you have to connect a "message" signal to the pipeline's bus, and then parse that signal from the messages to get what we need.

Once that signal is caught, we need to attach a window XID which allows the video output to be attached to our own element.  With the Gtk3 library we need to wait for an element to be "realized" before we can get the XID, which is from the GdkWindow that wraps our Gtk elements.

Here is my code:

    """ Prepare Elements """
    #video_source = Gst.ElementFactory.make('autovideosrc', "video-source")
    video_source = Gst.ElementFactory.make('videotestsrc', "video-source")
    video_rate = Gst.ElementFactory.make('videorate', None)
    self.video_caps = video_caps = Gst.ElementFactory.make('capsfilter', None)
    video_caps.set_property("caps", Gst.caps_from_string(CAPS))
    video_convert = Gst.ElementFactory.make("videoconvert", None)
    ximage_sink = Gst.ElementFactory.make("ximagesink", "video-preview")

    """ Create the Pipeline """
    self.pipe = Gst.Pipeline()

    """ Add Elements to Pipeline (Remember: Order Matters) """
    self.pipe.add(video_source)
    self.pipe.add(video_rate)
    self.pipe.add(video_caps)
    self.pipe.add(video_convert)
    self.pipe.add(ximage_sink)

    """ Chain together the Elements (Order also matters) """
    video_source.link(video_rate)
    video_rate.link(video_caps)
    video_caps.link(video_convert)
    video_convert.link(ximage_sink)

    # Acquire pipe bus
    self.pipe_bus = self.pipe.get_bus()

    # Make sure it knows we want to listen for signals
    self.pipe_bus.add_signal_watch()

    # Tell the bus we want to handle video messages synchronously
    self.pipe_bus.enable_sync_message_emission()

The last few lines show settings on the pipeline bus, we set two.

The first, `add_signal_watch`, tells the bus to trigger the "message" signal in our program, if we do not set this and connect to the "message" signal, nothing will happen.

The second enables the "sync-message" which we will want to connect to in order to catch the end of a stream.

Now to go over something very important.  **Order Matters**, and often a solid understanding of how video and audio will react with specific plugins helps.  Be ready to get lots of errors.

Here is a clean and understandable build process:

- Map out your required elements (pads and plugins)
- Create the elements (Including Sink & Source Pads)
- Create the Pipeline
- Attach all elements (in order) to the pipeline
- Link all elements in the same order they were added to the pipeline
- Extract the bus from the pipeline to set settings and connect signals
- Start the pipeline

The purpose of the pipeline is not the connect the elements, but to keep them running and give them a means to communicate with the bus as well as eachother.

Hence we link the elements.  Technically you can connect the elements to the pipeline after linking them.


## Turning on the Pipeline

Once you have setup the pipeline and are ready to go, you can activate it very easily with `set_state`.  Note that there are three states that a pipeline will traverse regularly.  Ready, Paused, and Playing.  It will **always** go to paused when changing between playing and ready.

Code:

    pipeline.set_state(Gst.State.PLAYING)


## Changing Settings at RunTime

When a pipeline is already playing you can only make certain changes, others will not work.

Changing the format, height, width, scaling, etc can all be done by simply updating the caps filter.  [Fortunately this is well documented](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-spoof-format.html#section-dynamic-format).

However, to swap elements you have to either stop the pipeline, or use a synchronous blocking callback to perform the swap.  If the stream is flowing when you disconnect an element, for example to swap elements in the pipeline, then you will get an error.  [More on dynamically changing a pipeline can be found in the documentation](http://gstreamer.freedesktop.org/data/doc/gstreamer/head/manual/html/section-dynamic-pipelines.html#section-dynamic-changing).


## Tips & Tricks

To use the ximagesink you have to be able to grab the xid from the GdkWindow each Gtk element is wrapped in.  Elements are only wrapped in Gdk windows on "realized", so you have to wait for that signal to fire first.  Second you need to import GdkX11: `from gi.repository import GdkX11`.

There may be an alternative way to attach video to a Gtk element, but I have not seen any modern examples nor have I had time to explore the Gst plugins library.


To use various elements you must initialize the GStreamer Library after the import with the `Gst.init(None)` method.  To avoid double initialization you can use `Gst.is_initialized() or Gst.init(None)`.


The ximagesink element implements the GstVideoOverlay interface, which gives it the `set_window_handle` method.  To have access to this method you must import GstVideo with Gst.


When changing caps at run-time you need a complete string, not a partial string, of the caps.  For example `caps = "video/x-raw,width=640,height=480,framerate=15/1"` will work, but `caps = "width=640,height=480"` will **not**.

Don't forget that FPS must be listed as a fraction, if you forget it the caps will fail to translate.

