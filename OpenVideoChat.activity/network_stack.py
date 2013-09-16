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

    call = None
    chat_observer = None
    chat_handler = None
    active_account = None
    active_connection = None
    close_channels = []

    """ Setup Logic """

    def __init__(self, callbacks={}):
        logger.debug("Preparing Network Stack...")

        # Create dicts for signals and callbacks
        self.network_stack_signals = {}
        self.network_stack_callbacks = callbacks

        # Grab the account manager to begin the setup process
        self.account_manager = Tp.AccountManager.dup()
        if self.account_manager:

            # Setup factory configuration and a channel observer
            self.configure_network_stack(self.account_manager)
            self.configure_observer(self.account_manager)

            # Register initial callbacks
            self.register_callback('get_jabber_accounts', self.initialize_account)
            self.register_callback("setup_active_account", self.close_chat_channels)
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
            Tp.Account.get_feature_quark_connection()               # Pull the connections for the accounts
        ])
        factory.add_connection_features([
            Tp.Connection.get_feature_quark_contact_list(),         # Get the contact list as a "feature"
        ])
        factory.add_contact_features([
            Tp.ContactFeature.ALIAS,                                # Get contact ALIAS's from system
        ])
        factory.add_channel_features([
            Tp.Channel.get_feature_quark_contacts(),                # Make sure we have contacts on the channel
            Tp.TextChannel.get_feature_quark_chat_states(),         # Gets us additional message info
            Tp.TextChannel.get_feature_quark_incoming_messages(),   # Why would we want to receive messages when using communication software by default?
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

        # Register listener for incoming chat requests
        self.listen_for_incoming_chat(account_manager)

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
        if account is self.active_account:
            logger.warning("Account is already active!")
        elif account.is_enabled() and account.get_connection_status()[0] is Tp.ConnectionStatus.CONNECTED:

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

        logger.debug("Connection Established")

    def contacts_add_remove(self, added, removed, *args):
        logger.debug("Received change to contacts...")

        # Run callback for changes to the contact list
        self.run_callbacks("contacts_changed", self, added, removed)

    """ Observe, Request, and Handle Channels with DBus Interfaces """

    def configure_observer(self, account_manager):

        # Create an observer with class-level reference
        self.chat_observer = observer = Tp.SimpleObserver.new_with_am(
            account_manager,
            False,
            "OVC.Chat.Observer",
            False,
            self.observe_chat_channels,
            None
        )

        # Filter Channel Types
        observer.add_observer_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,           # Only look for text channels
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),     # Private channels only
        })

        # Delay approvers on dbus from processing (to allow override time)
        observer.set_observer_delay_approvers(True)

        # Register with the DBus
        observer.register()

    def listen_for_incoming_chat(self, account_manager):
        logger.debug("Listening for incoming connections...")

        # Create a TpBaseClient to handle incoming chat requests
        self.chat_handler = handler = Tp.SimpleHandler.new_with_am(
            account_manager,              # As specified in the method name
            False,                             # bypass approval (dbus related)
            False,                             # Whether to implement requests (more work but allows optional accept or deny)
            "OVC.Chat.Handler",                # Name of handler
            False,                             # dbus uniquify-name token
            self.incoming_chat_channel,        # The callback
            None                               # Custom data to pass to callback
        )

        # Describe the channel we care about (a chat channel)
        handler.add_handler_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_REQUESTED: False,
        })

        # Tell dbus to let everything know this can handle messages
        handler.add_handler_capabilities([
            Tp.IFACE_CHANNEL_INTERFACE_MESSAGES,
        ])

        # Register the handler, we will receive information going forward.
        handler.register()

        logger.debug("Now listening for incoming chat requests...")

    def request_chat_channel(self, contact):
        logger.debug("Setting up outgoing chat channel...")

        # Describe the channel type (text)
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_TARGET_ID: contact.get_identifier()              # Who to open the channel with
        }

        # Request the channel from the account
        request = Tp.AccountChannelRequest.new(
            self.active_account,                        # Current Account
            channel_description,                        # Dict of channel properties
            Tp.USER_ACTION_TIME_NOT_USER_ACTION         # Time stamp of action (0 also works)
        )

        # Run this asynchronously and execute the callback
        request.ensure_and_handle_channel_async(
            None,                                       # Whether it can be cancelled
            self.chat_channel_request_callback,         # Callback to run when done
            None                                        # Custom Data sent to callback
        )

        # Private channels are not named, only group channels (MUC for Multi-User Channel)
        # Because they are not named, only one can exist at a time
        # The `ensure` method will reuse existing channels, hence it is the better choice

    """ Channel Logic """

    def observe_chat_channels(
        self,
        observer,
        account,
        connection,
        channels,
        operation,
        requests,
        context,
        data
    ):
        if account is self.active_account and operation and len(channels):

            # Claim Channel
            operation.claim_with_async(
                self.chat_handler,
                self.claimed_chat_channel,
                channels[0]
            )

            # Wait for claim before accepting context
            context.accept()

    def claimed_chat_channel(self, operation, status, channel):
        operation.claim_with_finish(status)
        logger.debug("Claimed channel!")

        # Prepare Channel
        channel.prepare_async(None, self.chat_channel_activated, None)

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

        if account is self.active_account and len(channels):
            channels[0].prepare_async(None, self.chat_channel_activated, None)
            context.accept()
        else:
            logger.warning("Channel is not for active account...")
            context.fail()

    def chat_channel_request_callback(self, request, status, data):
        logger.debug("Chat channel approved and initiating...")

        # Remove async process & grab channel plus context
        (channel, context) = request.ensure_and_handle_channel_finish(status)

        # Async channel to handle
        channel.prepare_async(None, self.chat_channel_activated, None)

    def chat_channel_activated(self, channel, status, data):
        logger.debug("Connecting channel callbacks...")
        channel.prepare_finish(status)

        # Append message processing
        message_handler = channel.connect('message-received', self.chat_message_received)

        # Add to close-channels & callback to list
        self.close_channels.append([channel, message_handler])

        # Run callbacks for new chat channel received
        self.run_callbacks('new_chat_channel', self, channel)

        # Handle Pending Messages (Not sure why I need this in OVC but my example worked without it...)
        for message in channel.dup_pending_messages():
            self.chat_message_received(channel, message, None)

    """ Shutdown Process """

    def close_chat_channels(self, callback, event, parent, data):
        logger.debug("Closing open chat channels...")

        for (channel, message_handler) in self.close_channels:

            if channel and message_handler:

                # Disconnect Handler
                channel.disconnect(message_handler)

                # Close Channel
                channel.leave_async(
                    Tp.ChannelGroupChangeReason.OFFLINE,
                    "Exited OVC.",
                    (lambda c, s, d: c.leave_finish(s)),
                    None
                )

        # Empty Channels again
        self.close_channels = []

    def stop_observer_and_handler(self):
        if self.chat_observer:
            self.chat_observer.unregister()
            self.chat_observer = None
        if self.chat_handler:
            self.chat_handler.unregister()
            self.chat_handler = None

    def shutdown(self):
        self.stop_observer_and_handler()
        self.close_chat_channels(None, None, None, None)

    """ Chat Methods """

    def send_chat_message(self, channel, message, message_type=Tp.ChannelTextMessageType.NORMAL):
        logger.debug("Sending a message over the wire...")

        # Wrap our message in a Telepathy Message object
        message_container = Tp.ClientMessage.new_text(message_type, message)

        # Send asynchronous message
        channel.send_message_async(
            message_container,          # Telepathy ClientMessage object
            0,                          # Optional Message Sending Flags
            self.chat_message_sent,     # Callback (to close async)
            None                        # Data for callback
        )

        # The message sending flags are numeric constants representing features
        # currently these include delivery, read, and deleted confirmation
        # The numeric representation uses bit-mapping increments (1, 2, 4, etc)
        # in this way 3 represents the combination of 1 + 2, or two-enabled features

        # Technically, they are missing a NONE constant to represent 0
        # hence why supplying 0 is the same as saying "use no features"
        # and supplying None will throw an error

    def chat_message_sent(self, channel, status, data):
        channel.send_message_finish(status)

    def chat_message_received(self, channel, message, data):
        logger.debug("Processing received messsage...")

        # Acknowledge Message
        channel.ack_message_async(
            message,
            self.chat_message_acknowledged,
            None
        )

        # Run Registered Callbacks
        self.run_callbacks("chat_message_received", self, message, channel.get_target_contact())

    def chat_message_acknowledged(self, channel, status, data):
        channel.ack_message_finish(status)

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
