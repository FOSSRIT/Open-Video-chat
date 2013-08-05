#    This file is part of OpenVideoChat.
#
#    OpenVideoChat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OpenVideoChat is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OpenVideoChat.  If not, see <http://www.gnu.org/licenses/>.
"""
:mod: `OpenVideoChat/OpenVideoChat.activity/network_stack` --
        Open Video Chat Network Stack (Non-Sugar)
=======================================================================

.. moduleauthor:: Justin Lewis <jlew.blackout@gmail.com>
.. moduleauthor:: Taylor Rose <tjr1351@rit.edu>
.. moduleauthor:: Fran Rogers <fran@dumetella.net>
.. moduleauthor:: Remy DeCausemaker <remyd@civx.us>
.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# External Imports
import logging
from gi.repository import TelepathyGLib as Tp


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NetworkStack(object):

    def __init__(self, owner=None, get_buddy=None):
        logger.debug("Preparing Network Stack...")

        # Network Components
        self.account_manager = None
        self.account = None
        self.connection = None

        # Channels for chat, stream, and commands
        # self.chat_channel = None
        # self.stream_channel = None
        # self.command_channel = None

        """ Sugar Specific Handling """

        # Assign owner if exists (???)

        # Assign buddy callback if exists (???)

        # Grab Account Details
        self.prepare_account()

        # Completed
        logger.debug("Network Stack Initialized")

    def prepare_account(self):
        logger.debug("Preparing account asynchronously...")

        # Grab the account manager
        self.account_manager = Tp.AccountManager.dup()

        # Grab the ambiguous factory object
        factory = self.account_manager.get_factory()

        # Add features to the shared abstract factory (used by all components)
        factory.add_account_features([
            Tp.Account.get_feature_quark_connection()            # Pull the connections for the accounts
        ])
        factory.add_connection_features([
            Tp.Connection.get_feature_quark_contact_list(),      # Get the contact list as a "feature"
            Tp.Connection.get_feature_quark_contact_groups(),    # Contact Groups?
            Tp.Connection.get_feature_quark_contact_blocking(),  # Contact Blocking?
        ])
        factory.add_contact_features([
            Tp.ContactFeature.ALIAS,                             # Get contact ALIAS's from system
            Tp.ContactFeature.CONTACT_GROUPS,                    #
            Tp.ContactFeature.PRESENCE,                          #
            Tp.ContactFeature.AVATAR_DATA,                       #
            Tp.ContactFeature.SUBSCRIPTION_STATES,               #
            Tp.ContactFeature.CAPABILITIES,                      #
            Tp.ContactFeature.CONTACT_INFO,                      #
            Tp.ContactFeature.LOCATION,                          #
            Tp.ContactFeature.CONTACT_BLOCKING,                  #

        ])

        # Wait for the account to be ready to ensure the channel
        self.account_manager.prepare_async(None, self.setup_accounts, None)

    def setup_accounts(self, account_manager, status, data):
        logger.debug("Setting up asynchronous stack components...")

        # Cease waiting on async event from account_manager
        self.account_manager.prepare_finish(status)

        # Grab accounts into locally stored list
        self.accounts = []
        for account in self.account_manager.dup_valid_accounts():
            if account.get_protocol() == "jabber":
                self.accounts.append(account)

        # If no accounts were found exit and notify
        if len(self.accounts) == 0:
            logger.debug("No accounts found...")
            # **FIXME** Add alert to UI and open the account manager
            return False

        # Attempt to find an enabled & connected account
        for account in self.accounts:
            if self.account is None and account.is_enabled and account.get_connection_status() is Tp.ConnectionStatus.CONNECTED:
                self.account = account
        if self.account is None:
            logger.debug("No enabled and connected accounts found...")
            # **FIXME** Add alert to UI and open the account manager
            # return False

        # **FIXME** Future iterations will not automatically use the first account
        #           Subsequently, no automatic connection logic will be required either
        self.account = self.accounts[0]
        if not self.account.is_enabled():
            logger.debug("TEMP: Enabling account...")
            self.account.set_enabled_async(True, self.enable_account_callback, None)
        elif self.account.get_connection_status() is not Tp.ConnectionStatus.CONNECTED:
            self.change_account_presence_available()
        else:
            logger.debug("TEMP: Connecting...")
            self.account.prepare_async(None, self.setup_connection_logic, None)

    def enable_account_callback(self, account, status, data):
        logger.debug("Account is now enabled")
        account.set_enabled_finish(status)
        self.change_account_presence_available()

    def change_account_presence_available(self):
        logger.debug("TEMP: Connecting async...")
        self.account.request_presence_async(Tp.ConnectionPresenceType.AVAILABLE, "", "", self.force_connect_callback, None)

    def force_connect_callback(self, account, status, data):
        logger.debug("User is now available")
        account.request_presence_finish(status)

        # Async into the connection logic
        self.account.prepare_async(None, self.setup_connection_logic, None)

        # Call connection handling
        # self.setup_connection_logic()

    def setup_connection_logic(self, account, status, data):
        logger.debug("Setting up the connection components...")

        # Kill async process
        account.prepare_finish(status)

        print account.get_connection()

        # Grab the connection from our account
        connection = account.get_connection()

        # If connection is (ever) None at this stage we have done something wrong
        if connection is None:
            logger.critical("Connection should not be none!")
            return False

        # Dup contact list & begin populating the UI user list
        if connection.get_contact_list_state() is Tp.ContactListState.SUCCESS:
            self.populate_users_list(connection.dup_contact_list())

        # Connect handler for contact list
        connection.connect('contact-list-changed', self.contacts_changed_callback)

        # Setup async on connection to handler changes to contact list
        connection.prepare_async(None, None, None)
        # **FIXME** Perhaps this needs to be closed later?  How can we do that?  Handler that stores gasyncresult object for running finish?
        # Also does this handle more than one contact-list-changed event or just one per?  In which case closing and re-opening in an "infinite" loop is good

        # Listen for incoming channel requests
        # self.listen_for_chat_channel()

        """ Sugar handling for if connection established through sugar sharing process """

    def populate_users_list(self, contacts):
        logger.debug("Adding contacts to gui...")

        for contact in contacts:
            self.add_user_to_gui(contact)

        logger.debug("Sent users to gui")

    def contacts_changed_callback(self, added, removed, data):
        logger.debug("Contacts have been updated!!!")
        logger.debug(added)
        logger.debug(removed)

    # def listen_for_chat_channel(self):
    #     logger.debug("Listening for incoming connections...")

    #     # Define handler for new channels
    #     self.chat_handler = handler = Tp.SimpleHandler.new_with_am(
    #         self.account_manager,              # As specified in the method name
    #         False,                             # bypass approval (dbus related)
    #         False,                             # Whether to implement requests (more work but allows optional accept or deny)
    #         "ChatHandler",                     # Name of handler
    #         False,                             # dbus uniquify-name token
    #         self.chat_channel_setup_callback,  # The callback
    #         None                               # Custom data to pass to callback
    #     )

    #     # Describe the channel (a chat channel)
    #     handler.add_handler_filter({
    #         Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
    #         Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
    #         Tp.PROP_CHANNEL_REQUESTED: False,
    #     })

    #     # Register the handler
    #     handler.register()

    #     logger.debug("Now listening for incoming chat requests...")

    def setup_chat_channel(self, contact):
        logger.debug("Setting up outgoing chat channel...")

        # Call Channel closure for previously opened channels
        self.close_chat_channel()

        # Remove handler for listener, since we are establishing the connection ourselves
        if self.chat_handler is not None:
            self.chat_handler.unregister()
            self.chat_handler = None

        # Describe the channel type (text)
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_TARGET_ID: contact.get_identifier()              # Who to open the channel with
        }

        # Private channels are not named, only group channels (MUC for Multi-User Channel)
        # Because they are not named, only one can exist at a time
        # This also means that `ensure` is better than create in this case

        # Request the channel
        request = Tp.AccountChannelRequest.new(
            self.account,                              # Account
            channel_description,                       # Dict of channel properties
            Tp.USER_ACTION_TIME_NOT_USER_ACTION        # Time stamp of action (0 also works)
        )

        # Run this asynchronously
        request.ensure_and_handle_channel_async(
            None,                              # Whether it can be canceled
            self.chat_channel_setup_callback,  # Callback
            None                               # Custom Data for callback
        )

    # def handler_chat_channel_setup_callback(
    #     self,
    #     handler,
    #     account,
    #     connection,
    #     channels,
    #     requests,
    #     user_action_time,
    #     context,
    #     loop
    # ):
    #     logger.debug("SimpleHandler received request for channel...")

    #     # Limit chat to one-on-one by unregistering the handler
    #     # if self.chat_handler is not None:
    #     #     self.chat_handler.unregister()
    #     #     self.chat_handler = None

    #     # for channel in channels:
    #     #     if not isinstance(channel, Tp.StreamTubeChannel):
    #     #         continue

    #     #     print "Accepting tube"

    #     #     channel.connect('invalidated', tube_invalidated_cb, loop)

    #     #     channel.accept_async(tube_accept_cb, loop)

    #     # context.accept()

    def close_chat_channel(self):
        logger.debug("Closing any existing chat channels...")

        if self.chat_channel is not None:
            # Try async with lambda to catch & finish
            self.chat_channel.close_async(
                lambda c, s, d: c.close_finish(s) and logger.debug("Existing channel closed"),  # Callback
                None                                                                            # User Data
            )

    def chat_channel_setup_callback(self, request, status, data):
        logger.debug("Chat channel approved and initiating...")

        # Remove async process & grab channel plus context
        (channel, context) = request.ensure_and_handle_channel_finish(status)

        # Call shared-setup process
        self.process_chat_channel_setup(channel)

    def process_chat_channel_setup(self, channel):

        # Assign channel to class variable
        self.chat_channel = channel

        # Add listener for received messages
        channel.connect('message-received', self.chat_message_received)

        # Activate Chat Services
        self.activate_chat()

    def send_chat_message(self, message, message_type=Tp.ChannelTextMessageType.NORMAL):
        logger.debug("Sending a message over the wire...")

        # Verifiy connection status before trying to send a message
        if self.account.get_connection_status() is not Tp.ConnectionStatus.CONNECTED:
            logger.debug("Disconnected, cannot send a message")
            # **FIXME** Add handling to message user that they are disconnected and no message could be sent
            return False

        # Wrap our message in a Telepathy Message object
        message_container = Tp.ClientMessage.new_text(message_type, message)

        # Send asynchronous message
        self.chat_channel.send_message_async(
            message_container,  # Telepathy ClientMessage object
            0,                  # Optional Message Sending Flags
            None,               # Callback (server-received confirmation)
            None                # Data for callback
        )

        # The message sending flags are numeric constants representing features
        # currently these include delivery, read, and deleted confirmation
        # The numeric representation uses bit-mapping increments (1, 2, 4, etc)
        # in this way 3 represents the combination of 1 + 2, or two-enabled features

        # Technically, they are missing a NONE constant to represent 0
        # hence why supplying 0 is the same as saying "use no features"
        # and supplying None will throw an error

        # **Also** server callback is not the same as user-delivery confirmation

    def chat_message_received(self, channel, message):
        logger.debug("Processing received message...")

    def set_chat_activation(self, callback):
        logger.debug("Defined chat activation in network stack...")
        self.activate_chat = callback

    def set_populate_users(self, callback):
        logger.debug("Adding callback to add users to gui...")
        self.add_user_to_gui = callback

    """ Old Code (Deprecated & scheduled for removal after testing) """

    # def setup(self, activity, get_buddy):
    #     # Grab Shared Activity Reference
    #     self.shared_activity = activity.shared_activity

    #     # Add get_buddy reference
    #     self.get_buddy = get_buddy

    #     # Grab Username & Apply Owner
    #     self.owner = activity.owner
    #     if self.owner.nick:
    #         self.username = self.owner.nick

    # def close(self):
    #     # Delete Telepathy Connection Reference
    #     self.chan = None
    #     # try:
    #     #     if self.chan is not None:
    #     #         self.chan[CHANNEL_INTERFACE].Close()
    #     # except Exception:
    #     #     logger.debug("Unable to close channel")
    #     # finally:

    # def connect(self, receive_message_callback):
    #     logger.debug("Creating Connection")

    #     # Assign Callback for Receiving Messages
    #     self.receive_message_callback = receive_message_callback

    #     # Acquire Channel and Connection
    #     self.chan = self.shared_activity.telepathy_text_chan

    #     # Assign Callbacks
    #     self.chan[CHANNEL_INTERFACE].connect_to_signal(
    #             'Closed',
    #             self.close)
    #     self.chan[CHANNEL_TYPE_TEXT].connect_to_signal(
    #             'Received',
    #             self.receive_message)

    # def send_message(self, message):
    #     if self.chan is not None:
    #         self.chan[CHANNEL_TYPE_TEXT].Send(
    #                 CHANNEL_TEXT_MESSAGE_TYPE_NORMAL,
    #                 message)

    # def receive_message(self, identity, timestamp, sender, type_, flags, message):
    #     # Exclude any auxiliary messages
    #     if type_ != 0:
    #         return

    #     # Get buddy from main
    #     buddy = self.get_buddy(sender)
    #     if type(buddy) is dict:
    #         nick = buddy['nick']
    #     else:
    #         nick = buddy.props.nick

    #     # Send Message if callback is set & buddy is not self
    #     if self.receive_message_callback is not None and buddy != self.owner:
    #         self.receive_message_callback(nick, message)

    #     # Empty from pending messages
    #     self.chan[CHANNEL_TYPE_TEXT].AcknowledgePendingMessages([identity])
