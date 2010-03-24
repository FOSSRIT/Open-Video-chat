import gtk
from gettext import gettext as _

from sugar.activity.activity import ActivityToolbox
from sugar.graphics.toolbutton import ToolButton

class Gui( gtk.VBox ):
    def __init__(self, activity):
        gtk.VBox.__init__(self)

        self.activity = activity

        # Add movie window
        self.movie_window = gtk.DrawingArea()
        self.pack_start( self.movie_window )

        # Add Chat section
        ##################

        # Chat expander allows chat to be hidden/shown
        chat_expander = gtk.Expander(_("Chat"))
        chat_expander.set_expanded( True )
        self.pack_start( chat_expander, False )

        chat_holder = gtk.VBox()
        chat_expander.add(chat_holder)

        # Create entry and history view for chat
        chat_history = gtk.ScrolledWindow()
        chat_history.set_policy( gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC )
        
        self.chat_text = gtk.TextBuffer()
        text_view = gtk.TextView( self.chat_text )
        text_view.set_editable( False )
        text_view.set_size_request( -1, 200 )
        
        chat_history.add( text_view )
        
        # Send button to complete feel of a chat program
        self.chat_entry = gtk.Entry()
        self.chat_entry.connect("activate",self.send_chat)
        send_but = gtk.Button( _("Send") )
        send_but.connect("clicked", self.send_chat)

        # Wrap button and entry in hbox so they are on the same line
        chat_entry_hbox = gtk.HBox()
        chat_entry_hbox.pack_start( self.chat_entry )
        chat_entry_hbox.pack_end( send_but, False )

        # Add chat history and entry to expander
        chat_holder.pack_start( chat_history )
        chat_holder.pack_start( chat_entry_hbox, False )

        # Show gui
        self.build_toolbars()
        self.show_all()

    def add_chat_text( self, text ):
        
        self.chat_text.insert( self.chat_text.get_end_iter(), "%s\n" % text ) 
        
    def send_chat(self, w):
        if self.chat_entry.get_text != "":
            self.activity.send_chat_text( self.chat_entry.get_text() )
            self.chat_entry.set_text("")

    def build_toolbars(self):
        self.settings_bar = gtk.Toolbar()

        self.settings_buttons = {}


        self.settings_buttons['test'] = ToolButton('view-spiral')
        self.settings_buttons['test'].set_tooltip(_("TEST ICON"))
        #self.settings_buttons['test'].connect("clicked", self.view_change_cb, 'new')
        self.settings_bar.insert(self.settings_buttons['test'], -1)

        self.toolbox = ActivityToolbox(self.activity)
        self.toolbox.add_toolbar(_("Settings"), self.settings_bar)

        self.activity.set_toolbox(self.toolbox)
        self.toolbox.show_all()
