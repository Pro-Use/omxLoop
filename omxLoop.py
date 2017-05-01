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

    def __start(self, playerNum, future, af):
            print('initialised %s' % self.INSTANCES[playerNum].initialize())
            if af is True:
                print('seek to start %s' % self.INSTANCES[playerNum].setPosition(0))
                wait = (float(future) - time.time()) - 0.5
            else:
                wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            else:
                sleep(0.1)
            if af is False:
                print('alpha = %s' % self.INSTANCES[playerNum].setAlpha(255))
            print('play = %s' % self.INSTANCES[playerNum].playPause())
            print('volume = %s' % self.INSTANCES[playerNum].setVolume(0))

    def loadfile(self, mediafile, future=0, loop=True, args=None, replace=True, af=False):
        ARGS = ['--vol', '-6000']
        if args is not None:
            ARGS += args
        if loop is True:
            ARGS += ['--loop']
        self.__cleanup()
        dbusNUM = 0
        if len(self.INSTANCES) != 0:
            while dbusNUM in self.INSTANCES.keys():
                dbusNUM += 1
        player = Player(dbusNUM, mediafile, args=ARGS)
        self.INSTANCES[dbusNUM] = player
        self.__start(dbusNUM, future, af)
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
