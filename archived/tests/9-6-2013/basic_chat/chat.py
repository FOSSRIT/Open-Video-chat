#!/usr/bin/env python

# Imports
from gi.repository import Gtk, TelepathyGLib as Tp
import datetime

class Chat(Gtk.Grid):

    # Class Properties
    account = None
    connection = None
    handler = None
    observer = None
    contact = None
    channels = []
    chat_entry = None
    chat_text_view = None
    contact_tree_view = None

    def __init__(self):
        Gtk.Grid.__init__(self, expand=True)
        self.setup_gui()


    """ UI Methods """

    def setup_gui(self):

        self.chat_entry = chat_entry = Gtk.Entry(
            max_length = 200,
            hexpand = True,
            placeholder_text = "type a message...",
            sensitive = False
        )
        chat_entry.connect('activate', self.send_message)
        chat_text_buffer = Gtk.TextBuffer()
        self.chat_text_view = chat_text_view = Gtk.TextView(
            editable = False,
            cursor_visible = False,
            wrap_mode = Gtk.WrapMode.WORD,
            buffer = chat_text_buffer
        )
        chat_scroller = Gtk.ScrolledWindow(
            expand = True,
            hscrollbar_policy = Gtk.PolicyType.NEVER,
            vscrollbar_policy = Gtk.PolicyType.AUTOMATIC
        )
        chat_scroller.add(chat_text_view)
        contact_list_store = Gtk.ListStore(
            str,                # Contact Alias
            object,             # TpContact
            object              # Text Channel
        )
        self.contact_tree_view = contact_tree_view = Gtk.TreeView(contact_list_store)
        contact_column = Gtk.TreeViewColumn(
            "Alias",
            Gtk.CellRendererText(),
            text=0
        )
        contact_column.set_sort_column_id(0)
        contact_tree_view.append_column(contact_column)
        contact_scroll_window = Gtk.ScrolledWindow(
            vexpand = True,
            hscrollbar_policy = Gtk.PolicyType.NEVER,
            vscrollbar_policy = Gtk.PolicyType.AUTOMATIC
        )
        contact_scroll_window.add(contact_tree_view)
        self.attach(chat_scroller, 0, 0, 1, 1)
        self.attach(chat_entry, 0, 1, 1, 1)
        self.attach(contact_scroll_window, 1, 0, 2, 2)

        # Row Selection Handler
        contact_tree_view.connect('row-activated', self.select_contact)

        # GUI will notify us when it is ready
        self.connect('realize', self.setup_network)

        # Simple show-all
        self.show_all()

    def select_contact(self, tree, index, column):
        self.contact = contact = tree.get_model()[index][1]

        # If no channel exists
        if tree.get_model()[index][2] is None:

            # Define Channel and request it
            channel_description = {
                Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type
                Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
                Tp.PROP_CHANNEL_TARGET_ID: contact.get_identifier()              # Who to open the channel with
            }
            request = Tp.AccountChannelRequest.new(
                self.account,                               # Current Account
                channel_description,                        # Dict of channel properties
                Tp.USER_ACTION_TIME_NOT_USER_ACTION         # Time stamp of action (0 also works)
            )
            request.ensure_channel_async(
                self.handler.get_bus_name(),
                None,
                self.request_channel,
                None
            )

    def add_remove_contacts(self, added, removed):
        if added:
            for contact in added:
                self.contact_tree_view.get_model().append([contact.get_alias(), contact, None])

        if removed:
            for contact in removed:
                for row in self.contact_tree_view.get_model():
                    if row[1] is contact:
                        self.contact_tree_view.get_model().remove(row)


    """ Network Methods """

    def setup_network(self, grid):

        # Grab the account manager
        am = Tp.AccountManager.dup()

        if am:

            # Set global feature defaults using the shared factory component
            factory = am.get_factory()
            if factory:
                factory.add_account_features([
                    Tp.Account.get_feature_quark_connection()               # When we ask for accounts, make sure they have connections
                ])
                factory.add_connection_features([
                    Tp.Connection.get_feature_quark_contact_list(),         # Connections should have populated contact lists
                ])
                factory.add_contact_features([
                    Tp.ContactFeature.ALIAS,                                # Contacts will be loaded with user Alias's
                ])
                factory.add_channel_features([
                    Tp.Channel.get_feature_quark_contacts(),                # Make sure we have contacts on the channel
                    Tp.TextChannel.get_feature_quark_chat_states(),         # Gets us additional message info
                    Tp.TextChannel.get_feature_quark_incoming_messages(),   # Yes, we want to know about incoming messages
                ])

                # Async process on account manager to prepare the above features for us
                am.prepare_async(None, self.am_setup, None)

    def am_setup(self, am, status, data):
        am.prepare_finish(status)

        # Grab Account
        self.get_account(am)

        if self.account:

            # Register Handler
            self.register_handler(am)

            # Register Observer
            self.register_observer(am)

            # Setup Contacts
            self.setup_contacts()

    def get_account(self, am):
        for a in am.get_valid_accounts():
            if self.account is None and a.get_protocol() == "jabber" and a.is_enabled():
                self.account = a
                self.get_parent_window().set_title(self.account.get_nickname())

    def register_handler(self, am):

        # Create & Register a handler with the dbus
        self.handler = handler = Tp.SimpleHandler.new_with_am(
            am,                                # As specified in the method name
            False,                             # bypass approval (dbus related)
            False,                             # Whether to implement requests (more work but allows optional accept or deny)
            "OVC.Chat.Handler",                # Name of handler
            False,                             # dbus uniquify-name token
            self.incoming_channel,             # The callback
            None                               # Custom data to pass to callback
        )
        handler.add_handler_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,        # Channel Type (Text)
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),  # What it is tied to (A Contact)
            Tp.PROP_CHANNEL_REQUESTED: False,                                # Don't process channels we ourselves requested
        })
        handler.add_handler_capabilities([
            Tp.IFACE_CHANNEL_INTERFACE_MESSAGES,                             # Let dbus know we want messages
        ])
        handler.register()

    def register_observer(self, am):

        # Create & Register an observer that points to our handler
        self.observer = observer = Tp.SimpleObserver.new_with_am(
            am,
            False,
            "OVC.Chat.Observer",
            False,
            self.observe_channels,
            None
        )
        observer.add_observer_filter({
            Tp.PROP_CHANNEL_CHANNEL_TYPE: Tp.IFACE_CHANNEL_TYPE_TEXT,           # Only look for text channels
            Tp.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(Tp.HandleType.CONTACT),     # Private channels only
        })
        observer.set_observer_delay_approvers(True)                             # Delay approvers on dbus from processing (to allow override time)
        observer.register()

    def setup_contacts(self):

        # Grab connection
        self.connection = connection = self.account.get_connection()

        # Grab contacts
        contacts = connection.dup_contact_list()

        # Send contacts to display
        self.add_remove_contacts(contacts, None)

        # Register signal for changes
        connection.connect('contact-list-changed', self.add_remove_contacts)


    """ Channel Methods """

    def observe_channels(
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
        if account is self.account and operation and len(channels):

            # Claim Channel
            operation.claim_with_async(
                self.handler,
                self.claimed_channel,
                channels[0]
            )

            # Wait for claim before accepting context
            context.accept()

    def claimed_channel(self, operation, status, channel):
        operation.claim_with_finish(status)

        # Prepare Channel
        channel.prepare_async(None, self.channel_activated, None)

    def request_channel(self, request, status, data):
        request.ensure_channel_finish(status)

    def incoming_channel(
        self,
        handler,
        account,
        connection,
        channels,
        requests,
        code,
        context,
        data
    ):
        if account is self.account and len(channels):
            channels[0].prepare_async(None, self.channel_activated, None)
            context.accept()
        else:
            context.fail()

    def channel_activated(self, channel, status, data):
        channel.prepare_finish(status)

        # Enable chat entry
        self.chat_entry.set_sensitive(True)
        self.chat_entry.grab_focus()

        # Add channel to channels list
        self.channels.append(channel)

        # Get Contact
        contact = channel.get_target_contact()

        # Add reference to contact list
        for c in self.contact_tree_view.get_model():
            if c[1] == contact:
                c[2] = channel

        # Append message processing
        channel.connect('message-received', self.message_received)

    def message_received(self, channel, message):
        # Acknowledge Message
        channel.ack_message_async(
            message,
            self.message_acknowledged,
            None
        )

        # Prepare Message for Display
        line = "%s [%s]: %s\n" % (channel.get_target_contact().get_alias(), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message.to_text()[0])

        # Add message to text buffer
        self.chat_text_view.get_buffer().insert(
            self.chat_text_view.get_buffer().get_end_iter(),
            line,
            -1
        )

        # Scroll to bottom
        self.chat_text_view.scroll_to_iter(
            self.chat_text_view.get_buffer().get_end_iter(),
            0.1,
            False,
            0.0,
            0.0
        )

    def message_acknowledged(self, channel, status, data):
        channel.ack_message_finish(status)

    def send_message(self, entry):
        if len(entry.get_text()):

            channel = None
            for c in self.contact_tree_view.get_model():
                if self.contact is c[1]:
                    channel = c[2]

            # Send Message to channel
            if channel:

                message_container = Tp.ClientMessage.new_text(
                    Tp.ChannelTextMessageType.NORMAL,
                    entry.get_text()
                )
                channel.send_message_async(
                    message_container,
                    0,                      # Optional Message Flags
                    self.message_sent,      # Callback
                    None
                )

            # Write to text iter
            line = "%s [%s]: %s\n" % (self.account.get_nickname(), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.chat_entry.get_text())

            # Add message to text buffer
            self.chat_text_view.get_buffer().insert(
                self.chat_text_view.get_buffer().get_end_iter(),
                line,
                -1
            )

            # Scroll to bottom
            self.chat_text_view.scroll_to_iter(
                self.chat_text_view.get_buffer().get_end_iter(),
                0.1,
                False,
                0.0,
                0.0
            )

            # Empty text entry
            entry.set_text("")
            entry.grab_focus()

    def message_sent(self, channel, status, data):
        channel.send_message_finish(status)

# If executed stand-alone it will execute itself
if __name__ == "__main__":

    # Create a window to hold the chat system
    window = Gtk.Window()
    window.set_default_size(800, 600)
    window.add(Chat())
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
