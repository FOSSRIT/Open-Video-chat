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

        # Channels for chat, stream, and commands
        self.chat_channel = None
        self.stream_channel = None
        self.command_channel = None

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

        # Using quarks tell the factory to pull the connection with the account
        factory.add_account_features([Tp.Account.get_feature_quark_connection()])

        # Using quarks tell the factory to pull the contact list with the connection
        factory.add_connection_features([Tp.Connection.get_feature_quark_contact_list()])

        # Tell the factory to include contact aliases
        factory.add_contact_features([Tp.ContactFeature.ALIAS])

        # Wait for the account to be ready to ensure the channel
        self.account_manager.prepare_async(None, self.setup_stack_components, None)

    def setup_stack_components(self, account_manager, status, data):
        logger.debug("Setting up asynchronous stack components...")

        # Remove Async Listener from account_manager
        self.account_manager.prepare_finish(status)

        # Grab the first available "jabber" account
        for account in self.account_manager.get_valid_accounts():
            if account.get_protocol() == "jabber":
                self.account = account
                break

        # Use of break terminates the loop early
        # We could use a while loop and a separately incremented index
        # but this would create an extra variable we won't need after
        # Or we could add `self.account is None` to the if statement
        # but that would waste cycles

        # If no account exists, print error and end setup
        if self.account is None:
            logger.debug("Failed to acquire account...")
            # **FIXME** if no valid accounts need to open account management window
            return False

        # Get connection
        connection = self.account.get_connection()

        # Dup the users & populate our users list for selecting a contact
        if connection is not None and connection.get_contact_list_state() == Tp.ContactListState.SUCCESS:
            self.populate_users_list(connection.dup_contact_list())

        # **FIXME** Further abstraction to adding contacts should be added to manage
        #           live updates for contacts with TelepathyGLib and reflecting it in Gtk3

        """ Sugar handling for if connection established through sugar sharing process """

        # Listen for incoming connections
        # self.setup_chat_channel()

    def populate_users_list(self, contacts):
        logger.debug("Adding contacts to gui...")

        for contact in contacts:
            self.add_user_to_gui(contact)

        logger.debug("Sent users to gui")

    def listen_for_chat_channel(self):
        logger.debug("Listening for incoming connections...")

    def setup_chat_channel(self, contact):
        logger.debug("Setting up outgoing chat channel...")

        # Describe the channel type (text)
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_TARGET_ID: contact.get_identifier()              # Who to open the channel with
        }

        # # **FIXME** Still investigating how to name the channel

        # # Request the channel
        # request = Tp.AccountChannelRequest.new(
        #     self.account,                              # Account
        #     channel_description,                       # Dict of channel properties
        #     Tp.USER_ACTION_TIME_NOT_USER_ACTION        # Time stamp of action (0 also works)
        # )

        # # Run this asynchronously
        # request.ensure_channel_async("", None, self.chat_channel_setup_callback, None)

    def chat_channel_setup_callback(self, request, status, data):
        logger.debug("Chat Channel Setup Completed")

        # # Grab the channel while removing the asynchronous listener
        # (self.chat_channel, context) = request.create_and_handle_channel_finish(status)

        # # If the chat channel was made connect message received handler
        # if self.chat_channel:
        #     self.chat_channel.connect('message-received', self.chat_message_received)

    def send_chat_message(self, message):
        logger.debug("Sending a message over the wire...")

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
