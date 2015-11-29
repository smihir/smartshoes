#!/usr/bin/python -u
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of Apache License v2 or later.

from __future__ import print_function, division

# (*) To communicate with Plotly's server, sign in with credentials file
import plotly.plotly as py

# (*) Useful Python/Plotly tools
import plotly.tools as tls

# (*) Graph objects to piece together plots
from plotly.graph_objs import *
stream_ids = tls.get_credentials_file()['stream_ids']

# Get stream id from stream id list 
stream_id = stream_ids[0]

# Make instance of stream id object 
stream = Stream(
    token=stream_id,  # (!) link stream id to 'token' key
    maxpoints=80      # (!) keep a max of 80 pts on screen
)

# Initialize trace of streaming plot by embedding the unique stream_id
trace1 = Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream         # (!) embed stream id, 1 per trace
)

data = Data([trace1])

# Add title to layout object
layout = Layout(title='Time Series')

# Make a figure object
fig = Figure(data=data, layout=layout)

# (@) Send fig to Plotly, initialize streaming plot, open new tab
unique_url = py.plot(fig, filename='s7_first-stream')

# (@) Make instance of the Stream link object, 
#     with same stream id as Stream id object
s = py.Stream(stream_id)

# (@) Open the stream
s.open()

print(s)
print(type(s))
import sys
from threading import Event
from gattlib import GATTRequester
import time


class Requester(GATTRequester):
    def __init__(self, wakeup, pstream, *args):
        GATTRequester.__init__(self, *args)
        self.wakeup = wakeup
        self.s = pstream

    def on_notification(self, handle, data):
		#print("- notification on handle: {}\n".format(handle))
		i = 0
		for d in data:
			print(hex(ord(d)), end=' ')
		print("")

		i = 0
		axl = 0x00
		axh = 0x00
		print("1")
		for d in data:
			if i > 5 and i <= 11:
				if i == 6: # get axl and axh
					axl = int(hex(ord(d)), 16)
					print("axl: ", axl, hex(ord(d)))
				if i == 7:
					axh = int(hex(ord(d)), 16)
					print("axh: ", axh, hex(ord(d)))
					axmsb = axh << 8
					axlsb = axl
					ax = axh + axl
					print ("ax:axmsb:axlsb ", ax / (32768/2), axmsb, axlsb)
					if self.s is not None:
						print("self.s exist")
						print(self.s)
						print(type(self.s))
						item = {}
						print(item)
						item['x'] = time.time()
						item['y'] = ax
						print(item)
						self.s.append(item)
					else:
						print("self.s no exist")
			i += 1

		#self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, address, pstream):
		self.received = Event()
		self.requester = Requester(self.received, pstream, address, False, "hci1")

		self.connect()
		self.requester.write_by_handle(0x3C, str(bytearray([0xff, 0xff])))
		self.requester.write_by_handle(0x3E, str(bytearray([0x64])))
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

    print(time.time())	
    data_stream = list()
    ReceiveNotification("B0:B4:48:BF:C3:83", data_stream)
    s.close()
    print("Done.")
