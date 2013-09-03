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

# Initialize threads for telepathy?
from gi.repository import GObject
GObject.threads_init()

from gi.repository import TelepathyGLib as Tp


# Define Logger for Logging & DEBUG level for Development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NetworkStack(object):


    """ Properties """
    active_account = None
    active_connection = None


    def __init__(self, callbacks={}):
        logger.debug("Preparing Network Stack...")

        # Create dicts for signals and callbacks
        self.network_stack_signals = {}
        self.network_stack_callbacks = callbacks

        # Grab the account manager to begin the setup process
        self.account_manager = Tp.AccountManager.dup()
        if self.account_manager:
            self.configure_network_stack(self.account_manager)

            # Register initial callbacks
            self.register_callback('get_jabber_accounts', self.initialize_account)
            self.register_callback('setup_active_account', self.initialize_connection)

            # Run first async process to startup the system
            self.account_manager_async()

        else:
            logger.error("Unable to acquire the account manager, software will not be usable...")

        logger.info("Network Stack Initialized")

    def configure_network_stack(self, account_manager):
        logger.debug("Configuring Telepathy...")

        # Grab the ambiguous factory object
        factory = account_manager.get_factory()

        # Add features to the shared abstract factory (used by all components)
        factory.add_account_features([
            Tp.Account.get_feature_quark_connection()            # Pull the connections for the accounts
        ])
        factory.add_connection_features([
            Tp.Connection.get_feature_quark_contact_list(),      # Get the contact list as a "feature"
        ])
        factory.add_contact_features([
            Tp.ContactFeature.ALIAS,                             # Get contact ALIAS's from system
        ])

        logger.debug("Configured Telepathy")

    def account_manager_async(self):
        logger.debug("Processing account manager async...")
        self.account_manager.prepare_async(None, self.account_manager_async_callback, None)

    def account_manager_async_callback(self, account_manager, status, data):
        logger.debug("Finishing account manager async...")
        account_manager.prepare_finish(status)

        # Run Jabber Accounts
        self.get_jabber_accounts(account_manager)


    """ Account Logic """

    def get_jabber_accounts(self, account_manager):
        logger.debug("Getting jabber accounts list...")

        accounts = []
        for account in account_manager.dup_valid_accounts():
            if account.get_protocol() == "jabber":
                accounts.append(account)

        # Handle Registered Callbacks & remove them after
        self.run_callbacks('get_jabber_accounts', self, accounts)

    def initialize_account(self, callback, event, parent, accounts):
        # This should only ever run once
        self.remove_callback(event, callback)

        for account in accounts:
            if self.active_account is None and account.is_enabled() and account.get_connection_status()[0] is Tp.ConnectionStatus.CONNECTED:
                self.active_account = account

        if self.active_account:
            self.setup_active_account()
        else:
            logger.warning("No enabled and connected accounts were found...")

    def switch_active_account(self, account):
        logger.debug("Switching accounts...")

        # Logic chain to automatically enable and connect account
        if account.is_enabled() and account.get_connection_status()[0] is Tp.ConnectionStatus.CONNECTED:

            # Check for & remove a status-changed signal from the former account
            if 'account_status_changed' in self.network_stack_signals and self.network_stack_signals['account_status_changed'] is not None:
                self.active_account.disconnect(self.network_stack_signals['account_status_changed'])

            self.active_account = account
            self.setup_active_account()

        elif not account.is_enabled():
            logger.warning("Attempting to enable account...")
            account.set_enabled_async(True, self.enable_active_account_callback, account)

        elif account.get_connection_status()[0] is not Tp.ConnectionStatus.CONNECTED:
            logger.warning("Attempting to connect (set account available)...")
            account.request_presence_async(Tp.ConnectionPresenceType.AVAILABLE, "", "", self.connect_active_account_callback, account)

        else:
            logger.warning("Unable to select account...")

    def enable_active_account_callback(self, account):
        if account.is_enabled():
            self.switch_active_account(account)
        else:
            logger.error("Unable to activate account!")

    def connect_active_account_callback(self, account):
        if account.get_connection_status()[0] is Tp.ConnectionStatus.CONNECTED:
            self.switch_active_account(account)
        else:
            logger.error("Unable to connect!")

    def setup_active_account(self):
        logger.debug("Configuring Active Account...")

        # The account should have a status-changed signal, connect to it here
        self.network_stack_signals['account_status_changed'] = self.active_account.connect(
            'status-changed',
            self.update_active_account_status
        )

        # Run callbacks
        self.run_callbacks('setup_active_account', self, self.active_account)

    def update_active_account_status(
        self,
        account,
        old_status,
        new_status,
        reason,
        dbus_error_name,
        details
    ):
        logger.debug("Account status changed...")
        # No logic or handlers have been added here yet


    """ Connection Logic """

    def initialize_connection(self, callback, event, parent, account):
        logger.debug("Initializing connection...")

        # Grab the connection
        connection = account.get_connection()

        if connection:

            # Remove signal from old connection
            if 'contact_list_changed' in self.network_stack_signals:
                self.active_connection.disconnect(self.network_stack_signals['contact_list_changed'])

            # Update connection
            self.active_connection = connection

            # Setup Connection
            self.connection_setup()

            logger.debug("Connection Initialized")

        else:
            logger.error("Unable to acquire connection...")

    def connection_setup(self):
        logger.debug("Setting up connection...")

        # Wipe out the previous contacts array
        self.run_callbacks('reset_contacts', self)

        # Dup Contacts
        contacts = self.active_connection.dup_contact_list()

        # Send to the contacts add/remove method
        self.contacts_add_remove(contacts, None)

        # Connect Signal for future changes to the list
        self.network_stack_signals['contact_list_changed'] = self.active_connection.connect(
            'contact-list-changed',
            self.contacts_add_remove
        )

        # Begin listening for chat messages
        self.listen_for_incoming_chat()

        logger.debug("Connection Established")

    def contacts_add_remove(self, added, removed, *args):
        logger.debug("Received change to contacts...")

        # Update the locally kept contact list(s)?

        # Run callback for changes to the contact list
        self.run_callbacks("contacts_changed", self, added, removed)

    """ Chat Channel Logic """

    def create_chat_channel(self, contact):
        logger.debug("Setting up outgoing chat channel...")

        # Describe the channel type (text)
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_TARGET_ID: contact.get_identifier()              # Who to open the channel with
        }

        # Request the channel
        request = Tp.AccountChannelRequest.new(
            self.account,                              # Account
            channel_description,                       # Dict of channel properties
            Tp.USER_ACTION_TIME_NOT_USER_ACTION        # Time stamp of action (0 also works)
        )

        # Run this asynchronously
        request.ensure_and_handle_channel_async(
            None,                              # Whether it can be cancelled
            self.create_chat_channel_callback, # Callback to run when done
            None                               # Custom Data sent to callback
        )

        # Private channels are not named, only group channels (MUC for Multi-User Channel)
        # Because they are not named, only one can exist at a time
        # This also means that `ensure` is better than create in this case

    def create_chat_channel_callback(self, request, status, contact):
        logger.debug("Chat channel approved and initiating...")

        # Remove async process & grab channel plus context
        (channel, context) = request.ensure_and_handle_channel_finish(status)

        # Run shared setup process
        self.setup_chat_channel(contact, channel)

    def setup_chat_channel(self, contact, channel):

        # Run Registered Callbacks
        self.run_callbacks("setup_chat_channel", contact, channel)

        # Add listener for received messages
        channel.connect('message-received', self.receive_chat_message, contact)

    def listen_for_incoming_chat(self):
        logger.debug("Listening for incoming connections...")

        # Define handler for new channels
        self.chat_handler = handler = Tp.SimpleHandler.new_with_am(
            self.account_manager,              # As specified in the method name
            False,                             # bypass approval (dbus related)
            False,                             # Whether to implement requests (more work but allows optional accept or deny)
            "ChatHandler",                     # Name of handler
            False,                             # dbus uniquify-name token
            self.incoming_chat_channel,        # The callback
            None                               # Custom data to pass to callback
        )

        # Describe the channel (a chat channel)
        handler.add_handler_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_REQUESTED: False,
        })

        # Register the handler
        handler.register()

        logger.debug("Now listening for incoming chat requests...")

    def incoming_chat_channel(
        self,
        handler,
        account,
        connection,
        channels,
        requests,
        user_action_time,
        context,
        loop
    ):
        logger.debug("SimpleHandler received request for channel...")

        # Check that each channel is a Tp.TextChannel
        # For each TextChannel check get_target_contact OR get_initiator_contact (if is not self)
        # Then send those to the shared create_chat_channel_callback method

        # for channel in channels:
            # if channel is Tp.TextChannel:
                # contact = channel.get_target_contact() or channel.get_initiator_contact()
                # if contact:
                    # self.setup_chat_channel(contact, channel)
                    # Accept Channel
                    # Assign close handler for when closed

        #     print "Accepting tube"
        #     channel.connect('invalidated', tube_invalidated_cb, loop)
        #     channel.accept_async(tube_accept_cb, loop)
        # context.accept()

    def close_chat_channels(self, channels):
        logger.debug("Closing any existing chat channels...")

        # for channel in channels:
            # channel.call_close()
            # channel.close()
            # channel.close_async()
            # channel.leave_async()

    """ Chat Methods """

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

    def receive_chat_message(self, channel, message, contact):
        logger.debug("Processing received messsage...")

        # Run Registered Callbacks
        # self.run_callbacks("chat_message_received", message, contact)



    """ Callback Handling """

    def remove_callback(self, event, callback):
        if event in self.network_stack_callbacks:
            if callback in self.network_stack_callbacks[event]:
                self.network_stack_callbacks[event].remove(callback)

    def register_callback(self, event, callback):
        # If no key exists define it with a list
        if not event in self.network_stack_callbacks:
            self.network_stack_callbacks[event] = []

        # Add callback
        self.network_stack_callbacks[event].append(callback)

    def run_callbacks(self, event, *args):
        if event in self.network_stack_callbacks:
            for callback in self.network_stack_callbacks[event]:
                callback(callback, event, *args)
