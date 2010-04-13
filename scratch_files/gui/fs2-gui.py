#!/usr/bin/python

# Farsight 2 demo GUI program
#
# Copyright (C) 2007 Collabora, Nokia
# @author: Olivier Crete <olivier.crete@collabora.co.uk>
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
import weakref

import signal

try:
    import pygtk
    pygtk.require("2.0")

    import gtk, gobject, gtk.gdk
    import gobject
except ImportError, e:
    raise SystemExit("PyGTK couldn't be found ! (%s)" % (e[0]))

try:
    import pygst
    pygst.require('0.10')
        
    import gst
except ImportError, e:
    raise SystemExit("Gst-Python couldn't be found! (%s)" % (e[0]))
try:
    import farsight
except:
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__),
                                     '..', '..', 'python', '.libs'))
        import farsight
    except ImportError, e:
        raise SystemExit("Farsight couldn't be found! (%s)" % (e[0]))



from fs2_gui_net import  FsUIClient, FsUIListener, FsUIServer

CAMERA=False

AUDIO=True
VIDEO=True

CLIENT=1
SERVER=2

TRANSMITTER="rawudp"

mycname = "".join((pwd.getpwuid(os.getuid())[0],
                   "-" ,
                   str(os.getpid()),
                   "@",
                   socket.gethostname()))

builderprefix = os.path.join(os.path.dirname(__file__),"fs2-gui-")


def make_video_sink(pipeline, xid, name, async=True):
    "Make a bin with a video sink in it, that will be displayed on xid."
    bin = gst.Bin("videosink_%d" % xid)
    sink = gst.element_factory_make("ximagesink", name)
    sink.set_property("sync", async)
    sink.set_property("async", async)
    bin.add(sink)
    colorspace = gst.element_factory_make("ffmpegcolorspace")
    bin.add(colorspace)
    videoscale = gst.element_factory_make("videoscale")
    bin.add(videoscale)
    videoscale.link(colorspace)
    colorspace.link(sink)
    bin.add_pad(gst.GhostPad("sink", videoscale.get_pad("sink")))
    sink.set_data("xid", xid)
    return bin


