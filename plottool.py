#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
try:
  import serial
except:
  print("You need to install pyserial. "
       "On Debian/Ubuntu try "
       "sudo apt-get install python-serial")
  exit(1)

# make input python2 and python3 compatible
try:
  input = raw_input
except NameError:
  pass

parser = argparse.ArgumentParser(description='Process all arguments')
parser.add_argument("-p", "--port", metavar='PORT', type=str, help="Serial port (default: /dev/ttyUSB0)", default="/dev/ttyUSB0")
parser.add_argument("file", type=str, help="the HPGL-file you want to plot")
args = parser.parse_args()

if not os.path.exists(args.port):
  print("The port {} does not exist.".format(args.port))
  exit(1)

print("Using port: {}".format(args.port))
try:
  HPGLinput = open(args.file)
except:
  print("no/wrong/empty file given in argument.")
  sys.exit(128)

print("Plotting file: " + args.file)

HPGLdata = HPGLinput.read()

print("{} characters loaded".format(len(HPGLdata)))

port = serial.Serial(
    port=args.port,
    baudrate=9600,
  parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  rtscts=True,
  dsrdtr=True
)

splitted = HPGLdata.split(";")
total = len(splitted)

sys.stdout.write("starting...")
for i, command in enumerate(splitted):
  sys.stdout.write("\rsending... {percent:.1f}% done ({done}/{total})".format(percent=(i + 1) * 100.0 / total, done=i + 1, total=total))
  sys.stdout.flush()
  # ignore empty
  if not command:
    continue
  port.write(command + ";")

port.write("U F U @;")
sys.stdout.write("\n")

__author__ = 'doommaster'
