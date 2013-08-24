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


    """ Properties """
    active_account = None


    def __init__(self, **callbacks):
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

        # Right now the feature descriptions are not well defined
        # many of the above may be totally unneeded
        # Once everything is working we can systematically remove features to see what breaks

        logger.debug("Configured Telepathy")

    def account_manager_async(self):
        logger.debug("Processing account manager async...")
        self.account_manager.prepare_async(None, self.account_manager_async_callback, None)

    def account_manager_async_callback(self, account_manager, status, data):
        logger.debug("Removing account manager async...")
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

        # Run Async to prepare the account
        self.active_account.prepare_async(None, self.initialize_connection, None)

    def update_active_account_status(
        self,
        account,
        old_status,
        new_status,
        reason,
        dbus_error_name,
        details,
        data
    ):
        logger.debug("Account status changed...")
        # No logic or handlers have been added here yet


    """ Connection Logic """

    def initialize_connection(self, account, status, data):
        logger.debug("Initializing connection...")

        # Finish account async
        account.prepare_finish(status)

        # Grab the connection
        connection = account.get_connection()

        if connection:
            logger.debug("Working on the next step!")

            # Remove signal from old connection
            if 'contact_list_changed' in self.network_stack_signals:
                self.active_connection.disconnect(self.network_stack_signals['contact_list_changed'])

            # Update connection
            self.active_connection = connection

            # Load Contacts
            self.get_connection_contacts()

            # Setup async & logic to disconnect async if connection changes
            # self.active_connection.prepare_async(None, self.connection_async_callback, None)

        else:
            logger.error("Unable to acquire connection...")

    def get_connection_contacts(self):
        logger.debug("Grabbing contacts from connection...")

        if self.active_connection.get_contact_list_state() is Tp.ContactListState.SUCCESS:
            contacts = self.active_connection.dup_contact_list()

            # Setup signals for contact list changes
            self.network_stack_signals['contact_list_changed'] = self.active_connection.connect('contact-list-changed', self.contacts_changed_callback)

            # Run registered handlers
            self.run_callbacks('get_connection_contacts', self, contacts)

        else:
            logger.warning("Unable to retreive contacts from connection!")

    def contacts_changed_callback(self):
        logger.debug("Received change to contacts...")

    def connection_async_callback(self, connection, status, data):
        # Alternative logic has us reset the callback while is
        # Still need to test whether the first approach works for notifying of changes to contact list
        if self.active_connection is not connection:
            connection.prepare_finish(status)


    """ Callback Handling """

    def remove_callback(self, event, callback):
        for cb in self.network_stack_callbacks[event]:
            if callback is cb:
                self.network_stack_callbacks[event].remove(callback)

    def register_callback(self, event, callback):
        # If no key exists define it with a list
        if not event in self.network_stack_callbacks:
            self.network_stack_callbacks[event] = []

        # Add callback
        self.network_stack_callbacks[event].append(callback)

    def run_callbacks(self, event, *args):
        for callback in self.network_stack_callbacks[event]:
            callback(callback, event, *args)
