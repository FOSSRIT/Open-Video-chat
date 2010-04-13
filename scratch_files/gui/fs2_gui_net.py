#!/usr/bin/python

# Farsight 2 simple network signalling library for the demo GUI
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

#
# This is the signalling code used by fs2-gui.py
#

import sys, os, pwd, os.path
import socket, struct
import gc


try:
    import pygst
    pygst.require('0.10')
        
    import gst
except ImportError, e:
    raise SystemExit("Gst-Python couldn't be found! (%s)" % (e[0]))

try:
    import farsight
except:
    sys.path.append(os.path.join(os.path.dirname(__file__),
                                 '..', '..', 'python', '.libs'))
    import farsight

import gobject

class FsUIConnect:
    ERROR = 0
    CODECS = 1
    CANDIDATE = 2
    CANDIDATES_DONE = 3
    INTRO = 4

    def __reset(self):
        self.type = None
        self.media = None
        self.size = struct.calcsize("!IIIIII")
        self.data = ""
        self.dest = -1
        self.src = -1
 
    
    def __init__(self, sock, callbacks, myid=0):
        self.sock = sock
        self.__reset()
        self.callbacks = callbacks
        self.myid = myid
        self.partid = 1
        self.is_server = True
        sock.setblocking(0)
        gobject.io_add_watch(self.sock.fileno(), gobject.IO_IN,
                             self.__data_in)
        gobject.io_add_watch(self.sock.fileno(),
                             gobject.IO_ERR | gobject.IO_HUP,
                             self.__error)

    def __error(self, source, condition):
        print "have error"
        if (self.src >= 0):
            self.callbacks[self.ERROR](self.src)
        else:
            self.callbacks[self.ERROR](self.partid)
        return False

    def __data_in(self, source, condition):
        data = self.sock.recv(self.size-len(self.data))

        if len(data) == 0:
            print "received nothing"
            if (self.src >= 0):
                self.callbacks[self.ERROR](self.src)
            else:
                self.callbacks[self.ERROR](self.partid)
            return False
        
        self.data += data
        if len(self.data) == self.size:
            if self.type is not None:
                if self.type == self.CODECS:
                    data = self.__codecs_from_string(data)
                elif self.type == self.CANDIDATE:
                    data = self.__candidate_from_string(data)
                else:
                    data = self.data
                self.callbacks[self.type](self.src, self.dest,
                                          self.media, data)
                self.__reset()
            else:
                (check,
                 self.src,
                 self.dest,
                 self.type,
                 self.media,
                 self.size) = struct.unpack("!IIIIII", self.data)
                if check != 0xDEADBEEF:
                    print "CORRUPTION"
                    sys.exit(1)
                if self.myid > 1 and self.dest != self.myid:
                    print "GOT MESSAGE FOR %d, but I am %d" % (self.dest,
                                                               self.myid)
                    sys.exit(1)
                self.data=""
                if self.size == 0:
                    self.callbacks[self.type](self.src, self.dest,
                                              self.media, None)
                    self.__reset()
        return True

    def __send_data(self, dest, type, media=0, data="", src=None):
        if src is None: src = self.myid
        if src == 0 and type != self.INTRO: raise Exception
        try:
            self.sock.sendall(struct.pack("!IIIIII",
                                          0xDEADBEEF,
                                          int(src),
                                          int(dest),
                                          int(type),
                                          int(media),
                                          len(data)))
            self.sock.sendall(data)
        except socket.error:
            print "have error"
            self.callbacks[self.ERROR](self.partid)


    def send_error(self, dest, src):
        self.__send_data(dest, self.ERROR, src=src)
    def send_intro(self, dest, cname, src=None):
        self.__send_data(dest, self.INTRO, data=cname, src=src)
    def send_codecs(self, dest, media, codecs, src=None):
        self.__send_data(dest, self.CODECS,
                         media=media,
                         data=self.__codecs_to_string(codecs), src=src)
    def send_candidate(self, dest, media, candidate, src=None):
        self.__send_data(dest, self.CANDIDATE, media=media,
                         data=self.__candidate_to_string(candidate), src=src)
    def send_candidates_done(self, dest, media, src=None):
        self.__send_data(dest, self.CANDIDATES_DONE, media=media, src=src)

    def __del__(self):
        try:
            self.sock.close()
        except AttributeError:
            pass


    def __candidate_to_string(self, candidate):
        return "|".join((
            candidate.foundation,
            str(candidate.component_id),
            candidate.ip,
            str(candidate.port),
            candidate.base_ip,
            str(candidate.base_port),
            str(int(candidate.proto)),
            str(candidate.priority),
            str(int(candidate.type)),
            candidate.username,
            candidate.password))

    def __candidate_from_string(self, string):
        candidate = farsight.Candidate()
        (candidate.foundation,
         component_id,
         candidate.ip,
         port,
         candidate.base_ip,
         base_port,
         proto,
         priority,
         type,
         candidate.username,
         candidate.password) = string.split("|")
        candidate.component_id = int(component_id)
        candidate.port = int(port)
        candidate.base_port = int(base_port)
        candidate.proto = int(proto)
        candidate.priority = int(priority)
        candidate.type = int(type)
        return candidate

    def __codecs_to_string(self, codecs):
        codec_strings = []
        for codec in codecs:
            start = " ".join((str(codec.id),
                              codec.encoding_name,
                              str(int(codec.media_type)),
                              str(codec.clock_rate),
                              str(codec.channels)))
            codec = "".join((start,
                             "|",
                             ";".join(["=".join(i) for i in codec.optional_params])))
            codec_strings.append(codec)
            
        return "\n".join(codec_strings)


    def __codecs_from_string(self, string):
        codecs = []
        for substring in string.split("\n"):
            (start,end) = substring.split("|")
            (id, encoding_name, media_type, clock_rate, channels) = start.split(" ")
            codec = farsight.Codec(int(id), encoding_name, int(media_type),
                               int(clock_rate))
            codec.channels = int(channels)
            if len(end):
                codec.optional_params = \
                  [tuple(x.split("=",1)) for x in end.split(";") if len(x) > 0]
            codecs.append(codec)
        return codecs

