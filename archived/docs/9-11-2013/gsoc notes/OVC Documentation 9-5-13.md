
# OVC Documentation 9-5-13

Today the project was saved by

- smcv
- xclaesse

They suggested that if other clients are running that they may catch the channels first.

The solution they recommended was to add an [Observer](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-simple-observer.html) or [Approver](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-simple-approver.html).

Here is our communication:

    16:23:33        CDeLorme | Can anyone explain why won't my [accepter](http://paste.fedoraproject.org/37131/13783260) catch my
                             | [offerer](http://paste.fedoraproject.org/37132/13783260)?
    Day changed to Thu, 05 Sep 2013
    06:27:07            smcv | CDeLorme: do you have another Text Handler, like Empathy? if you do, MC can't know that you'd prefer your accepter over Empathy's
    06:27:58            smcv | CDeLorme: workaround: add another matched property to the Handler filter, like Requested: False or TargetID: contact_id
    06:28:32            smcv | CDeLorme: (a Handler with more matching properties is considered to be a "better match")
    10:41:40        CDeLorme | smcv: I thought it was shared between clients, you're saying the system assigns priorities?  I did use Requested false, but I can't use
                             | target id for a receiver dynamically
    10:43:21        CDeLorme | I have empathy on the system, but it was closed.  The system itself is receiving the messages as gnome3 is showing this
    10:43:59        CDeLorme | I don't know through what client when it uses notifications
    10:45:35            smcv | CDeLorme: oh, sorry, yes, GNOME Shell is a text Handler too
    10:45:44            smcv | CDeLorme: each channel is handled by exactly one Handler (at a time)
    10:46:03            smcv | there's no particular priority system beyond "closest match"
    10:46:35            smcv | an Approver can instruct MC to make a particular Handler handle the channel - GNOME Shell's Approver might specify Shell as the Handler
                             | too
    10:47:23            smcv | what are you trying to achieve here?
    10:47:42            smcv | if you describe what you want to do with the channel I might be able to suggest how to do that
    10:48:13        CDeLorme | I am trying to build a video chat program, and it needs to be able to open text channels and call channels
    10:50:54            smcv | how is it meant to interact with Empathy/Shell?
    10:51:16            smcv | or is it not intended to run on the same system as them "in real life", and you're just doing development there?
    10:51:22        CDeLorme | It isn't, it's using TelepathyGLib, it just needs to accept incoming channels and messages
    10:51:44            smcv | well, it interacts with Empathy/Shell whether you like it or not, because they're sharing an IM connection
    10:51:47        CDeLorme | empathy came with the system I am testing on, (one of them)
    10:52:21            smcv | one possible way to interact with them is "it has its own notification of incoming things, and if you click on that, it accepts them
                             | itself"
    10:52:43            smcv | (i.e. stop Empathy/Shell from doing (some of) what they would normally do)
    10:53:13        CDeLorme | yeah, I don't click it, they popup though
    10:53:24        CDeLorme | even if I quit empathy
    10:53:38            smcv | the notification bubbles at the bottom of the screen are Shell's Approver
    10:53:45            smcv | your app could also be an Approver
    10:54:00            smcv | in which case you would have one "incoming $thing" notification from Shell, and one from your app
    10:54:06            smcv | and whichever one you click on, that's the Handler
    10:54:26        CDeLorme | I thought that was what the simplehandler was supposed to do, but I need an approver in front of it then?
    10:54:33            smcv | (or your app could even just say "yes I'll take it" noninteractively)
    10:54:43        CDeLorme | smcv: ^ that's what I want
    10:54:53            smcv | being a Handler means you are a possible UI for channels of this type
    10:54:58            smcv | note *possible*
    10:55:13            smcv | MC has to decide, somehow, whether to give the channel to you or to Empathy
    10:55:19        xclaesse | if you don't want interaction, the make an Observer and Claim every channel
    10:55:21            smcv | e.g. they can't both do the video streaming
    10:56:05            smcv | MC isn't very clever, so it doesn't know you think your app is better than Empathy
    10:56:11            smcv | something has to tell it :-)
    10:56:25        CDeLorme | Alright, so I can use an approver or an observer to do that?
    10:56:35            smcv | yeah
    10:56:45            smcv | the Observer/Approver and the Handler can be the same process
    10:56:54            smcv | (Shell is all three simultaneously, I think)
    10:57:02        CDeLorme | any examples of this out there you could point me to, or the object I should be checking out?
    10:57:12            smcv | be an Observer if you're being noninteractive, or an Approver if you're being interactive
    10:57:26            smcv | (there are timing implications - Observers are told first)
    10:57:40            smcv | Tp.SimpleObserver, Tp.SimpleApprover are a good start :-)
    10:57:57        CDeLorme | smcv: xclaesse excellent, I will give that a shot and see if I can figure it out.
    10:58:11        CDeLorme | Thanks for helping shed some light on what was causing this :)
    10:58:34            smcv | or subclass Tp.BaseClient and override its virtual methods (if your language allows that) and you can have both in the same object
    10:59:35        CDeLorme | Could this be the same reason I don't receive notifications on when contacts change?
    11:00:30        CDeLorme | it's a different problem to the one above, but `contact-list-changed` on TpConnection never triggers in my client either
    11:00:48        xclaesse | that's not related at all, no
    11:01:19        xclaesse | CDeLorme, you prepared TP_CONNECTION_FEATURE_CONTACT_LIST on your connection ?
    11:01:31        CDeLorme | yep, got the feature/quark codes on it
    11:01:36        CDeLorme | I can pull contacts, but they never update
    11:01:43            smcv | to claim channels, you want Tp.ChannelDispatchOperation.claim_with_async() (which is how you tell MC "I want this one")
    11:01:47        xclaesse | CDeLorme, check with dbus-monitor if the signal is emitted by the CM then
    11:01:58        xclaesse | CDeLorme, to check if the problem is CM-side or client-side
    11:02:18        CDeLorme | how can I check dbus-monitor for CM signals?
    11:02:41        CDeLorme | empathy displays notifications so I'm pretty sure that it works, unless they use a different CM
    11:02:50        CDeLorme | Are there more than one?
    11:03:32        xclaesse | just run dbus-monitor in a terminal, then check its messages to see if there is ContactListStateChanged signal when you add a contact
    11:03:56        xclaesse | ah, if empathy works then probably it's your code that doesn't work :p
    11:04:25        xclaesse | CDeLorme, oh maybe GPtrArray<TpContact> is not bindable in your language...
    11:04:32        xclaesse | for the signal args
    11:05:12        CDeLorme | xclaesse: that should be the same type as the dup_contacts method on the TpConnection though right?  Because duping existing contacts
                             | works, just can't tell when people join or exit the server
    11:05:43        xclaesse | yeah it's same type, but in a signal it could be a different code path... those things are never well tested :(
    11:06:05        xclaesse | at least, in a property it won't work
    11:06:18        xclaesse | it's not even annotable :(
    11:07:03        CDeLorme | I see, any idea how to test it, and should I open a bug report if the latter is the case?
    11:08:24        xclaesse | CDeLorme, you could check tp-glib debug messages and see if you get "roster changed: %d added, %d removed"
    11:08:52        xclaesse | Tp.debug_set_flags("all")
    11:09:21        xclaesse | and don't forget export G_MESSAGES_DEBUG=all in your terminal when you start your app
    11:10:58        CDeLorme | alright, thanks for the tips xclaesse

