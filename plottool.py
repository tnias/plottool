#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import os
import serial
import argparse

parser = argparse.ArgumentParser(description='Process all arguments')
parser.add_argument("-p", "--port", metavar='PORT', type=str, help="Serial port (default: /dev/ttyUSB0)", default="/dev/ttyUSB0")
parser.add_argument("file", type=str, help="the HPGL-file you want to plot")
args = parser.parse_args()

print("Unsing port: " + args.p)
try:
  HPGLinput = open(args.file,"rt")
except:
  print("no/wrong/empty file given as Argumen!")
  sys.exit(128)

print("Plotting file: " + args.file)

filelength = os.stat(args.file).st_size
print(str(filelength) + " characters loaded")
splitfile = []
fcounter = 0
buffer = ""
splitfile.append("")


for i in range(1, filelength):
  currentChar = HPGLinput.read(1)
  buffer += currentChar
  if currentChar == ";":
#    print(len(buffer))
#    print(len(splitfile[fcounter]))
    if len(buffer) + len(splitfile[fcounter]) <= 10250:
      splitfile[fcounter] += buffer
      buffer = ""
    else:
      fcounter += 1
      splitfile.append(buffer)
      buffer = ""

port = serial.Serial(
    port=args.p,
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

for i in range(0,len(splitfile)):
  port.write(splitfile[i])
  raw_input("Press Enter to continue...")

port.write("U F U @;")

__author__ = 'doommaster'