class FsUIPipeline:
    "Object to wrap the GstPipeline"

    def int_handler(self, sig, frame):
        try:
            gst.DEBUG_BIN_TO_DOT_FILE(self.pipeline, 0, "pipelinedump")
        except:
            pass
        sys.exit(2)
    
    def __init__(self, elementname="fsrtpconference"):
        self.pipeline = gst.Pipeline()
        signal.signal(signal.SIGINT, self.int_handler)
        notifier = farsight.ElementAddedNotifier()
        notifier.connect("element-added", self.element_added_cb)
        notifier.add(self.pipeline)
        self.pipeline.get_bus().set_sync_handler(self.sync_handler)
        self.pipeline.get_bus().add_watch(self.async_handler)
        self.conf = gst.element_factory_make(elementname)
        # Sets lets our own cname
        self.conf.set_property("sdes-cname", mycname)
        self.pipeline.add(self.conf)
        if VIDEO:
            self.videosource = FsUIVideoSource(self.pipeline)
            self.videosession = FsUISession(self.conf, self.videosource)
        if AUDIO:
            self.audiosource = FsUIAudioSource(self.pipeline)
            self.audiosession = FsUISession(self.conf, self.audiosource)
            self.adder = None
        self.pipeline.set_state(gst.STATE_PLAYING)

    def __del__(self):
        self.pipeline.set_state(gst.STATE_NULL)

    def sync_handler(self, bus, message):
        "Message handler to get the prepare-xwindow-id event"
        if message.type == gst.MESSAGE_ELEMENT and \
               message.structure.has_name("prepare-xwindow-id"):
            xid = None
            element = message.src
            # We stored the XID on the element or its parent on the expose event
            # Now lets look it up
            while not xid and element:
                xid = element.get_data("xid")
                element = element.get_parent()
            if xid:
                message.src.set_xwindow_id(xid)
                return gst.BUS_DROP
        return gst.BUS_PASS

    def async_handler(self, bus, message):
        "Async handler to print messages"
        if message.type == gst.MESSAGE_ERROR:
            print message.src.get_name(), ": ", message.parse_error()
        elif message.type == gst.MESSAGE_WARNING:
            print message.src.get_name(), ": ", message.parse_warning()
        elif message.type == gst.MESSAGE_ELEMENT:
            if message.structure.has_name("dtmf-event"):
                print "dtmf-event: %d" % message.structure["number"]
            elif message.structure.has_name("farsight-local-candidates-prepared"):
                message.structure["stream"].uistream.local_candidates_prepared()

            elif message.structure.has_name("farsight-new-local-candidate"):
                message.structure["stream"].uistream.new_local_candidate(
                    message.structure["candidate"])
            elif message.structure.has_name("farsight-codecs-changed"):
                print message.src.get_name(), ": ", message.structure.get_name()
                message.structure["session"].uisession.codecs_changed()
                if AUDIO and message.structure["session"] == self.audiosession.fssession:
                    self.codecs_changed_audio()
                if VIDEO and  message.structure["session"] == self.videosession.fssession:
                    self.codecs_changed_video()
            elif message.structure.has_name("farsight-send-codec-changed"):
                print message.src.get_name(), ": ", message.structure.get_name()
                print "send codec changed: " + message.structure["codec"].to_string()
                if AUDIO and message.structure["session"] == self.audiosession.fssession:
                    self.codecs_changed_audio()
                if VIDEO and message.structure["session"] == self.videosession.fssession:
                    self.codecs_changed_video()
            elif message.structure.has_name("farsight-recv-codecs-changed"):
                print message.src.get_name(), ": ", message.structure.get_name()
                message.structure["stream"].uistream.recv_codecs_changed( \
                    message.structure["codecs"])
                
                
            elif message.structure.has_name("farsight-error"):
                print "Async error ("+ str(message.structure["error-no"]) +"): " + message.structure["error-msg"] +" --- "+ message.structure["debug-msg"]
            else:
                print message.src.get_name(), ": ", message.structure.get_name()
        elif message.type != gst.MESSAGE_STATE_CHANGED \
                 and message.type != gst.MESSAGE_ASYNC_DONE:
            print message.type
        
        return True

    def make_video_preview(self, xid, newsize_callback):
        "Creates the preview sink"
        self.previewsink = make_video_sink(self.pipeline, xid,
                                           "previewvideosink", False)
        self.pipeline.add(self.previewsink)
        #Add a probe to wait for the first buffer to find the image size
        self.havesize = self.previewsink.get_pad("sink").add_buffer_probe(self.have_size,
                                                          newsize_callback)
                                                          
        self.previewsink.set_state(gst.STATE_PLAYING)
        self.videosource.tee.link(self.previewsink)
        self.pipeline.set_state(gst.STATE_PLAYING)
        return self.previewsink

    def have_size(self, pad, buffer, callback):
        "Callback on the first buffer to know the drawingarea size"
        x = buffer.caps[0]["width"]
        y = buffer.caps[0]["height"]
        callback(x,y)
        self.previewsink.get_pad("sink").remove_buffer_probe(self.havesize)
        return True

    def link_audio_sink(self, pad):
        "Link the audio sink to the pad"
        print >>sys.stderr, "LINKING AUDIO SINK"
        if not self.adder:
            audiosink = gst.element_factory_make("alsasink")
            audiosink.set_property("buffer-time", 50000)
            self.pipeline.add(audiosink)

            try:
                self.adder = gst.element_factory_make("liveadder")
            except gst.ElementNotFoundError:
                audiosink.set_state(gst.STATE_PLAYING)
                pad.link(audiosink.get_pad("sink"))
                return
            self.pipeline.add(self.adder)
            audiosink.set_state(gst.STATE_PLAYING)
            self.adder.link(audiosink)
            self.adder.set_state(gst.STATE_PLAYING)
        convert1 = gst.element_factory_make("audioconvert")
        self.pipeline.add(convert1)
        resample = gst.element_factory_make("audioresample")
        self.pipeline.add(resample)
        convert2 = gst.element_factory_make("audioconvert")
        self.pipeline.add(convert2)
        convert1.link(resample)
        resample.link(convert2)
        convert2.link(self.adder)
        pad.link(convert1.get_pad("sink"))
        convert2.set_state(gst.STATE_PLAYING)
        resample.set_state(gst.STATE_PLAYING)
        convert1.set_state(gst.STATE_PLAYING)

    def element_added_cb(self, notifier, bin, element):
        if element.get_factory().get_name() == "x264enc":
            element.set_property("byte-stream", True)
            element.set_property("bitrate", 128)
        elif element.get_factory().get_name() == "gstrtpbin":
            element.set_property("latency", 100)
            

