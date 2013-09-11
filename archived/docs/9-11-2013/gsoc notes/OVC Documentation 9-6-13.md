
# OVC Documentation 9-6-13

Still trying to debug why I cannot keep channels and receive messages.

I am guessing the same thing is causing contact list changes to not be caught by my code.

Apparently handlers are not enough, you need to observe and override.

I have managed to observe, but not "override".

The biggest problem currently is:

    tp-glib/proxy-DEBUG: tp_proxy_invalidate: 0xe610a0: Proxy unreferenced

Which indicates that the channel has disappeared, cause unknown, despite pending messages still existing on it even.


---

smcv says I need to become the handler using the ChannelDispatchOperation object, but that object comes in as None everytime.

He also said to create a reference to the channels to prevent them from being discarded by the system.

So I will try adding the channels to a list this time.

However, I still don't have ownership of them, which is a serious concern.


---

Alright, figured it all out thanks to smcv's amazingly good explaination:

    13:18:31            smcv | CDeLorme: ok you have several orthogonal issues here, please bear with me
    13:18:40            smcv | CDeLorme: 1) refcounting channels
    13:18:58            smcv | CDeLorme: if you put them in a list or something, they won't disappear with "proxy unreferenced"
    13:19:23            smcv | CDeLorme: after they emit invalidated, they are basically useless and you should do whatever logging you want to do, then take them out
                             | of the list
    13:19:33            smcv | CDeLorme: 2) getting the operation object
    13:20:27            smcv | CDeLorme: you should expect to see a non-None operation object for "incoming" channels - i.e. the channel is initiated by someone
                             | elsewhere sending you a message
    13:21:01            smcv | CDeLorme: you will get operation=None if the channel is "outgoing", i.e. initiated by you clicking on someone in Empathy or whatever
    13:22:01            smcv | CDeLorme: for outgoing channels, whatever initiated the channel gets to decide who will be the handler - so Empathy says "me", whereas
                             | gnome-contacts probably says "I don't care, pick something sensible"
    13:22:32            smcv | CDeLorme: which is why I've asked you a couple of times who initiated the channel, because it's significant
    13:22:52            smcv | CDeLorme: 3) observers vs. approvers vs. handlers
    13:23:03            smcv | we probably have a diagram somewhere but I don't know where
    13:23:17            smcv | observers are a sort of client
    13:23:23            smcv | approvers are another sort of client
    13:23:29            smcv | handlers are the last sort of client
    13:23:40            smcv | and you can be more than one at a time (like multiple inheritance)
    13:24:02            smcv | when mission control sees a new channel, it "dispatches" it
    13:24:04            smcv | what that means is:
    13:24:17            smcv | first it checks for observers whose filter matches that channel
    13:24:34            smcv | it tells them all ObserveChannels()
    13:24:45            smcv | observers are typically loggers and things like that
    13:25:07            smcv | next, *if the channel is an incoming one*, it looks for approvers whose filter matches that channel
    13:25:22            smcv | and tells them all AddDispatchOperation()
    13:25:29            smcv | then it waits
    13:25:56            smcv | normally, each approver would be expected to pop up a notification bubble, or flash an icon, or something, to get the user's attention
    13:26:23            smcv | when the user responds to say "yes I want to talk to this person" or "no, stop bothering me", the approver reacts to that
    13:27:13            smcv | it either calls HandleWith() to say "pass this channel to this Handler"
    13:27:21            smcv | actually more like HandleWith("Empathy.Chat") or whatever
    13:27:35            smcv | or it calls HandleWith("") which means "I don't care, pass it to any Handler that looks appropriate"
    13:27:45            smcv | or it closes the channel
    13:28:32            smcv | now (finally), mission control chooses exactly one Handler, taking into account the approver's response, and calls HandleChannels() on
                             | it
    13:29:22            smcv | as an alternative to HandleWith(me), an Approver that is also a Handler can also call Claim(), which is a bit of a shorthand for "I'll
                             | take this one"
    13:29:46            smcv | you'll probably notice that I haven't described your situation
    13:30:44            smcv | we realized that if a client wants to force a particular handler non-interactively by being an approver, because it's told about the
                             | new channel at the same time as every other approver, the others all get to join in too
    13:30:58            smcv | so for instance Shell would pop up a notification bubble which would immediately disappear
    13:31:24            smcv | so, we put in a mechanism by which an Observer can "be like a non-interactive Approver"
    13:32:18            smcv | observers get called first, so if one of the observers says HandleWith() or Claim() before it tells mission control "ok, continue",
                             | approvers don't get a chance to join in
    13:32:30            smcv | (and mission control will skip calling approvers at all)
    13:33:00            smcv | but it can only do that for channels that would normally go to approvers, i.e. incoming ones
    13:33:38            smcv | for channels that would normally ignore approvers anyway, i.e. outgoing ones, the ChannelDispatchOperation isn't provided (so you get
                             | None)
    13:33:51            smcv | I hope that made things a bit clearer :-)
    13:35:10            smcv | perhaps I'll turn some of that into documentation next week
    13:35:40        CDeLorme | smcv: yes that is a very clear explanation.  I am sending messages from a second account on a second machine, but getting no operation
                             | object
    13:36:22            smcv | that's odd
    13:36:37            smcv | age of distribution / mission control version?
    13:36:48        CDeLorme | Fedora 19, mission-control 5 I believe?
    13:36:57            smcv | (telepathy-mission-control-5 on Debian/Ubuntu, package name may vary)
    13:38:14        CDeLorme | rebooting the VM to double check
    13:38:30            smcv | the number I want is something like "5.15.1"
    13:38:42            smcv | (which I know you don't have, because we haven't released it yet :-)
    13:39:47        CDeLorme | How would I check the sub-version numbers?
    13:39:54            smcv | hmm. in observe_channels, what is context.is_recovering()?
    13:40:19            smcv | or perhaps equivalently: if you change the True to False in Tp.SimpleObserver.new_with_am, does it work?
    13:40:45            smcv | you probably don't want Observer.Recover to be True for this use-case
    13:41:07            smcv | (the documentation for that parameter is terrible, I realize)
    13:41:28        CDeLorme | I will try with false and see
    13:42:01            smcv | if it's True it means "when I start up, try to let me 'catch up on what I've missed' by telling me all the channels that already exist"
    13:42:29            smcv | which seems undesirable if you're trying to be like a noninteractive approver
    13:42:50            smcv | and in particular there'll never be a ChannelDispatchOperation because those channels were already dispatched
    13:42:56        CDeLorme | booting the second machine to send a message again
    13:43:34        CDeLorme | Ah that would make total sense, because the shell pops up a window with the message before my program acknowledged it
    13:44:09            smcv | the Shell is probably also an Observer
    13:44:10        CDeLorme | I have been picking up pending channels and messages because I wasn't getting anything if I tried starting my software then sending the
                             | messages.
    13:44:16            smcv | also an Approver, also a Handler
    13:44:25            smcv | oh I see what's going on
    13:44:34            smcv | maybe
    13:45:06            smcv | Shell is being the Handler here, because you haven't implemented all the "claim it" stuff yet
    13:45:37            smcv | that means the same Channel stays open across multiple runs of your python code
    13:45:45            smcv | (after all, its Handler didn't exit, so why should it?)
    13:45:48        CDeLorme | which is wierd because I can still read pending messages, since I haven't yet acknowledged them through shell
    13:46:17            smcv | so: disconnecting/reconnecting before each attempt is probably a good scheme
    13:46:18        CDeLorme | so I'm guessing until I click it, it doesn't run through its approver?
    13:46:20            smcv | brb phone
    13:47:16            smcv | what I expect would happen is
    13:47:37            smcv | Shell has been notified in its Observer and Approver roles
    13:48:00            smcv | but until you click on the bubble, it hasn't Claimed the channel
    13:48:08            smcv | so it isn't officially that channel's Handler
    13:48:25            smcv | so it isn't meant to start acknowledging messages yet
    13:49:07            smcv | while you have a Channel open, any XMPP messages from the same contact just pile up in the same Channel
    13:49:15            smcv | so no new channel gets dispatched
    13:49:40            smcv | so no, you won't get a ChannelDispatchOperation
    13:49:44        CDeLorme | ok, when I set recover to False it doesn't trigger at all for incoming channels
    13:49:58        CDeLorme | it never fires the observer callback
    13:50:06            smcv | if you already had a channel open, then there is no incoming channel, only incoming messages
    13:50:13            smcv | (into the same channel)
    13:50:17        CDeLorme | I see, so I need to close the channel first.
    13:50:26            smcv | try disconnecting that IM connection, and re-connecting
    13:50:27        CDeLorme | I can do that by disconnecting?
    13:50:47            smcv | (which will close all its channels as a side-effect - channels never live longer than their parent connection)
    13:50:55            smcv | then send another IM
    13:51:07            smcv | that one should hopefully start a new Channel
    13:51:20            smcv | at which point your observer gets kicked
    13:51:30        CDeLorme | do I disconnect from both sides or just the one?  I tried setting offline and then available and sending, but shell continued to pickup
                             | the messages
    13:51:41            smcv | and gets a ChannelDispatchOperation, because this time, it isn't too late to influence how to dispatch it
    13:51:41             <-- | fsimonce (~simon@host210-6-dynamic.51-82-r.retail.telecomitalia.it) has quit (Quit: Coyote finally caught me)
    13:51:48            smcv | CDeLorme: disconnect the recipient
    13:52:01            smcv | (the one where you're running your python code)
    13:52:10        CDeLorme | Alright, got it!
    13:52:21        CDeLorme | This time I have the operation object
    13:52:26            smcv | a channel to the same sender can survive even when that sender disconnects and reconnects
    13:52:36            smcv | because its parent Connection is still up
    13:52:38        CDeLorme | smcv: you are a life-saver.  So at this point I can create a handler and pass that with claim?
    13:52:49            smcv | yep
    13:53:10        CDeLorme | Awesome, I'm going to give that a spin, I'll check back in a bit later.
    13:53:12            smcv |         # Perhaps I should be accepting right away?
    13:53:22            smcv | no, delay is right
    13:53:53            smcv | although if you have delay()ed the context, you still have to accept() or reject() it exactly once
    13:53:58            smcv | no more no less
    13:53:59        CDeLorme | Does the delay give us time to make sure we can grab the channel after prepare_async?
    13:54:17            smcv | the delay is for doing things like preparing the channel
    13:54:22        CDeLorme | so, I would say if prepare_finish accept, else reject?
    13:55:03            smcv | if prepare_finish fails, it doesn't really matter what you do - the channel isn't going to be dispatched either way, because it already
                             | died
    13:55:21        CDeLorme | The channels in the callback for the observer is a list, are there situations where a single context would apply to multiple incoming
                             | channels?
    13:55:29            smcv | there used to be
    13:55:49            smcv | if you have mission control 5.14 or later, not any more
    13:56:03            smcv | (it was really confusing and in practice nobody handled it correctly)
    13:56:57            smcv | "rpm -q telepathy-mission-control" might tell you which MC you have
    13:57:04            smcv | or telepathy-mission-control-5 or something
    13:57:11             <-- | kuuko (~kuuko@enlightenment/developer/kuuko) has quit (Quit: Leaving)
    13:57:36        CDeLorme | yep, 5.14.1-2.fc19
    13:57:41            smcv | good
    13:57:48            smcv | ok, so you can assume you will see exactly one channel
    13:57:53            smcv | which makes life a lot easier
    13:59:29            smcv | the point of the delay is: until you say "ok go" (or you crash or a timeout happens), mission control won't carry on dispatching
    14:00:21            smcv | and because you called set_observer_delay_approvers, "not carrying on" implies not calling approvers either
    14:00:29            smcv | -> no notification bubble from the Shell until you say so
    14:00:57        CDeLorme | This is making a lot more sense now
    14:01:07            smcv | so ideally, you want to not accept() until you've decided whether to claim the channel or let it go
    14:01:15            smcv | and if you wanted to claim it, started that process
    14:01:51            smcv | you must accept before waiting for claim to finish though, because the main thing that gets delayed is "giving channels to a Handler"
    14:02:09            smcv | and claim won't finish until the channel is given to you as a handler, so, deadlock
    14:02:17            smcv | (resolved by an arbitrary timeout)
    14:03:08            smcv | it is possible for claim_with_finish() to fail - if it does, then that means someone else got there first, and you're not the channel's
                             | handler after all
    14:03:46            smcv | (MC obeys whoever is first to tell it what to do)
    14:04:16            smcv | one thing you should watch out for before I stop work for the day: if you're using SimpleWhatever, they'll all need distinct names
    14:04:25            smcv | e.g. "MyApp.Handler"
    14:05:03        CDeLorme | Yeah I thought as much, also what about the Uniquify option?
    14:05:06            smcv | if you subclass BaseClient instead of using SimpleWhatever, then the down side is that you have to work out how pygi subclassing works,
                             | but you get them all nicely sharing a name
    14:05:17            smcv | uniquify also works
    14:05:29            smcv | it means: if you asked for Foo, you're actually Foo._1_42.1 or something
    14:05:51            smcv | constructed such that they can't clash
    14:06:23        CDeLorme | I see, so it prevents duplicate named handlers, such as starting the same software twice
    14:06:28            smcv | (but then your name is unpredictable, which might be fine, or might be annoying, depending whether you'll be interacting with other
                             | processes that want to refer to your app by name)
    14:07:00            smcv | well if you uniquify your SimpleHandler and your SimpleObserver, they also won't clash with each other
    14:07:43            smcv | there can only be one of each name on D-Bus
    14:07:59            smcv | uniquify means "give me a unique name, even if there's another instance of this same software already"
    14:08:30            smcv | as opposed to "I am the one true implementation of Empathy.Chat, the others are liars" which is what Empathy does :-)

Long right?  First time I think I've ever had someone walk me through something in such detail, it was wonderful.

So, the three components I've been dabbling with now fully explained.

Observers trigger first and are generally used for logging.  However they added the Operation object to allow you to use an observer to override who gets a channel.

The handler is what it must be attached to when using the `claim_with_async` operation.

Channels disappear when no references are kept to them, hence the **proxy unreferended** error I kept seeing.

Also because I had the "recover" option set to True in my code for the Observer, it was "catching up on old info" first.

The problem there is that the shell had already triggered an observer>handler chain, and while it had not claimed the channel I missed my chance to get the Operation object.

By setting recover to False, I only get new channels.  This meant I had to disconnect both sides to close the channel first, then reconnect, run my client program, then the sender.

This worked, and the operation object existed.

At this point it's about creating a handler and passing it to the operation object with a claim_with operation attached.

If all goes well this should be an easy weekend task.

The only pre-video concern I have left is whether I need to do something with the requested channels, or if my handler already has claim over them (which I would assume it does).