class FsUIConnectClient (FsUIConnect):
    def __init__(self, ip, port, callbacks):
        sock = socket.socket()
        sock.connect((ip, port))
        FsUIConnect.__init__(self, sock, callbacks)
        self.is_server = False

class FsUIListener:
    def __init__(self, port, callback, *args):
        self.sock = socket.socket()
        self.callback = callback
        self.args = args
        bound = False
        while not bound:
            try:
                self.sock.bind(("", port))
                bound = True
            except socket.error, e:
                port += 1
        self.port = port
        print "Bound to port ", port
        self.sock.setblocking(0)
        gobject.io_add_watch(self.sock.fileno(), gobject.IO_IN, self.data_in)
        gobject.io_add_watch(self.sock.fileno(),
                             gobject.IO_ERR | gobject.IO_HUP,
                             self.error)
        self.sock.listen(3)

    def error(self, source, condition):
        print "Error on listen"
        sys.exit(1)
        return False

    def data_in(self, source, condition):
        (sock,addr) = self.sock.accept()
        self.callback(sock, *self.args)
        return True
    
class FsUIClient:
    def __init__(self, ip, port, cname, get_participant, *args):
        self.participants = {}
        self.get_participant = get_participant
        self.args = args
        self.cname = cname
        self.connect = FsUIConnectClient(ip, port, (self.__error,
                                                    self.__codecs,
                                                    self.__candidate,
                                                    self.__candidate_done,
                                                    self.__intro))
        self.connect.send_intro(1, cname)

    def __codecs(self, src, dest, media, data):
        print "Got codec Src:%d dest:%d data:%s" % (src, dest, data)
        self.participants[src].codecs(media, data)
    def __candidate(self, src, dest, media, data):
        self.participants[src].candidate(media, data)
    def __candidate_done(self, src, dest, media, data):
        self.participants[src].candidates_done(media)
    def __intro(self, src, dest, media, cname):
        print "Got Intro from %s, I am %d" % (src, dest)
        if src == 1:
            self.connect.myid = dest
        if not self.participants.has_key(src):
            if src != 1:
                self.connect.send_intro(src, self.cname)
            self.participants[src] = self.get_participant(self.connect, src,
                                                          cname,
                                                          *self.args)
    def __error(self, participantid, *arg):
        print "Client Error", participantid
        if participantid == 1:
            # Communication error with server, its over
            self.participants[participantid].error()
        else:
            self.participants[participantid].destroy()
            del self.participants[participantid]
            gc.collect()