class FsUISource:
    "An abstract generic class for media sources"

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.tee = gst.element_factory_make("tee")
        pipeline.add(self.tee)
        self.tee.set_state(gst.STATE_PLAYING)

        self.source = self.make_source()
        pipeline.add(self.source)
        self.source.link(self.tee)
        self.playcount = 0

    def __del__(self):
        self.source.set_state(gst.STATE_NULL)
        self.tee.set_state(gst.STATE_NULL)
        self.pipeline.remove(self.source)
        self.pipeline.remove(self.tee)
        
        
    def make_source(self):
        "Creates and returns the source GstElement"
        raise NotImplementedError()


    def get_type(self):
        "Returns the FsMediaType of the source."
        raise NotImplementedError()

    def get_src_pad(self, name="src%d"):
        "Gets a source pad from the source"
        queue = gst.element_factory_make("queue")
        queue.set_property("leaky", 2)
        queue.set_property("max-size-time", 50*gst.MSECOND)
        requestpad = self.tee.get_request_pad(name)
        self.pipeline.add(queue)
        requestpad.link(queue.get_static_pad("sink"))
        pad = queue.get_static_pad("src")
        pad.set_data("requestpad", requestpad)
        pad.set_data("queue", queue)
        return pad

    def put_src_pad(self, pad):
        "Puts the source pad from the source"
        self.pipeline.remove(pad.get_data("queue"))
        self.tee.release_request_pad(pad.get_data("requestpad"))
    

class FsUIVideoSource(FsUISource):
    "A Video source"
    
    def get_type(self):
        return farsight.MEDIA_TYPE_VIDEO

    def make_source(self):
        bin = gst.Bin()
        if CAMERA:
            source = gst.element_factory_make("v4l2src")
            source.set_property("device", CAMERA)
            bin.add(source)
        else:
            source = gst.element_factory_make("videotestsrc")
            source.set_property("is-live", 1)
            bin.add(source)
            overlay = gst.element_factory_make("timeoverlay")
            overlay.set_property("font-desc", "Sans 32")
            bin.add(overlay)
            source.link(overlay)
            source=overlay

        filter = gst.element_factory_make("capsfilter")
        filter.set_property("caps", gst.Caps("video/x-raw-yuv , width=[300,500] , height=[200,500], framerate=[20/1,30/1]"))
        bin.add(filter)
        source.link(filter)

        videoscale = gst.element_factory_make("videoscale")
        bin.add(videoscale)
        filter.link(videoscale)

        bin.add_pad(gst.GhostPad("src", videoscale.get_pad("src")))
        return bin
            
      

class FsUIAudioSource(FsUISource):
    "An audio source"

    def get_type(self):
        return farsight.MEDIA_TYPE_AUDIO

    def make_source(self):
        source = gst.element_factory_make("audiotestsrc")
        source.set_property("is-live", True)
        source.set_property("wave", 5)
        return source
        #return gst.element_factory_make("alsasrc")
        #return gst.element_factory_make("gconfaudiosrc")



