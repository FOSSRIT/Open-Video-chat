
# OVC Documentation 7-30-13

Contact List test:

Add async to connection after connecting the signal.
I believe this was the flaw, leaving an async open is required, or restarting the asycn after each success maybe.

Created second machine, but cannot connect to jabber server from it, no idea why.
Test receiving open channels in the application.
Test receiving messages to get both sides of the system working.


Once I have a live contact list, and can catch and receive channel requests and messages I will be set to close this feature and merge to develop.


Future enhancements to note:

Enhanced messaging system with tags on text buffer for:

- Alternative system-message color and perhaps bold
- Color change on message received (by server)

Other cool ideas in the future release include


---

# ANOTHER BLOG POST


IRC Transcript with smcv in #telepathy.

<code><pre>

    12:18:33 CDeLorme | When I request a channel using python it creates a widget in gnome separate from my application.  How can I modify that behavior?            │ jonnylamb
    12:20:55 CDeLorme | I am also not sure I understand what the context object is for when I get the request back with the channel.                                 │ jrayhawk_
    12:22:19     smcv | CDeLorme: be a Handler for that type of channel, and use the create_and_handle() or ensure_and_handle() version of the API                   │ KA
    12:22:32 CDeLorme | yes I used the ensure_and_handle method
    12:23:03     smcv | the context is so you can call get_handler_info() on it if you want, ignore it if you don't                                                  │ abner
    12:23:17 CDeLorme | but I don't know if my code is working to "be" a handler.  The widget connects to my program, but it still shows in the notifications of the │ alasdair
                      | OS                                                                                                                                           │ albanc
    12:23:40 CDeLorme | smcv: ah ok that makes sense then (about the context)                                                                                        │ alexandernst_
    12:23:54     smcv | the point of telepathy is that every application can see the same channels/connections/etc.                                                  │ AmandaC
    12:24:32     smcv | so it's not unexpected that other things in the desktop see what's going on                                                                  │ andrunko
    12:24:54 CDeLorme | smcv: I see so that is entirely separate from the code I am writing then.  That works then.                                                  │ araujo
    12:25:14     smcv | ensure_and_handle_channel_async should be making your application the "preferred handler" though                                             │ barisione
    12:25:37     smcv | what channel type is it?                                                                                                                     │ bigon
    12:25:47 CDeLorme | Yep it is working for that, but I don't have a second machine setup to test from yet (working on setting that up now).                       │ boiko
    12:25:49 CDeLorme | It's a text channel                                                                                                                          │ burger
    12:26:15     smcv | ok                                                                                                                                           │ cassidy
    12:26:33 CDeLorme | I registered a private text channel with a simplehandler, but no second machine so not test cases yet.                                       │ CDeLorme
    12:26:35 CDeLorme | Thanks for the help.                                                                                                                         │ cyphermox
    12:26:46     smcv | being the preferred handler should mean that you don't get an Empathy or GNOME Shell chat window for it                                      │ d_ed_
    12:26:57     smcv | unless you are talking to an account that is also configured on the same machine                                                             │ danilocesar
    12:27:11 CDeLorme | smcv: any chance you know how to keep the contact list updated in python?  I tried listening for the ContactsChanged signal on the           │ Elleo
                      | connection but it said the signal does not exist.                                                                                            │ elmo
    12:27:16     smcv | if you have, say, alice@ and bob@ configured on the same machine                                                                             │ em-
    12:27:19 CDeLorme | smcv: yes the account is stored on the machine.                                                                                              │ erAck
    12:27:30     smcv | and you create a channel as alice, talking to bob                                                                                            │ felipe`
    12:27:49     smcv | when we receive bob's "new message" notification from the server                                                                             │ fledermaus
    12:27:58     smcv | we have no way to relate it to alice's end of the conversation                                                                               │ fredp
    12:28:24     smcv | so it'll be handled by whatever normally handles incoming text chat, which in GNOME means the Shell                                          │ fsimonce
    12:29:03     smcv | so you're in control of alice's end of the conversation but the Shell ends up in control of bob's end of the conversation (a different       │ fxrh
                      | Channel in a different Account)                                                                                                              │ geomyidae__
    12:30:02 CDeLorme | Currently pulling down a contact list to select a person on the jabber server to connect to                                                  │ gkiagia
    12:30:43     smcv | regarding the contact list: prepare the CONTACT_LIST feature on the Connection and look for the contact-list-changed signal                  │ hagabaka
    12:30:59 CDeLorme | ah ok, contact-list-changed is the name in python?                                                                                           │ Hei_Ku
    12:31:04     smcv | you can't connect to D-Bus signals directly when using python + g-i + telepathy-glib                                                         │ inz
    12:31:15     smcv | there is no dbus-python involved                                                                                                             │ jbos_
    12:31:31     smcv | (and the dbus-glib goo that does the D-Bus stuff is not introspectable for python)                                                           │ jjardon
    12:31:42     smcv | but you can use the higher-level API that telepathy-glib provides                                                                            │ jonner
    12:32:04 CDeLorme | Ah ok, I couldn't find documentation with the signals for python list, so I was trying whatever I found in the C code.                       │ jonnylamb
    12:32:17     smcv | contact-list-changed is what you should use in C code too                                                                                    │ jrayhawk_
    12:32:44     smcv | looking at the C documentation is often not a bad idea when using g-i                                                                        │ KA
    12:33:14     smcv | the python API for stuff is usually an automated 1:1 mapping of a subset of the C API                                                        │ KaKaRoTo
    12:33:57 CDeLorme | smcv: wow I feel like a fool, did not even notice the signals list in the docs.  Thanks for the tip
    12:37:42    kuuko | CDeLorme, I was working on a little telepathy client with python, haven't touched the code in a while but should be still relevant:          │ jonnylamb
                      | http://git.enlightenment.org/devs/kuuko/apathy.git/                                                                                          │ jrayhawk_
    12:39:22 CDeLorme | kuuko: thanks I will check it out for reference.                                                                                             │ KA
    13:18:34 CDeLorme | smcv: I forgot to ask, is there any references for what quarks add which features in python?                                                 │ KaKaRoTo
    13:22:48     smcv | CDeLorme: I don't think so, unfortunately. check the source code :-(

</pre></code>

Makes sense that since Telepathy channels are shared over DBus the system itself sees them, not just my software.  That is why the widgets are being displayed, and why they connect to my software when clicked.

Apparently I was not looking at the docs properly, because many objects do have signals listed.  The signal for contacts-updated and the method it ties to are both there, which is awesome news.  I now have a way to test updates to contacts on a connection.

Also, kuuko from irc recommended [an old project](http://git.enlightenment.org/devs/kuuko/apathy.git/) they were testing as a reference.  Said it should still be relative (eg. using modern tools).

Unfortunately I was also informed that there is no "easy" way to determine which features each quark refers to.



I had some followup communication after I had failed at getting the contact list signal to run:

<code><pre>

    09:13:25 xclaesse | CDeLorme, there is an example to get the contact list in python:                                                                             │ CDeLorme
                      | http://cgit.freedesktop.org/telepathy/telepathy-glib/tree/examples/client/python/contact-list.py                                             │ cyphermox
    10:03:43      --> | glassrose (~chandni@122.161.212.110) has joined #telepathy                                                                                   │ danilocesar
    10:09:18      <-- | zapb (~zapb@frbg-5d84f5c3.pool.mediaWays.net) has quit (Remote host closed the connection)                                                   │ dvratil
    10:29:52 CDeLorme | xclaesse: yes I can get the contact list, but I added a line to connect the connection to 'contact-list-changed' and it isn't being called.  │ Elleo
    10:30:05 CDeLorme | so I cannot get updates when people leave or join the server.                                                                                │ elmo
    10:30:40 xclaesse | CDeLorme, check with dbus-montitor if the signal goes through dbus                                                                           │ em-
    10:30:55 xclaesse | maybe it is a bug in the CM, or the server                                                                                                   │ felipe`
    10:31:13 xclaesse | CDeLorme, note that you won't get that signal for contacts going online/offline                                                              │ fledermaus
    10:31:22 xclaesse | only when you add/remove contacts from your roster                                                                                           │ fredp
    10:31:43 CDeLorme | xclaesse: oh, is there a signal when users join or leave the server?                                                                         │ fsimonce
    10:34:12 CDeLorme | or should I be polling the server regularly for an updated list?                                                                             │ fxrh
    10:35:11 xclaesse | what do you mean by 'join or leave the server' ?                                                                                             │ geomyidae__
    10:35:22 xclaesse | you mean connects/disconnect?                                                                                                                │ gkiagia
    10:35:42 CDeLorme | While I am connected to the jabber server, other users may join or leave, I want the list in my application to reflect that.                 │ glassrose
    10:36:18 xclaesse | you probably want to connect "presence-changed" signal on every TpContact                                                                    │ hagabaka
    10:36:24 xclaesse | and check if they are online/offline                                                                                                         │ Hei_Ku
    10:36:38      <-- | mlundblad (~marcus@gatekeeper.primekey.se) has quit (Ping timeout: 240 seconds)                                                              │ inz
    10:36:53 CDeLorme | Alright, and how about new contacts that have just joined and were not formerly in my list?                                                  │ jbos_
    10:38:39 xclaesse | that's contact-list-changed                                                                                                                  │ jjardon
    10:38:59 xclaesse | if you can list your initial contacts, it means that signal should be emitted                                                                │ jobstijl
    10:40:25 CDeLorme | hmm not sure I understand, the returned object was a list, and I attached them to a list in Gtk3, but that signal never fired even when      │ jonner
                      | other users were joining the jabber server                                                                                                   │ jonnylamb
    10:42:27 xclaesse | CDeLorme, run dbus-monitor in a terminal and check if you see the signal                                                                     │ jrayhawk_
    10:42:35 CDeLorme | I think I see what I did wrong, I don't think I left an async open on the connection, I'll have to give that a try.                          │ KA
    10:43:06 CDeLorme | xclaesse: thanks for your help, I will try the dbus-monitor as well.

</pre></code>

