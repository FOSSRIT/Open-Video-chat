#!/usr/bin/python

# Farsight 2 demo GUI program
#
# Copyright (C) 2007 Collabora, Nokia
# @author: Olivier Crete <olivier.crete@collabora.co.uk>
# Modified by Justin Lewis <jlew.blackout@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#

import sys, os, pwd, os.path
import socket
import threading

import signal

import pygtk
pygtk.require("2.0")

import gtk, gobject, gtk.gdk
import gobject

import pygst
pygst.require('0.10')
import gst
import farsight

from fs_stack import FsPipeline, FsParticipant

from fs2_gui_net import  FsUIClient, FsUIListener, FsUIServer

CAMERA=False

AUDIO=True
VIDEO=True

CLIENT=1
SERVER=2

import os, pwd
mycname = "".join((pwd.getpwuid(os.getuid())[0],
                   "-" ,
                   str(os.getpid()),
                   "@",
                   socket.gethostname()))

builderprefix = os.path.join(os.path.dirname(__file__),"fs2-gui-")


class FsMainUI:
    "The main UI and its different callbacks"
    
    def __init__(self, mode, ip, port):
        self.mode = mode
        self.pipeline = FsPipeline()
        self.pipeline.codecs_changed_audio = self.reset_audio_codecs
        self.pipeline.codecs_changed_video = self.reset_video_codecs
        self.builder = gtk.Builder()
        self.builder.add_from_file(builderprefix + "main-window.ui")
        self.builder.connect_signals(self)
        self.mainwindow = self.builder.get_object("main_window")
        self.audio_combobox = self.builder.get_object("audio_combobox")
        self.video_combobox = self.builder.get_object("video_combobox")
        liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.audio_combobox.set_model(liststore)
        cell = gtk.CellRendererText()
        self.audio_combobox.pack_start(cell, True)
        self.audio_combobox.add_attribute(cell, 'text', 0)
        self.reset_audio_codecs()
        liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.video_combobox.set_model(liststore)
        cell = gtk.CellRendererText()
        self.video_combobox.pack_start(cell, True)
        self.video_combobox.add_attribute(cell, 'text', 0)
        self.reset_video_codecs()

        if mode == CLIENT:
            self.client = FsUIClient(ip, port, mycname, FsParticipant,
                                     self.pipeline, self)
            self.builder.get_object("info_label").set_markup(
                "<b>%s</b>\nConnected to %s:%s" % (mycname, ip, port))
        elif mode == SERVER:
            self.server = FsUIListener(port, FsUIServer, mycname,
                                       FsParticipant, self.pipeline, self)
            self.builder.get_object("info_label").set_markup(
                "<b>%s</b>\nExpecting connections on port %s" %
                (mycname, self.server.port))

        
        self.mainwindow.show()

    def reset_codecs(self, combobox, fssession):
        liststore = combobox.get_model()
        current = fssession.get_property("current-send-codec")
        liststore.clear()
        for c in fssession.get_property("codecs"):
            str = ("%s: %s/%s %s" % (c.id, 
                                     c.media_type.value_nick,
                                     c.encoding_name,
                                     c.clock_rate))
            iter = liststore.append([str, c])
            if current and c and current.id == c.id:
                combobox.set_active_iter(iter)
                print "active: "+ c.to_string()

    def reset_audio_codecs(self):
        if AUDIO:
            self.reset_codecs(self.audio_combobox,
                              self.pipeline.audiosession.fssession)

    def reset_video_codecs(self):
        if VIDEO:
            self.reset_codecs(self.video_combobox,
                              self.pipeline.videosession.fssession)

    def combobox_changed_cb(self, combobox, fssession):
        liststore = combobox.get_model()
        iter = combobox.get_active_iter()
        if iter:
            codec = liststore.get_value(iter, 1)
            fssession.set_send_codec(codec)

    def audio_combobox_changed_cb(self, combobox):
        self.combobox_changed_cb(combobox, self.pipeline.audiosession.fssession)
    
    def video_combobox_changed_cb(self, combobox):
        self.combobox_changed_cb(combobox, self.pipeline.videosession.fssession)
        
        
    def exposed(self, widget, *args):
        "Callback from the exposed event of the widget to make the preview sink"
        if not VIDEO:
            return
        try:
            self.preview.get_by_interface(gst.interfaces.XOverlay).expose()
        except AttributeError:
            self.preview = self.pipeline.make_video_preview(widget.window.xid,
                                                            self.newsize)

    def newsize (self, x, y):
        self.builder.get_object("preview_drawingarea").set_size_request(x,y)
        
    def shutdown(self, widget=None):
        gtk.main_quit()
        
    def hbox_add(self, widget, label):
        table = self.builder.get_object("users_table")
        x = table.get_properties("n-columns")[0]
        table.attach(widget, x, x+1, 0, 1)
        table.attach(label, x, x+1, 1, 3, xpadding=6)

    def __del__(self):
        self.mainwindow.destroy()

    def fatal_error(self, errormsg):
        gtk.gdk.threads_enter()
        dialog = gtk.MessageDialog(self.mainwindow,
                                   gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_OK)
        dialog.set_markup(errormsg);
        dialog.run()
        dialog.destroy()
        gtk.main_quit()
        gtk.gdk.threads_leave()


class FsUIStartup:
    "Displays the startup window and then creates the FsMainUI"
    
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(builderprefix + "startup.ui")
        self.dialog = self.builder.get_object("neworconnect_dialog")
        self.builder.get_object("spinbutton_adjustment").set_value(9893)
        self.builder.connect_signals(self)
        self.dialog.show()
        self.acted = False

    def action(self, mode):
        port = int(self.builder.get_object("spinbutton_adjustment").get_value())
        ip = self.builder.get_object("newip_entry").get_text()
        try:
            self.ui = FsMainUI(mode, ip, port)
            self.acted = True
            self.dialog.destroy()
            del self.dialog
            del self.builder
        except socket.error, e:
            dialog = gtk.MessageDialog(self.dialog,
                                       gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_ERROR,
                                       gtk.BUTTONS_OK)
            dialog.set_markup("<b>Could not connect to %s %d</b>" % (ip,port))
            dialog.format_secondary_markup(e[1])
            dialog.run()
            dialog.destroy()
        
    def new_server(self, widget):
        self.action(SERVER)

    def connect(self, widget):
        self.action(CLIENT)
        

    def quit(self, widget):
        if not self.acted:
            gtk.main_quit()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        CAMERA = sys.argv[1]
    else:
        CAMERA = None
    
    gobject.threads_init()
    gtk.gdk.threads_init()
    startup = FsUIStartup()
    gtk.main()