class FsUISession:
    "This is one session (audio or video depending on the source)"
    
    def __init__(self, conference, source):
        self.conference = conference
        self.source = source
        self.streams = []
        self.fssession = conference.new_session(source.get_type())
        self.fssession.uisession = self
        if source.get_type() == farsight.MEDIA_TYPE_VIDEO:
            # We prefer H263-1998 because we know it works
            # We don't know if the others do work
            # We know H264 doesn't work for now or anything else
            # that needs to send config data
            self.fssession.set_codec_preferences( [ \
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "THEORA",
                               farsight.MEDIA_TYPE_VIDEO,
                               90000),
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "H264",
                               farsight.MEDIA_TYPE_VIDEO,
                               0),
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "H263-1998",
                               farsight.MEDIA_TYPE_VIDEO,
                               0),
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "H263",
                               farsight.MEDIA_TYPE_VIDEO,
                               0)
                ])
        elif source.get_type() == farsight.MEDIA_TYPE_AUDIO:
            self.fssession.set_codec_preferences( [ \
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "PCMA",
                               farsight.MEDIA_TYPE_AUDIO,
                               0),
                farsight.Codec(farsight.CODEC_ID_ANY,
                               "PCMU",
                               farsight.MEDIA_TYPE_AUDIO,
                               0),
                # The gst speexenc element breaks timestamps
                farsight.Codec(farsight.CODEC_ID_DISABLE,
                               "SPEEX",
                               farsight.MEDIA_TYPE_AUDIO,
                               16000),
                # Sadly, vorbis is not currently compatible with live streaming :-(
                farsight.Codec(farsight.CODEC_ID_DISABLE,
                               "VORBIS",
                               farsight.MEDIA_TYPE_AUDIO,
                               0),
                ])

        self.sourcepad = self.source.get_src_pad()
        self.sourcepad.link(self.fssession.get_property("sink-pad"))

    def __del__(self):
        self.sourcepad(unlink)
        self.source.put_src_pad(self.sourcepad)
    def __stream_finalized(self, s):
        self.streams.remove(s)
            
    def new_stream(self, id, participant):
        "Creates a new stream for a specific participant"
        transmitter_params = {}
        # If its video, we start at port 9078, to make it more easy
        # to differentiate it in a tcpdump log
        if self.source.get_type() == farsight.MEDIA_TYPE_VIDEO and \
               TRANSMITTER == "rawudp":
            cand = farsight.Candidate()
            cand.component_id = farsight.COMPONENT_RTP
            cand.port = 9078
            transmitter_params["preferred-local-candidates"] = [cand]
        realstream = self.fssession.new_stream(participant.fsparticipant,
                                             farsight.DIRECTION_BOTH,
                                             TRANSMITTER, transmitter_params)
        stream = FsUIStream(id, self, participant, realstream)
        self.streams.append(weakref.ref(stream, self.__stream_finalized))
        return stream

    def dtmf_start(self, event, method):
        if (event == "*"):
            event = farsight.DTMF_EVENT_STAR
        elif (event == "#"):
            event = farsight.DTMF_EVENT_POUND
        else:
            event = int(event)
        self.fssession.start_telephony_event(event, 2, method)
        
    def dtmf_stop(self, method):
        self.fssession.stop_telephony_event(method)

    def codecs_changed(self):
        "Callback from FsSession"
        for s in self.streams:
            try:
                s().codecs_changed()
            except AttributeError:
                pass

    def send_stream_codecs(self, codecs, sourcestream):
        for s in self.streams:
            stream = s()
            if stream and stream is not sourcestream:
                stream.connect.send_codecs(stream.participant.id,
                                           sourcestream.id,
                                           codecs,
                                           sourcestream.participant.id)

class FsUIStream:
    "One participant in one session"

    def __init__(self, id, session, participant, fsstream):
        self.id = id
        self.session = session
        self.participant = participant
        self.fsstream = fsstream
        self.connect = participant.connect
        self.fsstream.uistream = self
        self.fsstream.connect("src-pad-added", self.__src_pad_added)
        self.send_codecs = False
        self.last_codecs = None
        self.last_stream_codecs = None
        self.candidates = []

    def local_candidates_prepared(self):
        "Callback from FsStream"
        self.connect.send_candidates_done(self.participant.id, self.id)
    def new_local_candidate(self, candidate):
        "Callback from FsStream"
        self.connect.send_candidate(self.participant.id, self.id, candidate)
    def __src_pad_added(self, stream, pad, codec):
        "Callback from FsStream"
        if self.session.source.get_type() == farsight.MEDIA_TYPE_VIDEO:
            self.participant.link_video_sink(pad)
        else:
            self.participant.pipeline.link_audio_sink(pad)

    def candidate(self, candidate):
        "Callback for the network object."
        self.candidates.append(candidate)
    def candidates_done(self):
        "Callback for the network object."
        self.fsstream.set_remote_candidates(self.candidates)
        self.candidates = []
    def codecs(self, codecs):
        "Callback for the network object. Set the codecs"

        print "Remote codecs"
        for c in codecs:
            print "Got remote codec from %s/%s %s" % \
                  (self.participant.id, self.id, c.to_string())
        oldcodecs = self.fsstream.get_property("remote-codecs")
        if oldcodecs == codecs:
            return
        try:
            self.fsstream.set_remote_codecs(codecs)
        except AttributeError:
            print "Tried to set codecs with 0 codec"
        self.send_local_codecs()
        self.send_stream_codecs()


    def send_local_codecs(self):
        "Callback for the network object."
        self.send_codecs = True
        self.check_send_local_codecs()

    def codecs_changed(self):
        self.check_send_local_codecs()
        self.send_stream_codecs()

    def check_send_local_codecs(self):
        "Internal function to send our local codecs when they're ready"
        if not self.send_codecs:
            return
        if not self.session.fssession.get_property("codecs-ready"):
            print "Codecs are not ready"
            return
        codecs = self.session.fssession.get_property("codecs")
        assert(codecs is not None and len(codecs) > 0)
        if (codecs == self.last_codecs):
            return
        self.last_codecs = codecs
        print "sending local codecs"
        self.connect.send_codecs(self.participant.id, self.id, codecs)

    def send_stream_codecs(self):
        if not self.connect.is_server:
            return
        if not self.session.fssession.get_property("codecs-ready"):
            return
        codecs = self.fsstream.get_property("negotiated-codecs")
        if codecs:
            self.session.send_stream_codecs(codecs, self)

    def recv_codecs_changed(self, codecs):
        self.participant.recv_codecs_changed()


    def __remove_from_send_codecs_to(self, participant):
        self.send_codecs_to.remote(participant)


    def send_codecs_to(self, participant):
        codecs = self.fsstream.get_property("negotiated-codecs")
        print "sending stream %s codecs from %s to %s" % \
              (self.id, self.participant.id, participant.id)
        if codecs:
            participant.connect.send_codecs(participant.id, self.id, codecs,
                                            self.participant.id)            


