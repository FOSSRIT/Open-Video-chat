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
:mod: `OpenVideoChat.activity/account_manager` -- Open Video Chat
=======================================================================

.. moduleauthor:: Casey DeLorme <cxd4280@rit.edu>
"""


# Imports
import logging
from gi.repository import Gtk
from gettext import gettext as _


# Define Logger for Logging & DEBUG level for Development
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants
MAX_TEXT_WIDTH = 300


class AccountManager(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self, expand=True)
        logger.debug("Preparing Account Management GUI...")

        self.build_list()
        self.build_info_container()

        logger.debug("Displaying Content")
        self.show_all()

        logger.info("Prepared Account Manager")

    def build_list(self):

        logger.debug("Creating Account List...")

        self.account_list_store = Gtk.ListStore(
            str,        # User Account Alias
            object      # TpAccount
        )

        # Create a Tree View and supply it the List Store
        account_list_tree_view = Gtk.TreeView(self.account_list_store)

        # Define the columns of the Tree View to render the data
        account_tree_view_column = Gtk.TreeViewColumn(
            "Account Name",          # Column Title (is displayed)
            Gtk.CellRendererText(),  # Renderer Component
            text=0                   # Column Index
        )

        # Sort by the alias column
        account_tree_view_column.set_sort_column_id(0)

        # Add the column to the Tree View
        account_list_tree_view.append_column(account_tree_view_column)

        # Create a scrollbox for user list
        account_list_scrolled_window = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            width_request=MAX_TEXT_WIDTH
        )
        account_list_scrolled_window.add(account_list_tree_view)

        # Add a click handler to the tree view for user selection
        account_list_tree_view.connect('row-activated', self.set_active_account)

        logger.debug("Created Account List")
        logger.debug("Creating Account Buttons...")

        # Create Buttons for add & remove
        create_account_button = Gtk.Button(label="+", tooltip_text=_("Create a jabber account."))
        delete_account_button = Gtk.Button(label="-", tooltip_text=_("Delete a jabber aaccount"))

        # Add handler functions (incomplete)
        create_account_button.connect('clicked', self.create_account)
        delete_account_button.connect('clicked', self.delete_account)

        logger.debug("Created Account Buttons...")
        logger.debug("Attaching to display...")

        # Append to grid
        self.attach(account_list_scrolled_window, 0, 0, 2, 2)
        self.attach(create_account_button, 0, 2, 1, 1)
        self.attach(delete_account_button, 1, 2, 1, 1)

        logger.debug("Built Account List")

    def build_info_container(self):

        # Entry fields for account
        self.account_name_entry = account_name_entry = Gtk.Entry(width_request=MAX_TEXT_WIDTH)
        self.account_password_entry = account_password_entry = Gtk.Entry(width_request=MAX_TEXT_WIDTH)
        self.server_entry = server_entry = Gtk.Entry(width_request=MAX_TEXT_WIDTH)

        # Hide Password Value
        account_password_entry.set_visibility(False)

        # Create a grid with labels
        account_info_grid = Gtk.Grid()
        account_info_grid.attach(
            Gtk.Label(
                halign=Gtk.Align.START,
                justify=Gtk.Justification.LEFT,
                label=_("Username: ")
            ),
            0, 0, 1, 1)
        account_info_grid.attach(
            Gtk.Label(
                halign=Gtk.Align.START,
                justify=Gtk.Justification.LEFT,
                label=_("Password: ")
            ),
            0, 1, 1, 1)
        account_info_grid.attach(Gtk.Label(
            halign=Gtk.Align.START,
            justify=Gtk.Justification.LEFT,
            label=_("Server: ")
            ),
            0, 2, 1, 1)
        account_info_grid.attach(account_name_entry, 1, 0, 1, 1)
        account_info_grid.attach(account_password_entry, 1, 1, 1, 1)
        account_info_grid.attach(server_entry, 1, 2, 1, 1)

        # **FIXME** Add dynamic buttons for update/create handling

        # Attach grid to grid
        self.attach(account_info_grid, 3, 0, 1, 1)

    def set_active_account(self, tree_view, selected_index, column_object):
        logger.debug("Testing Account Selection...")

        # Grab the selected account & run call to network stack
        account = self.account_list_store[selected_index][1]

        # Run call to setup process in network stack
        self.switch_active_account(account)

    def add_accounts(self, accounts):
        for account in accounts:
            self.account_list_store.append([account.get_nickname(), account])

    def create_account(self):
        logger.debug("Account Creation is Incomplete...")

    def delete_account(self):
        logger.debug("Account Deletion is Incomplete...")
