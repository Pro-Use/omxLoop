#!/usr/bin/python

from time import sleep
from omxDbus import Player
import time


class OMXcontrol(object):
    def __init__(self):
        self.INSTANCES = []

    def loadfile(self, mediafile, future=0, loop=True, args=[]):
        self.FILE = mediafile
        self.FUTURE = future
        if loop is True:
            args += '--loop'
        if len(self.INSTANCES) == 0:
            self.player = Player(0, mediafile, args=args)
            self.INSTANCES += self.player
            self.INSTANCES[0].initialize()
            wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            self.INSTANCES[0].setAlpha(255)
            self.INSTANCES[0].playPause()
            volume = self.INSTANCES[0].setVolume(0)
            print('volume=%s' % volume)
        else:
            dbusNUM = int(not self.INSTANCES[0].dbusNUM)
            self.player = Player(dbusNUM, mediafile, args=args)
            self.INSTANCES += self.player
            self.INSTANCES[1].initialize()
            wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            self.INSTANCES[1].setAlpha(255)
            self.INSTANCES[1].playPause()
            volume = self.INSTANCES[1].setVolume(0)
            print('volume=%s' % volume)
            if self.INSTANCES[0].isAlive() is True:
                self.INSTANCES[0].exit()
            self.INSTANCES.pop(0)

    def stop(self, future):
        wait = float(future) - time.time()
        print('sleeping %s' % wait)
        if wait > 0:
            sleep(wait)
        for i in range(len(self.INSTANCES)):
            self.INSTANCES[i].exit()
        self.INSTANCES = []
