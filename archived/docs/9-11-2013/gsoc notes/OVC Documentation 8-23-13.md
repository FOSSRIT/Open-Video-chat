
# OVC Documentation 8-23-13

Remaining Tasks:

- Finish network stack updates
- Implement some form of multi-user capabilities
- Begin farstream investigation & development
- Log output cleanup (change to info level and change key messages from debug to info)
- Documentation & Diagrams


### Refining the Network Stack

Last I left off I had implemented a new architecture for the network stack.  Since functionality is often asynchronous I created a custom callback registration and execution system, which allows clean independent additions of custom logic.

The design for signal dict should be string:signal mapping, but in the future we may consider switching to string:list[signal] mapping, if we need to recall multiple callbacks per named signal (unlikely with the current design).

Specification for the callbacks dict is string:list[callback], where the string is the name of an "event" we define.

At this point I need to continue moving forward in the cleanest way possible, despite the callback system I want to rely on it as little as possible.  Only when we really need external handling.

Working forward I need a `switch_active_account` method, and a `setup_active_account` method.  The second method will be modular and called by both initialize and switch methods.  It will also lead to the next step in setup, the connection object.

Revisiting the logic for my callback system, I realized a problem.  First if I want it to be flexible I should be doing what other systems do, providing the necessary data to remove the callback dynamically.  In the event of GTK signal connections we receive the object the signal was attached to first.

So our code needs to send the callback method as the first argument to the callback method (very meta?).  Ideally we should also be passing the event, and the parent of the method for access to other components.  Passing the parrent could be done from the callback execution, but in the likely event that we want to extrapolate it from the network stack we should consider passing it as the first argument when triggering the callback.

With these modifications I will now have to hold the code responsible for canceling callbacks that should only be executed once and re-registered as needed.

One other concern for the callbacks is passing the event that triggered them.  Not a big deal but a possible consideration for a third required argument.

With this change we can register callbacks from the parent ovc component and simply let the system run from there.  Callbacks sending the network_stack to other components will create a bit of crossed logic to execute required followup processes, but it will work better than standard dependency injection for this situation.


---

I have to do something about the GUI as well though, in particular two components of concern.

- Message System
- Contact List

I need a way to cleanly wipe out and reload contacts, as well as update them individually.  I also need a way to wrap and decorate the messages running through the message system.  This will involve some sort of intelligent iteration tracking, since changing older messages on asynchronous callbacks will effect the position of newer content.


### Fixing Log Output

I have built a bad habit of using debug for all messages, when ideally I want to mix them accordingly.  Using debug for verbose status, info for regular status, and of course warnings and errors where appropriate.

I need to go back through and make sure my log output is appropriate for all major components.


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

