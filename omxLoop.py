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
            self.INSTANCES += Player(0, mediafile, args=args)
            self.playerOne = self.INSTANCES[0]
            self.playerOne.initialize()
            wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            self.playerOne.setAlpha(255)
            self.playerOne.playPause()
            volume = self.playerOne.setVolume(0)
            print('volume=%s' % volume)
        else:
            dbusNUM = int(not self.playerOne.dbusNUM)
            self.INSTANCES += Player(dbusNUM, mediafile, args=args)
            self.playerTwo = self.INSTANCES[1]
            self.playerTwo.initialize()
            wait = float(future) - time.time()
            print('sleeping %s' % wait)
            if wait > 0:
                sleep(wait)
            self.playerTwo.setAlpha(255)
            self.playerTwo.playPause()
            volume = self.playerTwo.setVolume(0)
            print('volume=%s' % volume)
            if self.playerOne.isAlive() is True:
                self.playerOne.exit()
            self.INSTANCES.pop(0)

    def stop(self, future):
        wait = float(future) - time.time()
        print('sleeping %s' % wait)
        if wait > 0:
            sleep(wait)
        for i in range(len(self.INSTANCES)):
            self.INSTANCES[i].exit()
        self.INSTANCES = []
