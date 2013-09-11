
# OVC Documentation 8-24-13

Despite it being a weekend, I decided to finish up some loops so I could close this chapter a bit sooner.

Here are the tasks:

- Refining the Network Stack
- Fixing Log Output
- Farstream Investigation
- Readme, Documentation & Diagrams

### Refining the Network Stack

Working on pulling in the contact list, and being notified of changes to it.  Having some trouble thinking of a cleaner way to establish the connection logic in a modular way.

Well, it appears thatt he contact-list-changed signal fails to fire, reasons unknown.  I've left a message in telepathy, I don't expect a favorable response since no examples show a different approach and there are almost no google results for the question.

Alrighty, got kuuko checking it out, they built the apathy source I've been working from.  Hopefully they can lend me a trained eye.  That's a bust, tried adding GObject threads, no changes.  I have to assume it's something else.  I could add signals to every user account, but that feels... messy?

Well, we tried and no luck so I'm going to skip right on past a live contact list for now.  The only options I have would be to run a 5 second interval and refresh the list, but afaik empathy which comes with the newest systems and runs telepathy also doesn't have this functionality working.  I want to say contact-list-changed is a broken signal in current implementations, since it doesn't appear to be working elsewhere.  I have now tried in Debian Wheezy, Jessi, Fedora 19, and Sugar on Fedora 19 and sugar-build on Jessie.  Same behavior.

If I can finish cleaning up the design and work around the rest that'll be plenty enough.  I could also add a detection on the availability so if existing people suddenly drop out it'll remove them from the visible list of contacts.  status-changed per person signal, seems like it'd eat cpu but we'll see.


### Fixing Log Output

I have built a bad habit of using debug for all messages, when ideally I want to mix them accordingly.  Using debug for verbose status, info for regular status, and of course warnings and errors where appropriate.

I need to go back through and make sure my log output is appropriate for all major components.


### Farstream Investigation

Starting with the issue:

[Use supplied source](https://github.com/FOSSRIT/Open-Video-chat/issues/22)

I need to review the 1000 lines of farstream source code and see if I can't make some sense of it.

I then have to begin testing passthrough of the onboard AND USB Webcam's for video communication.

# Readme, Documentation & Diagrams

I have to update the readme with new features, instructions, and installation details.

I have to open issues for all incomplete-but-planned features.

I have to fully update the detailed external documentation.

I should update the use cases for sugar user vs non-sugar user.

I need to create activity diagrams to map logical flow.

I should create sequence diagrams to map object communication.
