from __future__ import division
from gattlib import DiscoveryService
from gattlib import GATTRequester, GATTResponse
import time
from pylab import *


#line, = plot(0,0)
#time.sleep(5)
service = DiscoveryService("hci1")
devices = service.discover(2)
tag_address = "B0:B4:48:BF:C3:83"

for address, name in devices.items():
	print("name: {}, address: {}".format(name, address))
	if address == tag_address:
				
		print "cilia found"
		req = GATTRequester(tag_address, False, "hci1")
		response = GATTResponse()
		req.connect()
		req.read_by_handle_async(0x3A, response)
		while not response.received():
			time.sleep(0.1)

		steps = response.received()[0]
		#print "steps..."
		#print type(steps)
		#print steps
		#for b in steps:
		#	print hex(ord(b)),' '
		
		req.write_by_handle(0x3C, str(bytearray([0xff, 0xff])))
		req.write_by_handle(0x3E, str(bytearray([0x64])))
		data = req.read_by_handle(0x3C)[0]
		#for d in data:
		#	print hex(ord(d)),' '
		#print("")
		req.write_by_handle(0x3A, str(bytearray([0x0, 0x0])))
		for i in range(1000):
			data = req.read_by_handle(0x39)[0]
			for d in data:
				print hex(ord(d)), 
			print("")
			i = 0
			axl = 0x00
			axh = 0x00
			for d in data:
				if i > 5 and i <= 11:
					if i == 6: # get axl and axh
						axl = int(hex(ord(d)), 16)
						print "axl: ", axl, hex(ord(d))
					if i == 7:
						axh = int(hex(ord(d)), 16)
						print "axh: ", axh, hex(ord(d))
						axmsb = axh << 8
						axlsb = axl
						ax = axh + axl
						print ("ax:axmsb:axlsb ", ax / (32768/2), axmsb, axlsb)
				i += 1
			time.sleep(0.1)