So, I create an Observer, tell it what to watch for, then claim the channels as they come in using [TpChannelDispatchOperation](http://telepathy.freedesktop.org/doc/telepathy-glib/telepathy-glib-channel-dispatch-operation.html).

---

So, using the temporary test code I am going to figure out how to add an observer and see if I can't override empathy and any other client running alongside it.

Setup the Observer and fail.

Asked in channel, and was told to [debug](https://wiki.gnome.org/Empathy/Debugging).

Also, to enable debugging in console:

    export G_MESSAGES_DEBUG=all

Then add this to the python application:

    Tp.debug_set_flags("all")

When run it will spit out a TON of data.

[Here](http://paste.fedoraproject.org/37360/97829137) is my test data.  I don't know how to read it, there are no "errors" and I'm not even sure what I should be looking for.

I was able to run `empathy-debugger` from console, and it opened a GUI.  There was nothing under mission control even when I stopped and started my observer code a dozen times.

Oddly, when I ran my observer code, it was an option in the drop-down with mission-control from the debugger.  However, when selected it said that the "Connection Manager" doesn't support the remote debugging extension.


---

I decided to run this test with the whole OVC software, and [here](http://paste.fedoraproject.org/37370/78399153/) were the results.  I sent and received messages (though not received through OVC), and the output doesn't have anything about contact list changing.

It does have a `message_received_cb`, but nothing logged or happened in my client.

I am just as lost as before, if not further because of the added complexity of forcing observers ontop of other applications.

Is it really this hard to setup a simple chat client?


---

In a spat of sheer brilliance I decided to add a `send_message_async` process to my test sender, and go figure suddenly my script is picking up channels.

I verified that the old SimpleHandler didn't change at all, so it definetally needs the observer, but until I sent an actual message it didn't actually see the channel?

[Here](http://paste.fedoraproject.org/37373/00086137) is the output.


---

Then `glassrose` said that I am not getting full debug output, and should run:

    pkill mission-control && G_MESSAGES_DEBUG=all MC_DEBUG=all /usr/lib/telepathy/mission-control-5

No dir `/usr/lib/telepathy`, so that's a no-go.

Apparently it is located in `libexec`:

    pkill mission-control && G_MESSAGES_DEBUG=all MC_DEBUG=all /usr/libexec/mission-control-5

This gives me full debug output to the console for mission control.  Excellent!

---

Back to the other situation I got errors for not accepting or declining the context, so I am going to work on getting that taken care of first.

Asking whether I need to "claim" channels or if I can just begin using them.

Well, I can now "obtain" channels, but I cannot own them and use them.  Waiting for a response in channel.


---

Back to the [fun documentation](http://telepathy.freedesktop.org/doc/book/appendix.source-code.glib_mc5_observer.example2.c.html), starting with checking how they use observer's in C, since python is clearly "too difficult" to make examples in.

In their `observe_channels` callback, they iterate the channels and:

- Get pending messages
- Prepare Async to handle (in their example "group" chat)
- Setup invalidate method
- Use context.delay() until the async channels have been processed?

So, there are two things I could be doing wrong.

- I don't have async's on channels AND
- I accept context too early OR
- I should delay context

So, I have about a half-dozen things to test now.

Running async worked on channels, I did not receive any errors using delay but I have a feeling I will.

Awesome, I can "acknowledge" received messages [according to the docs](http://telepathy.freedesktop.org/doc/book/sect.messaging.simple.html#sect.messaging.simple.receiving).

I managed to accomplish this, but I still can't retain the channel.

So I am back to [Incoming Channels](http://telepathy.freedesktop.org/doc/book/sect.channel.newchannels.html), and retaining them afterwards...

Well, that documentation is meaningless, but I looked again at TpChannelObserveOperation and cannot create a "new" one, I would have to get it from the channel from an async process.

I don't think that seems right, and would take a lot more garbage to test since I then do not know in what order to process async callbacks.

So instead I am looking up:

    101 (tp.py:10812): tp-glib/proxy-DEBUG: tp_proxy_invalidate: 0xe610a0: Proxy unreferenced

Which is the error I am getting.


---

More [fun reading](http://telepathy.freedesktop.org/doc/book/sect.channel.requesting.html), in here is describes the ContactList as a Channel Type, maybe we can add that to fix the live-updates to contacts?


---

Plans for the (future) chat engine that would handle decoration etc.

message - inserts a message and returns the iterators (start/end) of the message?  Accepts the message, and the textbuffer?
wrap_message - Accepts the text buffer, start/end iter's for a message, and the tag type & values to wrap with.

Concerns:

Async processing would break message wrapping if messages are received out of order.
To address this we need some kind of adjustment to make to identifying iter's?
Perhaps we store iter's and create our own identifiers for the messages inside the system?
Or is there a better way to track changes without heavy state monitoring?



---

List of things to do:

- Finish channels implementation for chat
- Merge & Close TelepathyGLib Feature Branch
- Update TelepathyGLib documentation with notes on specifics for the things I've just learned about contact-list-changed possible break, and the channels with multiple clients.
- Push gstreamer to repo
- Begin populating GStreamer documentation (Pretty simple stuff really)
- Rethink farstream, as it may not be needed (add info to doc & upload to repo)
- Fix Logging Messages Globally (Type specific error/warning/debug/info varying)
- Open gstreamer/farstream branch (depending on if farstream is going to be used)
- Implement video!
- Merge & Close
- Update Readme
- Update Primary Documentation File
- Clean & Upload all personal project documentation into the archives.

---

Notes on Calls:

TpCallChannel has a TpCallStream.
TpCallStream has a TpCallContent.

We can setup the TpCallChannel.
Get the TpCallStream.
And possibly Connect GStreamer to the TpCallStream or TpCallContent.

