
# Final Status (9-20-13)

For the final "Pencils Down" week I have been pushing to finish Telepathy Channels, and been told to use Farstream.

Conversations in #telepathy have clearly indicated that all examples are out of date, and it would become a game of translating.

Fortunately much has been learned from this (and they have been added to the various documentation files).

Unfortunately getting a functional call-channel caught by the other end and as a result working video is still incomplete.

At this point we are waiting on feedback from #telepathy (ocrete) regarding the Farstream GLib implementation.  My test code is finished but not functional, and I have no debug output to investigate.  Channels are being created, but nothing is being seen by the other end.

I have finished a complete demo of local GStreamer with dynamic pipeline changes, and individual element creation.  I have also fully documented it.


---

Remaining Bugs:

- How to receive call channels
- Picture in Picture with local video
- How to update the contact list
- How to acquire a contact-id off of a Sugar3 buddy objects

The demo code for a call channel with farstream is done, no errors, and the pipeline supposedly starts up.  Feedback required from #telepathy.

Getting picture in picture using a videobox should be possible, but I have not had time to test it.

The TelepathyGLib Connection object never triggers it's "contact-list-changed" signal, and as a result we have no information regarding users that have recently logged into the server.

The sugar3 system uses their presence service which is still telepathy based (not TelepathyGLib), and their custom buddy objects only carry a nickname that I could tell.  While nicknames could be used there are potential name conflict problems, and contact-not-found (because the contact list never updates).


---

The contact list problem is not native to TelepathyGLib either, I have found that even sugar itself rarely updates the contact list.  In fact if I boot two machines, the first cannot see the second, but the second can see the first, and communication is only possible in one direction.

**If Bob logs in before Alice, Alice will be able to see Bob but Bob will not be able to see Alice.**

The same symptoms apply to the contact list in the OVC software.


---

[Buddy Docs](http://doc.sugarlabs.org/epydocs/sugar.presence.buddy-pysrc.html), shows that no properties with the contact-id exist.


---

I have updated the readme, added demo code that should make implementing the changes easier for the next interested development party.

I feel comfortable bringing this project to a close due with the remaining time being in the negatives.
