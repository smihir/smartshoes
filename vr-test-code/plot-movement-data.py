#!/usr/bin/python -u
# -*- mode: python; coding: utf-8 -*-

# Copyright (C) 2014, Oscar Acena <oscaracena@gmail.com>
# This software is under the terms of Apache License v2 or later.

from __future__ import print_function, division
import sys
from threading import Event
from gattlib import GATTRequester
import time
from pylab import *
import numpy as np

dev = "hci0"
ion()

class Requester(GATTRequester):
    def __init__(self, wakeup, pstream, tstream, *args):
        GATTRequester.__init__(self, *args)
        self.wakeup = wakeup
        self.s = pstream
        self.t = tstream
        self.count = 0

    def on_notification(self, handle, data):
        i = 0
        data2 = data[3:]

        axl = int(hex(ord(data2[6])), 16)
        axh = int(hex(ord(data2[7])), 16)
        axmsb = axh << 8
        axlsb = axl
        ax = axmsb + axlsb
        if ax >= 32768:
            ax -= 65536
        ax = ax / 4096

        ayl = int(hex(ord(data2[8])), 16)
        ayh = int(hex(ord(data2[9])), 16)
        aymsb = ayh << 8
        aylsb = ayl
        ay = aymsb + aylsb
        if ay >= 32768:
            ay -= 65536
        ay = ay / 4096

        azl = int(hex(ord(data2[10])), 16)
        azh = int(hex(ord(data2[11])), 16)
        azmsb = azh << 8
        azlsb = azl
        az = azmsb + azlsb
        if az >= 32768:
            az -= 65536
        az = az / 4096

        self.s['acc-x'].pop(0)
        self.s['acc-x'].append(ax)

        self.s['acc-y'].pop(0)
        self.s['acc-y'].append(ay)

        self.s['acc-z'].pop(0)
        self.s['acc-z'].append(az)

        self.wakeup.set()


class ReceiveNotification(object):
    def __init__(self, address, pstream, tstream):
        self.data = pstream
        self.time = tstream
        self.First = True
        self.received = Event()
        self.requester = Requester(self.received, pstream, tstream, address, False, dev)

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
        while True:
            self.received.wait()
            if (self.First):
                self.time = range(len(self.data['acc-x']))
                subplot(3, 1, 1)
                line_acc_x, = plot(np.asarray(self.time), np.asarray(self.data['acc-x']))
                ylim((-2, 2))

                subplot(3, 1, 2)
                line_acc_y, = plot(np.asarray(self.time), np.asarray(self.data['acc-y']))
                ylim((-2, 2))


                subplot(3, 1, 3)
                line_acc_z, = plot(np.asarray(self.time), np.asarray(self.data['acc-z']))
                ylim((-2, 2))

                draw()
                self.First = False
            else:
                line_acc_x.set_ydata(np.asarray(self.data['acc-x']))
                line_acc_x.set_xdata(np.asarray(self.time))

                line_acc_y.set_ydata(np.asarray(self.data['acc-y']))
                line_acc_y.set_xdata(np.asarray(self.time))

                line_acc_z.set_ydata(np.asarray(self.data['acc-z']))
                line_acc_z.set_xdata(np.asarray(self.time))
                draw()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <dev>".format(sys.argv[0]))
        sys.exit(1)

    dev = sys.argv[1]
    data_stream = dict()
    data_stream['acc-x'] = [0] * 100;
    data_stream['acc-y'] = [0] * 100;
    data_stream['acc-z'] = [0] * 100;
    time_stream = range(100)

    ReceiveNotification("B0:B4:48:BF:C3:83", data_stream, time_stream)
    time.sleep(20)
    print("Done.")
