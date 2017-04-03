#!/usr/bin/python

from time import sleep
from omxDbus import Player
import time


class OMXcontrol(object):
    def __init__(self):
        self.INSTANCES = {}

    def __cleanup(self):
            for instance in self.INSTANCES.keys():
                if not self.INSTANCES[instance].isAlive():
                    del self.INSTANCES[instance]

    def __start(self, playerNum, future):
            self.INSTANCES[playerNum].initialize()
            wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            else:
                sleep(0.1)
            print('alpha = %s' % self.INSTANCES[playerNum].setAlpha(255))
            print('play = %s' % self.INSTANCES[playerNum].playPause())
            print('volume = %s' % self.INSTANCES[playerNum].setVolume(0))

    def loadfile(self, mediafile, future=0, loop=True, args=None, replace=True):
        ARGS = ['--vol', '-6000']
        if args is not None:
            ARGS += args
        if loop is True:
            ARGS += ['--loop']
        self.__cleanup()
        if len(self.INSTANCES) == 0:
            dbusNUM = 0
        else:
            c = 0
            while c in self.INSTANCES.keys():
                c += 1
            dbusNUM = c
        player = Player(dbusNUM, mediafile, args=ARGS)
        self.INSTANCES[dbusNUM] = player
        self.__start(dbusNUM, future)
        if replace is True:
            sleep(0.2)
            for instance in self.INSTANCES.keys():
                if instance is not dbusNUM:
                    self.INSTANCES[instance].exit()
                    del self.INSTANCES[instance]
        return self.INSTANCES.keys()

    def stop(self, future=0):
        wait = float(future) - time.time()
        print('sleeping %s' % wait)
        if wait > 0:
            sleep(wait)
        for instance in self.INSTANCES.keys():
            self.INSTANCES[instance].exit()
            del self.INSTANCES[instance]