class FsUIServer:
    nextid = 2
    participants = {}

    def __init__(self, sock, cname, get_participant, *args):
        self.cname = cname
        self.get_participant = get_participant
        self.args = args
        self.connect = FsUIConnect(sock, (self.__error,
                                          self.__codecs,
                                          self.__candidate,
                                          self.__candidate_done,
                                          self.__intro), 1)
    def __codecs(self, src, dest, media, data):
        FsUIServer.participants[src].codecs(media, data)
    def __candidate(self, src, dest, media, data):
        if dest == 1:
            FsUIServer.participants[src].candidate(media, data)
        else:
            print data
            FsUIServer.participants[dest].connect.send_candidate(dest,
                                                                 media,
                                                                 data,
                                                                 src)
    def __candidate_done(self, src, dest, media, data):
        if dest == 1:
            FsUIServer.participants[src].candidates_done(media)
        else:
            FsUIServer.participants[dest].connect.send_candidates_done(dest,
                                                                       media,
                                                                       src)
    def __intro(self, src, dest, media, cname):
        print "Got Intro from %s to %s" % (src, dest)
        if src == 0 and dest == 1:
            newid = FsUIServer.nextid
            # Forward the introduction to all other participants
            for pid in FsUIServer.participants:
                print "Sending from %d to %d" % (newid, pid)
                FsUIServer.participants[pid].connect.send_intro(pid, cname,
                                                                newid)
            self.connect.send_intro(newid, self.cname)
            self.connect.partid = newid
            FsUIServer.participants[newid] = self.get_participant(self.connect,
                                                                  newid,
                                                                  cname,
                                                                  *self.args)
            FsUIServer.participants[newid].send_local_codecs()
            FsUIServer.nextid += 1
        elif dest != 1:
            FsUIServer.participants[dest].connect.send_intro(dest,
                                                             cname,
                                                             src)
            FsUIServer.participants[src].send_codecs_to(
                        FsUIServer.participants[dest])
        else:
            print "ERROR SRC != 0"
            
    def __error(self, participantid, *args):
        print "Server Error", participantid
        FsUIServer.participants[participantid].destroy()
        del FsUIServer.participants[participantid]
        gc.collect()
        for pid in FsUIServer.participants:
            FsUIServer.participants[pid].connect.send_error(pid, participantid)

if __name__ == "__main__":
    class TestMedia:
        def __init__(self, pid, id, connect):
            self.pid = pid
            self.id = id
            self.connect = connect
            candidate = farsight.Candidate()
            candidate.component_id = 1
            connect.send_candidate(self.pid, self.id, candidate)
            connect.send_candidates_done(self.pid, self.id)
        def candidate(self, candidate):
            print "Got candidate", candidate
        def candidates_done(self):
            print "Got candidate done"
        def codecs(self, codecs):
            if self.connect.myid != 1:
                self.connect.send_codecs(1, self.id,
                                        [farsight.Codec(self.connect.myid,
                                                       "codec-name",
                                                       self.pid,
                                                       self.id)])
       
        def send_local_codecs(self):
            print "Send local codecs to %s for media %s" % (self.pid, self.id)
            self.connect.send_codecs(self.pid, self.id,
                                     [farsight.Codec(self.connect.myid,
                                                     "local_codec",
                                                     self.pid,
                                                     self.id)])
        def get_codecs(self):
            return [farsight.Codec(self.connect.myid,
                                   "nego-codecs",
                                   self.pid,
                                   self.id)]
            
            
    class TestParticipant:
        def __init__(self, connect, id, cname, *args):
            self.id = id
            self.streams = {1: TestMedia(id, 1, connect),
                            2: TestMedia(id, 2, connect)}
            self.cname = cname
            self.connect = connect
            print "New Participant %s and cname %s" % (id,cname)
        def candidate(self, media, candidate):
            self.streams[media].candidate(candidate)
        def candidates_done(self, media):
            self.streams[media].candidates_done()
        def codecs(self, media, codecs):
            self.streams[media].codecs(codecs)
        def send_local_codecs(self):
            for id in self.streams:
                self.streams[id].send_local_codecs()
        def destroy(self):
            pass
        def send_codecs_to(self, participant):
            for sid in self.streams:
                print "to: %s from: %s" % (str(participant.id), (self.id))
                participant.connect.send_codecs(participant.id,
                                                self.streams[sid].id,
                                                self.streams[sid].get_codecs(),
                                                self.id)
        def error(self):
            print "ERROR"
            sys.exit(1)
        def destroy(self):
            passs
            

    mycname = "test"
    mainloop = gobject.MainLoop()
    gobject.threads_init()
    if len(sys.argv) > 1:
        client = FsUIClient("127.0.0.1", int(sys.argv[1]),
                            "cname" + sys.argv[1],
                            TestParticipant)
    else:
        listener = FsUIListener(9893, FsUIServer, "cnameServ", TestParticipant)
    mainloop.run()
