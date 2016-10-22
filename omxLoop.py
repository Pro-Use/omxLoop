#!/usr/bin/python

from time import sleep
from threading import Thread
from pyomxplayer import OMXPlayer
from omxDbus import PlayerInterface
import subprocess
import pexpect
import re

class OMXloopSingle(object):
	INSTANCES=0
	VISIBLE=0
	HIDDEN=1
	FILE=''
	EXIT=False
	TOLERANCE=300000
	def __init__(self, mediafile, addargs=''):
		self.FILE = mediafile
		self.ADDARGS = addargs
		args = self.ADDARGS+' --no-osd --layer '+str(self.VISIBLE)+' --dbus_name=org.mpris.MediaPlayer2.omxplayer'+str(self.VISIBLE)
		omx0=OMXPlayer(mediafile, args)
		self.INSTANCES += 1
		print 'players='+str(self.INSTANCES)
	        self._loop_thread = Thread(target=self._loop_control)
	        self._loop_thread.start()

	def _loop_control(self):
		while True:
			if self.INSTANCES < 2:
				self.HIDDEN=int(not(self.VISIBLE))
				print 'hidden='+str(self.HIDDEN)
				args = self.ADDARGS+' --no-osd --alpha=0 --layer '+str(self.HIDDEN)+' --dbus_name=org.mpris.MediaPlayer2.omxplayer'+str(self.HIDDEN)
				print args
				if self.HIDDEN == 0:
					omx0=OMXPlayer(self.FILE, args)
				else:
					omx1=OMXPlayer(self.FILE, args)
		                self.INSTANCES += 1
                		print 'players='+str(self.INSTANCES) 
				sleep(1)
				self.hiddenCMD = PlayerInterface(self.HIDDEN)
				self.hiddenCMD.initialize()
				self.hiddenCMD.mute()
				self.hiddenCMD.playPause()
				self.hiddenCMD.setPosition(0)
			else:
				self.visibleCMD = PlayerInterface(self.VISIBLE)
				print self.visibleCMD.initialize()
				self.visibleDur = self.visibleCMD.duration()
				self.remaining = self.visibleDur
				print 'remaining='+str(self.remaining)
				while self.remaining > self.TOLERANCE:
					visiblePos = self.visibleCMD.position()
					self.remaining = self.visibleDur - visiblePos
#					sleep(0.5)
				if self.EXIT == True:
					break
				self.hiddenCMD.playPause()
				sleep(0.15)
				print 'unhide='+str(self.hiddenCMD.unhide())
				print 'unmute='+str(self.hiddenCMD.unmute())
#				self.visibleCMD.hide()
				self.visibleCMD.exit()
				print 'self.remaining='+str(self.remaining)
				print 'unPausing '+self.FILE
				self.VISIBLE=int(not(self.VISIBLE))
				self.INSTANCES -= 1
                		print 'players='+str(self.INSTANCES) 
				sleep(1)

        def setAlpha(self, alpha):
                print 'setAlpha='+str(self.visibleCMD.setAlpha(int(alpha)))

	def pause(self):
		self.visibleCMD.playPause() 

        def seek(self, seconds):
                if self.remaining < 680000:
                        sleep(2)
		self.visibleCMD.setPosition(seconds)

	def stop(self):
		if self.remaining < 680000:
			sleep(2)
		self.EXIT = True
		self.visibleDur = 0
		sleep(0.1)
		self.visibleCMD.exit()
		self.hiddenCMD.exit()

	def loadfile(self, mediafile, arg='replace'):
		if arg not in ['replace', 'append']:
			print "loadfile arguement must be either 'replace' or 'append'"
		else:
                	if self.remaining < 680000:
                        	sleep(2)
			self.FILE = mediafile
			self.hiddenCMD.exit()
			args = self.ADDARGS+' --no-osd --alpha=0 --layer '+str(self.HIDDEN)+' --dbus_name=org.mpris.MediaPlayer2.omxplayer'+str(self.HIDDEN)
			print args
			if self.HIDDEN == 0:
				omx0=OMXPlayer(self.FILE, args)
			else:
				omx1=OMXPlayer(self.FILE, args)
               		self.hiddenCMD = PlayerInterface(self.HIDDEN)
	                self.hiddenCMD.initialize()
        	        self.hiddenCMD.mute()
                	self.hiddenCMD.playPause()
	                self.hiddenCMD.setPosition(0)
			sleep(1)
			if arg == 'replace':
		                self.visibleDur = 0
                		sleep(0.5)
		                self.visibleCMD.exit()
	

class OMXplaySingle(object):
        def __init__(self, mediafile, addargs=''):
                self.FILE = mediafile
                self.ADDARGS = addargs
                args = self.ADDARGS+' --no-osd --layer 4 --dbus_name=org.mpris.MediaPlayer2.omxplayer4'
                omxSingle=OMXPlayer(mediafile, args)


        def stop(self):
                self.singleCMD = PlayerInterface(4)
                self.singleCMD.initialize()
                self.singleCMD.exit()

class OMXplayCrazy(object):
        def __init__(self, mediafile, addargs=''):
                self.FILE = mediafile
                self.ADDARGS = addargs
                args = self.ADDARGS+' --no-osd --layer 4 --dbus_name=org.mpris.MediaPlayer2.omxplayer4'
                omxSingle=OMXPlayer(mediafile, args)

        def crazy(self):
                self.singleCMD = PlayerInterface(4)
                self.singleCMD.initialize()
		self.duration = self.singleCMD.duration()
		self.span = self.duration - 4000000
		print self.duration
		print self.span
		while self.Exit != True:				
			self.singleCMD.seek

        def stop(self):
                self.singleCMD = PlayerInterface(4)
                self.singleCMD.initialize()
                self.singleCMD.exit()

