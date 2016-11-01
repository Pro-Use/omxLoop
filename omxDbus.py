#!/usr/bin/python

from time import sleep
import dbus
import subprocess
import os
import signal

class Player(object):
    def __init__(self, dbusNUM, filename, args=None, visible=False, paused=True, muted=True):
        self.dbusNUM = dbusNUM
        self.filename = filename
	self.ARGS = []
        if args is not None:
            self.ARGS += args
#        else:
#            self.ARGS = []
        self.visible = visible
        self.paused = paused
        self.muted = muted
        if "--alpha" in self.ARGS:
            self.visible = True
        else:
            self.ARGS.extend(['--alpha', '0'])
        if "--vol" in self.ARGS or self.muted is False:
            self.muted = False
        else:
            self.ARGS.extend(['--vol', '-6000'])
        self.ARGS += ['--dbus_name', 'org.mpris.MediaPlayer2.omxplayer%s' % self.dbusNUM, '--no-osd']
        print(self.ARGS)

    def _get_dbus_interface(self):
        try:
            OMXPLAYER_DBUS_ADDR='/tmp/omxplayerdbus.pi'
            bus = dbus.bus.BusConnection(
                open(OMXPLAYER_DBUS_ADDR).readlines()[0].rstrip())
            proxy = bus.get_object(
                'org.mpris.MediaPlayer2.omxplayer'+str(self.dbusNUM),
                '/org/mpris/MediaPlayer2',
                introspect=False)
            self.player_interface = dbus.Interface(
                proxy, 'org.mpris.MediaPlayer2.Player')
            self.properties_interface = dbus.Interface(
                proxy, 'org.freedesktop.DBus.Properties')

        except Exception, e:
            print "WARNING: dbus connection could not be established"
            print e
            return False

        return True

    def initialize(self):
        command = ['omxplayer'] + self.ARGS + [self.filename]
        print(command)
        with open(os.devnull, 'w') as devnull:
            self.omxplayer = subprocess.Popen(command, stdin=devnull, stdout=devnull, preexec_fn=os.setsid)
        sleep(0.1) # wait for omxplayer to appear on dbus
        counter = 0
        while not self._get_dbus_interface():
            counter += 1
            if counter == 10:
                break
            sleep(0.1)
        if counter < 10:
            if self.paused is True:
                self.playPause()
            return True
        else:
            return False

    def test(self):
        try:
            self.player_interface.Action(24)
        except:
            return False

        return True
    def playPause(self):
        try:
            self.player_interface.Action(16)
            return True
        except:
            return False


    def setPosition(self, seconds):
        try:
            self.player_interface.SetPosition(
                dbus.ObjectPath('/not/used'),
                long(seconds * 1000000))
            return True
        except:
            return False

    def setPositionFine(self, seconds):
        try:
            self.player_interface.SetPosition(
                dbus.ObjectPath('/not/used'),
                long(seconds))
            return True
        except:
            return False


    def setAlpha(self, alpha):
        try:
            self.player_interface.SetAlpha(
                dbus.ObjectPath('/not/used'),
                long(alpha))
            if alpha != 0:
                self.hidden = False
            return True
        except:
            return False


    def setVPosition(self, x1, y1, x2, y2):
        try:
            position = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
            self.player_interface.VideoPos(
                dbus.ObjectPath('/not/used'),
                str(position))
            return True
        except:
            return False


    def setVCrop(self, x1, y1, x2, y2):
        try:
            crop = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
            self.player_interface.SetVideoCropPos(
                dbus.ObjectPath('/not/used'),
                str(crop))
            return True
        except:
            return False


    def hide(self):
        try:
            self.player_interface.Action(28)
            self.hidden = True
            return True
        except:
            return False


    def unhide(self):
        try:
            self.player_interface.Action(29)
            self.hidden = False
            return True
        except:
            return False


    def duration(self):
        try:
            Duration=self.properties_interface.Duration()
            return Duration
        except:
            return False


    def position(self):
        try:
            Position=self.properties_interface.Position()
            return Position
        except:
            Position=False


    def dimensions(self):
        try:
            width=self.properties_interface.ResWidth()
            height=self.properties_interface.ResHeight()
            dimensions = "%s %s" % (str(width), str(height))
            return dimensions
        except:
            return False


    def unmute(self):
        try:
            self.properties_interface.Unmute()
            return True
        except:
            return False

    def mute(self):
        try:
            self.properties_interface.Mute()
            return True
        except:
            return False

    def setVolume(self, volume):
        try:
            self.properties_interface.Volume(10**(volume/2000.0))
	    self.muted = False
	    return True
        except:
            return False

    def isAlive(self):
        if self.omxplayer.poll() is None:
            return True
        else:
            return False

    def exit(self):
        omxStatus = None
        exitCount = 0
        while omxStatus is None and exitCount < 10:
            self.player_interface.Action(15)
            sleep(0.1)
            omxStatus = self.omxplayer.poll()
            exitCount += 1
        if exitCount >= 10:
            try:
                process_group_id = os.getpgid(self.omxplayer.pid)
                os.killpg(process_group_id, signal.SIGTERM)
            except OSError:
                print('Could not find the process to kill')

