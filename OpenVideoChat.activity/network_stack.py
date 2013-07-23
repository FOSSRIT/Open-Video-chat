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

        # Other data (??? Do we still need it all)
        self.owner = None
        self.shared_activity = None
        self.username = None
        self.receive_message_callback = None

        """ Sugar Specific Handling """

        # Assign owner if exists (???)

        # Assign buddy callback if exists (???)

        # Grab Account Details
        if not self.prepare_account():
            logger.debug("Failed to initialize the network stack")

        # Completed
        logger.debug("Network Stack Initialized")

    def prepare_account(self):
        logger.debug("Preparing account asynchronously...")

        # Grab the account manager
        self.account_manager = Tp.AccountManager.dup()

        # Don't do anything else if the account manager is non-existent
        if self.account_manager is None:
            return False

        # Wait for the account to be ready to ensure the channel
        self.account_manager.prepare_async(None, self.setup_channels, None)

    def setup_channels(self, account_manager, status, data):
        logger.debug("Setting up channels...")

        # Remove Async Listener from account_manager
        self.account_manager.prepare_finish(status)

        # Grab the first available account (**FIXME** assumptions are bad!)
        self.account = self.account_manager.get_valid_accounts()[0]

        # If no account exists (eg. None), print error and end setup (**FIXME** cleaner error handling is desirable)
        if not self.account:
            logger.debug("Failed to acquire account...")
            return False

        # Run through channel setup procedures
        self.setup_chat_channel()
        # self.setup_command_channel()
        # self.setup_stream_channel()

    def setup_chat_channel(self):
        logger.debug("Setting up chat channel...")

        # Describe the channel type (text)
        channel_description = {
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),
            Tp.PROP_CHANNEL_TARGET_ID: self.account.get_normalized_name()
        }

        # Request the channel
        request = Tp.AccountChannelRequest.new(self.account, channel_description, 0)

        # Run this asynchronously
        request.ensure_channel_async("", None, self.chat_channel_setup_callback, None)

    # def chat_channel_setup_callback(request, status, data):
    def chat_channel_setup_callback(arg1, arg2, arg3, arg4):
        logger.debug("Chat Channel Setup Completed")

        print arg1
        print arg2
        print arg3
        print arg4
        # Still more to do, but this means the request succeeded?

        # Remove asynchronous listener
        # request.ensure_channel_finish(status)

    def channel_setup_callback(self):
        logger.debug("Handle channel setup callback...")

        # Setup an account manager
        account_manager = Tp.AccountManager.dup()

        # Prepare to create channel
        handler = Tp.SimpleHandler.new_with_am(
            account_manager,
            False,                        # Bypass Approval
            False,                        # Implement Requests
            username + '.chat',   # Name of service
            False,                        # Unique Name
            self.channel_setup_callback,  # Callback
            None                          # Custom Data supplied to callback
        )

        # Define Channel
        handler.add_handler_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),
            Tp.PROP_CHANNEL_REQUESTED: False,
        })

        # Register Channel
        handler.register()

    def setup_command_channel(self):
        logger.debug("Setting up command channel...")

    def setup_stream_channel(self):
        logger.debug("Setting up stream channel...")

    def get_users_list(self):
        logger.debug("Getting user list...")

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
