#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import os
import serial

try:
  print sys.argv[1]
  HPGLinput = open(sys.argv[1],"rt")
except:
  print("no/wrong/empty file given as Argumen!")
  sys.exit(128)

filelength = os.stat(sys.argv[1]).st_size
print(str(filelength) + " characters loaded")
splitfile = []
fcounter = 0
buffer = ""
splitfile.append("")


for i in range(1, int(filelength)):
  currentChar = HPGLinput.read(1)
  buffer += currentChar
  if currentChar == ";":
#    print(len(buffer))
#    print(len(splitfile[fcounter]))
    if len(buffer) + len(splitfile[fcounter]) <= 1025:
      splitfile[fcounter] += buffer
      buffer = ""
    else:
      fcounter += 1
      splitfile.append(buffer)
      buffer = ""

try:
  port = serial.Serial(sys.argv[2], 9200)
except:
  print("no propper port given or rights missing")
  sys.exit(128)

for i in range(0,len(splitfile)):
  port.write(splitfile[i])
  raw_input("Press Enter to continue...")

__author__ = 'doommaster'
