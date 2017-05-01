#!/usr/bin/python

from time import sleep
from threading import Timer
import omxLoop
from socket import *
import time
import RPi.GPIO as GPIO
import netifaces
import os

ACTIONS = ['stop', 'playLoop', 'playSingle']
ARGS = {'loop': ' -o local', 'live': ' -o local', 'single': ' -o local'}
# GPIOTYPE = "LAMP"
# GPIOPINS = [ 26, 19, 13, 6, 5]
GPIOTYPE = "PS"
GPIOPINS = [15, 18]
VIDEODIR = "/home/pi/video/"
LOCALIP = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']


class run():
    def __init__(self):
        self.current = ACTIONS[0]
        self.overlays = []
        self.layers = 0
        self.omx = omxLoop.OMXcontrol()

    def stopAll(self, future=0):
        self.omx.stop(future)
        return 'stop'

    def start(self, file, future, type):
        if os.path.exists(VIDEODIR + file):
            args = ['-o', 'local']
            af = '.wav' in file
            if type == 'loop':
                self.omx.loadfile(VIDEODIR + file, future, args=args, af=af)
                return 'playLoop'
            else:
                self.omx.loadfile(VIDEODIR + file, future, loop=False, replace=False, args=args, af=af)
                return 'playSingle'
        else:
            print str(file) + " is not a valid file"
            f = open('missing.log', 'a')
            f.write(str(file) + " is not a valid file")
            f.close()
            return self.current

    def gpio(self, state, pins):
        if state == 'on':
            down = False
        else:
            down = True
        for pin in pins:
            GPIO.output(pin, down)

    def client(self):
        host = LOCALIP
        port = 15000
        buf = 1024
        addr = (host, port)
        UDPSock = socket(AF_INET, SOCK_DGRAM)
        UDPSock.bind(addr)
        GPIO.setmode(GPIO.BCM)
        for i in range(0, len(GPIOPINS)):
            GPIO.setup(GPIOPINS[i], GPIO.OUT)
        print "Waiting to receive messages..."
        while True:
            (data, addr) = UDPSock.recvfrom(buf)
            print "Received message: " + data
            if data == "exit":
                break
            cmd = data.split()
            print(cmd)
            action = cmd[0]
            if action == 'stop':
                self.current = self.stopAll(future=cmd[1])
            elif GPIOTYPE in action:
                future = cmd[2]
                type, channel = action.split('_')
                state = cmd[1]
                if channel == "ALL":
                    pins = GPIOPINS
                else:
                    try:
                        pins = [int(channel)]
                    except:
                        pins = []
                wait = float(future) - time.time()
                if state in ("on", 'off'):
                    c = Timer(wait, self.gpio(state, pins))
                    c.start()
                else:
                    print("%s is not a valid state" % state)
            elif action in ACTIONS:
                future = cmd[2]
                if action == 'playLoop':
                    type = 'loop'
                else:
                    type = 'single'
                file = cmd[1]
                self.current = self.start(file, future, type)
            else:
                print str(action) + " is not a valid command, please choose playLoop, playSingle, or stop"
            print 'current=' + self.current

        GPIO.cleanup()
        UDPSock.close()
        os._exit(0)


if __name__ == '__main__':
    run().client()
