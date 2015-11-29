#!/usr/bin/python -u
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of Apache License v2 or later.

from __future__ import print_function, division
import sys
from threading import Event
from gattlib import GATTRequester
import time


class Requester(GATTRequester):
    def __init__(self, wakeup, *args):
        GATTRequester.__init__(self, *args)
        self.wakeup = wakeup

    def on_notification(self, handle, data):
		#print("- notification on handle: {}\n".format(handle))
		i = 0
		data2 = data[3:]
		'''
		for d in data2:
			print(hex(ord(d)), end=' ')
		print("")
		'''

		i = 0
		axl = 0x00
		axh = 0x00
		for d in data2:
			if i > 5 and i <= 11:
				if i == 6: # get axl and axh
					axl = int(hex(ord(d)), 16)
					#print("axl: ", axl, hex(ord(d)))
				if i == 7:
					axh = int(hex(ord(d)), 16)
					#print("axh: ", axh, hex(ord(d)))
					axmsb = axh << 8
					axlsb = axl
					ax = axmsb + axlsb
					if ax >= 32768:
						ax -= 65536
					#print ("ax:axmsb:axlsb ", ax / (32768/2), axmsb, axlsb, ax)
				if i == 8: # get axl and axh
					ayl = int(hex(ord(d)), 16)
					#print("ayl: ", ayl, hex(ord(d)))
				if i == 9:
					ayh = int(hex(ord(d)), 16)
					#print("ayh: ", ayh, hex(ord(d)))
					aymsb = ayh << 8
					aylsb = ayl
					ay = aymsb + aylsb
					if ay >= 32768:
						ay -= 65536
					#print ("ay:aymsb:aylsb ", ay / (32768/2), aymsb, aylsb, ay)
				if i == 10: # get axl and axh
					azl = int(hex(ord(d)), 16)
					#print("azl: ", azl, hex(ord(d)))
				if i == 11:
					azh = int(hex(ord(d)), 16)
					#print("azh: ", azh, hex(ord(d)))
					azmsb = azh << 8
					azlsb = azl
					az = azmsb + azlsb
					if az >= 32768:
						az -= 65536
					#print ("az:azmsb:azlsb ", az / (32768/2), azmsb, azlsb, az)
			i += 1
		print(ax/4096, ay/4096, az/4096)

		#self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, address):
		self.received = Event()
		self.requester = Requester(self.received, address, False, "hci1")

		self.connect()
		self.requester.write_by_handle(0x3C, str(bytearray([0x38, 0x03])))
		self.requester.write_by_handle(0x3E, str(bytearray([0x0A])))
		data = self.requester.read_by_handle(0x3C)[0]
		for d in data:
			print(hex(ord(d)), end=' ')
		print("")
		self.requester.write_by_handle(0x3A, str(bytearray([0x1, 0x0])))
		self.wait_notification()

    def connect(self):
        print("Connecting...", end=' ')
        sys.stdout.flush()

        self.requester.connect()
        print("OK!")

    def wait_notification(self):
        print("\nThis is a bit tricky. You need to make your device to send\n"
              "some notification. I'll wait...")
        self.received.wait()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <addr>".format(sys.argv[0]))
        sys.exit(1)

    ReceiveNotification("B0:B4:48:BF:C3:83")
    print("Done.")
