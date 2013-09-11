
# OVC Documentation 8-22-13

Remaining Tasks:

- Finish Account Manager Feature Branch
- Finish network stack updates
- Implement some form of multi-user capabilities
- Begin farstream investigation & development
- Log output cleanup (change to info level and change key messages from debug to info)
- Documentation & Diagrams


### Account Manager Feature Branch

The important part is adding a cross-platform only method that loads the local accounts into the account manager.  It should then share the selected account with the account manager.

Despite the disarrayed state of the network stack (400+ lines, almost half being comments of working test code).  I still need to work on extrapolating sugar logic to the sugar ovc file from the network stack and setting up a proper callback system if time allows.

A temporary "quick-fix" might be to try a [duck-punching](http://en.wikipedia.org/wiki/Duck_punching) approach to cross-platform, where I can replace the setup process with a custom series of setup processes that chain to the original.

Although a more appropriate method would be to create a proper callback registration system with named events.  Then no actual changes need to be made to the network stack, it just iterates a series of registered callbacks at the given event.  However, this will take a bit of time to figure out the architecture fore.

At this point I have the account manager pulling in the list of accounts, but not selecting, changing, or populating the fields when clicked.  I will have to leave it as such until I have time to go back to it.

Then I can move onto finishing up some of the remaining network stack feature issues.


### Network Stack

As stated above, the network stack is in a state of disarray.  I have rebased develop into the TelepathyGLib feature branch to continue work from there.

Ideally I should backup the contents locally and wipe out the file.  Starting from scratch but employing all of the best methods I found during my tests to reconstruct the network stack one step at a time.

I need to add a dict for storing signals, custom event callbacks, and adding callback registration as a constructor argument.  With that I can eliminate the setup method and register system specific callbacks from the constructor, making it highly cross-platform capable.

With the signal connections I can easily disconnect to swap signals as needed.

I need to make the network setup process a bit more modular, such that a callback to send fresh accounts to the account manager can be stand-alone and not tied to every other area.  In fact, having the callback system allow registration of the classes own internal methods is not a bad idea to resolve this.  I would need to map out some of it before I try it to make sure the logic is sound.

The primary account will still default to the first available in the list.  I have not yet added, and may not have time to add, logic to select and activate different accounts, let alone create and delete them.

Other concerns include making sure that the contact list gets updated.

I guess my first step will be identifying all of the key module functions that need to be addressed, and then identifying how a callback system could be used to handle them.

Before closing this feature tree I want to make sure I can process incoming messages.  That will be enough to know I have "completed" my primary goals.





### Farstream Investigation

Starting with the issue:

[Use supplied source](https://github.com/FOSSRIT/Open-Video-chat/issues/22)

I need to review the 1000 lines of farstream source code and see if I can't make some sense of it.

I then have to begin testing passthrough of the onboard AND USB Webcam's for video communication.


### Documentation & Diagrams

At the one week mark, if not sooner, I absolutely need to stop coding and begin building all the missing documentation.

Going through the docs file I need to fully rewrite it to match the current code in the most sensible way possible.

I need to adjust the use cases for Sugar Users and Cross Platform Users, updating all available actions.

I also need to create activity diagrams that outline the logical flow for all the major actions.

If enough time and information is available I need to create sequence diagrams showing how each component interacts named according to the major actions/activity diagrams.

