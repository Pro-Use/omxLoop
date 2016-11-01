#!/usr/bin/python

from time import sleep
from omxDbus import Player
import time


class OMXcontrol(object):
    def __init__(self):
        self.INSTANCES = []

    def loadfile(self, mediafile, future=0, loop=True, args=None):
        self.FILE = mediafile
        self.FUTURE = future
	self.ARGS = []
	if args is not None:
	    self.ARGS += args
        if loop is True:
            self.ARGS += ['--loop']
        if len(self.INSTANCES) == 0:
            self.player = Player(0, mediafile, args=self.ARGS)
            self.start(0, future)
        else:
            dbusNUM = int(not self.INSTANCES[0].dbusNUM)
            self.player = Player(dbusNUM, mediafile, args=self.ARGS)
            self.start(1, future)
            if self.INSTANCES[0].isAlive() is True:
		sleep(0.2)
                self.INSTANCES[0].exit()
            self.INSTANCES.pop(0)

    def start(self, playerNum, future):
            self.INSTANCES += [self.player]
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


    def stop(self, future=0):
        wait = float(future) - time.time()
        print('sleeping %s' % wait)
        if wait > 0:
            sleep(wait)
        for i in range(len(self.INSTANCES)):
            self.INSTANCES[i].exit()
        self.INSTANCES = []