class FsUIParticipant:
    "Wraps one FsParticipant, is one user remote contact"
    
    def __init__(self, connect, id, cname, pipeline, mainui):
        self.connect = connect
        self.id = id
        self.cname = cname
        self.pipeline = pipeline
        self.mainui = mainui
        self.fsparticipant = pipeline.conf.new_participant(cname)
        self.outcv = threading.Condition()
        self.funnel = None
        self.make_widget()
        self.streams = {}
        if VIDEO:
            self.streams[int(farsight.MEDIA_TYPE_VIDEO)] = \
              pipeline.videosession.new_stream(
                int(farsight.MEDIA_TYPE_VIDEO), self)
        if AUDIO:
            self.streams[int(farsight.MEDIA_TYPE_AUDIO)] = \
              pipeline.audiosession.new_stream(
                int(farsight.MEDIA_TYPE_AUDIO), self)
        
    def candidate(self, media, candidate):
        "Callback for the network object."
        self.streams[media].candidate(candidate)
    def candidates_done(self, media):
        "Callback for the network object."
        self.streams[media].candidates_done()
    def codecs(self, media, codecs):
        "Callback for the network object."
        self.streams[media].codecs(codecs)
    def send_local_codecs(self):
        "Callback for the network object."
        for id in self.streams:
            self.streams[id].send_local_codecs()

    def make_widget(self):
        "Make the widget of the participant's video stream."
        gtk.gdk.threads_enter()
        self.builder = gtk.Builder()
        self.builder.add_from_file(builderprefix + "user-frame.ui")
        self.userframe = self.builder.get_object("user_frame")
        self.builder.get_object("frame_label").set_text(self.cname)
        self.builder.connect_signals(self)
        self.label = gtk.Label()
        self.label.set_alignment(0,0)
        self.label.show()
        self.mainui.hbox_add(self.userframe, self.label)
        gtk.gdk.threads_leave()

    def exposed(self, widget, *args):
        """From the exposed signal, used to create the video sink
        The video sink will be created here, but will only be linked when the
        pad arrives and link_video_sink() is called.
        """
        if not VIDEO:
            return
        try:
            self.videosink.get_by_interface(gst.interfaces.XOverlay).expose()
        except AttributeError:
            try:
                self.outcv.acquire()
                self.videosink = make_video_sink(self.pipeline.pipeline,
                                                 widget.window.xid,
                                                 "uservideosink")
                self.pipeline.pipeline.add(self.videosink)
                self.funnel = gst.element_factory_make("fsfunnel")
                self.pipeline.pipeline.add(self.funnel)
                self.funnel.link(self.videosink)
                self.havesize = self.videosink.get_pad("sink").add_buffer_probe(self.have_size)

                self.videosink.set_state(gst.STATE_PLAYING)
                self.funnel.set_state(gst.STATE_PLAYING)
                self.outcv.notifyAll()
            finally:
                self.outcv.release()
            

    def have_size(self, pad, buffer):
        "Callback on the first buffer to know the drawingarea size"
        x = buffer.caps[0]["width"]
        y = buffer.caps[0]["height"]
        gtk.gdk.threads_enter()
        self.builder.get_object("user_drawingarea").set_size_request(x,y)
        gtk.gdk.threads_leave()
        self.videosink.get_pad("sink").remove_buffer_probe(self.havesize)
        del self.havesize
        return True
                 


    def link_video_sink(self, pad):
        """Link the video sink

        Wait for the funnnel for the video sink to be created, when it has been
        created, link it.
        """
        try:
            self.outcv.acquire()
            while self.funnel is None:
                self.outcv.wait()
            print >>sys.stderr, "LINKING VIDEO SINK"
            pad.link(self.funnel.get_pad("sink%d"))
        finally:
            self.outcv.release()

    def destroy(self):
        if VIDEO:
            try:
                self.videosink.get_pad("sink").disconnect_handler(self.havesize)
                pass
            except AttributeError:
                pass
            self.builder.get_object("user_drawingarea").disconnect_by_func(self.exposed)
            self.streams = {}
            self.outcv.acquire()
            self.videosink.set_locked_state(True)
            self.funnel.set_locked_state(True)
            self.videosink.set_state(gst.STATE_NULL)
            self.funnel.set_state(gst.STATE_NULL)
            self.pipeline.pipeline.remove(self.videosink)
            self.pipeline.pipeline.remove(self.funnel)
            del self.videosink
            del self.funnel
            self.outcv.release()
        gtk.gdk.threads_enter()
        self.userframe.destroy()
        self.label.destroy()
        gtk.gdk.threads_leave()

    def error(self):
        "Callback for the network object."
        if self.id == 1:
            self.mainui.fatal_error("<b>Disconnected from server</b>")
        else:
            print "ERROR ON %d" % (self.id)

    def recv_codecs_changed(self):
        codecs = {}
        for s in self.streams:
            codec = self.streams[s].fsstream.get_property("current-recv-codecs")
            mediatype = self.streams[s].session.fssession.get_property("media-type")
            if len(codec):
                if mediatype in codecs:
                    codecs[mediatype] += codec
                else:
                    codecs[mediatype] = codec
        str = ""
        for mt in codecs:
            str += "<big>" +mt.value_nick.title() + "</big>:\n"
            for c in codecs[mt]:
                str += "  <b>%s</b>: %s %s\n" % (c.id, 
                                                 c.encoding_name,
                                                 c.clock_rate)
        self.label.set_markup(str)

    def send_codecs_to(self, participant):
        for sid in self.streams:
            self.streams[sid].send_codecs_to(participant)
    

