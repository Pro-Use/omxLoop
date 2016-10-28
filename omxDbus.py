#!/usr/bin/python

from time import sleep
import dbus
import subprocess
import os
import signal

class Player(object):
    def __init__(self, dbusNUM, filename, args=[], visible=False, paused=True, muted=True):
        self.dbusNUM = dbusNUM
        self.filename = filename
        self.args = args
        self.visible = visible
        self.paused = paused
        self.muted = muted
        if "--alpha" in self.args:
            self.visible = True
        else:
            self.args.append(['--alpha', '0'])
        if "--vol" in self.args:
            self.muted = False
        else:
            self.args.append(['--vol', '-6000'])
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
        command = ['omxplayer'] + self.args + [self.filename]
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
            self.playPause()
            print('position=%s' % self.position())
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
        except:
            return False

        return True

    def setPosition(self, seconds):
        try:
            self.player_interface.SetPosition(
                dbus.ObjectPath('/not/used'),
                long(seconds * 1000000))
        except:
            return False

        return True

    def setPositionFine(self, seconds):
        try:
            self.player_interface.SetPosition(
                dbus.ObjectPath('/not/used'),
                long(seconds))
        except:
            return False

        return True

    def setAlpha(self, alpha):
        try:
            self.player_interface.SetAlpha(
                dbus.ObjectPath('/not/used'),
                long(alpha))
        except:
            return False

        return True

    def setVPosition(self, x1, y1, x2, y2):
        try:
            position = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
            self.player_interface.VideoPos(
                dbus.ObjectPath('/not/used'),
                str(position))
        except:
            return False

        return True

    def setVCrop(self, x1, y1, x2, y2):
        try:
            crop = "%s %s %s %s" % (str(x1),str(y1),str(x2),str(y2))
            self.player_interface.SetVideoCropPos(
                dbus.ObjectPath('/not/used'),
                str(crop))
        except:
            return False

        return True

    def hide(self):
        try:
            self.player_interface.Action(28)
        except:
            return False

        return True

    def unhide(self):
        try:
            self.player_interface.Action(29)
        except:
            return False

        return True

    def duration(self):
        try:
            Duration=self.properties_interface.Duration()
        except:
            return False

        return Duration

    def position(self):
        try:
            Position=self.properties_interface.Position()
        except:
            Position=False

        return Position

    def dimensions(self):
        try:
            width=self.properties_interface.ResWidth()
            height=self.properties_interface.ResHeight()
            dimensions = "%s %s" % (str(width), str(height))
        except:
            return False

        return dimensions

    def unmute(self):
        try:
            self.properties_interface.Unmute()
        except:
            return False
        return True

    def mute(self):
        try:
            self.properties_interface.Mute()
        except:
            return False

        return True

    def exit(self):
        omxStatus = None
        exitCount = 0
        while omxStatus is None and exitCount < 10:
            self.player_interface.Action(15)
            omxStatus = self.omxplayer.poll()
        if exitCount >= 10:
            try:
                process_group_id = os.getpgid(self.omxplayer.pid)
                os.killpg(process_group_id, signal.SIGTERM)
            except OSError:
                print('Could not find the process to kill')

