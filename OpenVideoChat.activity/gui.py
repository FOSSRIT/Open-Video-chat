import gtk

class Gui( gtk.VBox ):
    def __init__(self):
        gtk.VBox.__init__(self)

        # Add movie window
        self.movie_window = gtk.DrawingArea()
        self.add( self.movie_window )


        # Show Elements
        self.movie_window.show()