class FsMainUI:
    "The main UI and its different callbacks"
    
    def __init__(self, mode, ip, port):
        self.mode = mode
        self.pipeline = FsUIPipeline()
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
            self.client = FsUIClient(ip, port, mycname, FsUIParticipant,
                                     self.pipeline, self)
            self.builder.get_object("info_label").set_markup(
                "<b>%s</b>\nConnected to %s:%s" % (mycname, ip, port))
        elif mode == SERVER:
            self.server = FsUIListener(port, FsUIServer, mycname,
                                       FsUIParticipant, self.pipeline, self)
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

    def show_dtmf(self, button):
        try:
            self.dtmf_builder.present()
        except AttributeError:
            self.dtmf_builder = gtk.Builder()
            self.dtmf_builder.add_from_file(builderprefix + "dtmf.ui")
            self.dtmf_builder.connect_signals(self)
            

    def dtmf_start(self, button):
        if (self.dtmf_builder.get_object("dtmf_as_event").get_active()):
            self.dtmf_last_method = farsight.DTMF_METHOD_RTP_RFC4733
        elif (self.dtmf_builder.get_object("dtmf_as_sound").get_active()):
            self.dtmf_last_method = farsight.DTMF_METHOD_IN_BAND
        else:
            print "Invalid DTMF Method"
            return
        self.pipeline.audiosession.dtmf_start(button.get_label(), \
                                              self.dtmf_last_method)
                                              
    def dtmf_stop(self, button):
        try:
            self.pipeline.audiosession.dtmf_stop(self.dtmf_last_method)
            del self.dtmf_last_method
        except AttributeError:
            pass
    def dtmf_destroy(self, button):
        self.dtmf_builder.get_object("dtmf_window").destroy()
        del self.dtmf_builder



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
