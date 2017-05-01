#!/usr/bin/python

from time import sleep
from omxDbus import Player
import time
import subprocess



class OMXcontrol(object):
    def __init__(self):
        self.INSTANCES = {}
        res = subprocess.check_output('fbset -s', stderr=subprocess.STDOUT, shell=True)
        res = res.split()
        self.RES = res[3:5]

    def __cleanup(self):
            for instance in self.INSTANCES.keys():
                if not self.INSTANCES[instance].isAlive():
                    del self.INSTANCES[instance]

    def __start(self, playerNum, future, pos, alpha, vol):
            if self.INSTANCES[playerNum].initialize():
                print('seek to start %s' % self.INSTANCES[playerNum].setPosition(0))
                video = self.INSTANCES[playerNum].videoStreamCount()
                if pos is not None:
                        dimensions = self.INSTANCES[playerNum].dimensions()
                        print dimensions
                        self.INSTANCES[playerNum].setVPosition(
                            pos[0], pos[1], pos[0] + dimensions[0], pos[1] + dimensions[1])
                wait = float(future) - time.time()
                print('sleeping %s' % wait)
                if wait > 0:
                    sleep(wait)
                else:
                    sleep(0.1)
                if video > 0:
                    print('alpha = %s' % self.INSTANCES[playerNum].setAlpha(alpha))
                print('play = %s' % self.INSTANCES[playerNum].playPause())
                print('volume = %s' % self.INSTANCES[playerNum].setVolume(vol))
                return True
            else:
                return False

    def loadfile(self, mediafile, future=0, loop=True, args=None, crop=None, pos=None, alpha=255, vol=0):
        self.__cleanup()
        dbusNUM = 0
        if len(self.INSTANCES) != 0:
            while dbusNUM in self.INSTANCES.keys():
                dbusNUM += 1
        ARGS = ['--vol', '-6000', '--layer', '%s' % dbusNUM]
        if args is not None:
            ARGS += args
        if loop is True:
            ARGS += ['--loop']
        if crop is not None:
            if isinstance(crop, list) and len(crop) == 4:
                ARGS += ['--crop', '%s,%s,%s,%s' % (crop[0], crop[1], crop[2], crop[3])]
                if pos is None or isinstance(pos, list) is False or len(pos) != 4:
                    pos = crop
            if isinstance(pos, list):
                if len(pos) == 4:
                    ARGS += ['--win', '%s,%s,%s,%s' % (pos[0], pos[1], pos[2], pos[3])]
                elif len(pos) != 2:
                    pos = None
        player = Player(dbusNUM, mediafile, args=ARGS)
        self.INSTANCES[dbusNUM] = player
        self.__start(dbusNUM, future, pos, alpha, vol)
        return self.INSTANCES.keys()

    def stop(self, future=0, instances=None):
        wait = float(future) - time.time()
        print('sleeping %s' % wait)
        if wait > 0:
            sleep(wait)
        if instances is None or not isinstance(instances, list):
            instances = self.INSTANCES.keys()
        for instance in instances:
            self.INSTANCES[instance].exit()
            del self.INSTANCES[instance]
