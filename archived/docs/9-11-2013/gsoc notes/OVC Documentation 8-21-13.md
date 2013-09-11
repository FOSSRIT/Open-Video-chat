
# OVC Documentation 8-21-13

Remaining Steps:

- Add new icons to toolbars
- Account Management GUI
- Multiple Channels
- Farstream
- Documentation
- Diagrams

_I don't expect to have enough time to complete all the issues in the issue tracker, and possibly even the items above._


### Toolbar Icons

- Create a local-only feature branch.
- Export/Add/Swap the new icons.
- Merge to Devel.


Sugar uses 55px icons.
Other uses 24px icons.

All done, and toolbar code has been updated.

Next step will have me integrating the new Account Management GUI.


### Account Management GUI

Switch back to feature branch and finish general UI layout:

- List of Accounts
    - Indicator for active account
    - Double click to change active account
- Add and Delete Buttons
    - No functionality yet
- Account Info area with name, server, and password fields

So long as the non-sugar toolbar has a working button to swap to the account management screen, and the user can switch active accounts, that will be enough for now.

Network stack needs to feed in local user accounts to the Account Management GUI.

Toolbar needs to swap grids somehow.

_I will omit the functionality of creating, deleting, and editing accounts for future iterations._

Discovered that GtkLabel text alignment with the justify property alone doesn't work.  Need to use halign and GtkAlignSTART.

Also, in order to retain access to the toolbar the gui which formerly held direct access to the toolbar had to have it stripped away and re-implemented the sugar-way, in order to retain access to the button to switch between the account management grid.


**Problems Remaining to tackle before I can close the feature branch into develop:**

- Dialog handling needs to be modified to adjust how it is attached due to toolbar relocation
    - No current instances of dialog have been implemented but we will want it when we add video comm
- Fixing network abstraction between sugar and cross platform for loading accounts async
    - Sugar edition supplies owner and buddy to constructor, non-sugar will need to suppliy async account loader
        - Possible solution is to remove constructor arguments and instead use external setup method and individual setters

I also need to begin adding the sugar-specific logic, or at the very least finalizing where that logic should be placed, whether in the network stack or in the sugar_ovc file.


### Multiple Channels

Determine best route for handling multiple open channels for chat:

1. Shared Text Buffer with Selected User as Send Target?
2. Tabs with separated buffers per user?
3. Selected Users dynamically create & swap buffers (stored in ListStore)

**Look at Sash for how to save to datastore to retain message data for multiple accounts.**

Post Issue to Sash for future:

    Sash should not have a list of known compatible applications.
    Instead, you should define a specification for Badge compatibility, in a way that Sash can dynamically scan for and automatically import compatible activities.
    This could be as simple as recursively checking for a badges folder in ~/Activities/
    Alternatively having every activity write to a shared datastore that Sash uses to generate symlinks (???)


### Farstream

I need to try to finish getting working video, at least in the development environments.

Provided I can get that working I will be pleased.

[Use supplied source](https://github.com/FOSSRIT/Open-Video-chat/issues/22)

The question is whether I still need to generate GStreamer pipelines manually or if this abstracts their creation.


### Documentation

I need to document all the success-only details.  Ideally I want to provide people the correct path without any side-tracking like my daily-documentation carries with it.

Once we approach the one week remaining mark, I will take the current build and reconstruct the system documentation to match.

I will then add documentation on services used to explain how they work for the next developers who choose to pick this project up.


### Diagrams

I want to get at the very least logical flowcharts (eg. activity diagrams) of the system working.

I should update the use case diagram to account for the new changes in the system.  We have a Sugar User and a User now, with slightly varies situations.

I want to create sequence diagrams once I have a basic understanding of the activity diagrams and the

