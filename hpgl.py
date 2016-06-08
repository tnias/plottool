#!/usr/bin/env python
from __future__ import division
import re
import math

HPGL_GOTO = "PU%s,%s;"
HPGL_CUTTO = "PD%s,%s;"
HPGL_CUTTO_STR = "PD%s;"
HPGL_INIT = "IN:;"
HPGL_SELECT_PEN = "SP%s;"
HPGL_PEN_ABSOLUTE = "PA;"


def mm2hpgl(value):
	return value / 25.4 * 1016.0


def hpgl2mm(value):
	return round(value, 0) / 1016.0 * 25.4


def vecDot(a, b):
	return sum(map(lambda i: i[0] * i[1], zip(a, b)))


def vecLen(a):
	return math.sqrt(vecDot(a, a))


def vecAngle(a, b, c):
	v0 = (a[0] - b[0], a[1] - b[1])
	v1 = (c[0] - b[0], c[1] - b[1])
	if a == c:
		return 0
	r = vecDot(v0, v1) / (vecLen(v0) * vecLen(v1))
	if r >= -1 and r <= 1:
		return math.acos(r)
	return math.pi


def vecDist(a, b):
	return vecLen((a[0] - b[0], a[1] - b[1]))


def vecExtend(a, b, x):
	return a[0] + x * (b[0] - a[0]), a[1] + x * (b[1] - a[1])


def hpgl_goto(match):
	x = int(match.group(1))
	y = int(match.group(2))
	return HPGL_GOTO, (x, y)


def hpgl_pen_up(match):
	x = None
	y = None
	return HPGL_GOTO, (x, y)


def hpgl_cutto(match):
	x = int(match.group(1))
	y = int(match.group(2))
	return HPGL_CUTTO, (x, y)


def hpgl_cutto2(match):
	coords = map(int, match.groups()[0].split(","))
	xy = zip(coords[0::2], coords[1::2])
	return HPGL_CUTTO, xy


def hpgl_init(match):
	return HPGL_INIT, None

def hpgl_pen_absolute(match):
	return HPGL_PEN_ABSOLUTE, None

def hpgl_select_pen(match):
	pen = int(match.group(1))
	return HPGL_SELECT_PEN, (pen,)


def path_start_stop(path):
	start = path[0]
	stop = path[-1]
	return start, stop


def path_center(path):
	xvals, yvals = zip(*path)
	max_x = max(xvals)
	max_y = max(yvals)
	min_x = min(xvals)
	min_y = min(yvals)

	start = (min_x + (max_x - min_x) / 2, min_y + (max_y - min_y) / 2)
	return start, start


def path_median(path):
	xvals, yvals = zip(*path)
	min_x = min(xvals)
	min_y = min(yvals)
	xvals = map(lambda x: x - min_x, xvals)
	yvals = map(lambda y: y - min_y, yvals)
	xmedian = sorted(xvals)[int(math.ceil(len(xvals) // 2))]
	ymedian = sorted(yvals)[int(math.ceil(len(yvals) // 2))]

	start = (min_x + xmedian, min_y + ymedian)
	return start, start


def path_mean(path):
	xvals, yvals = zip(*path)
	min_x = min(xvals)
	min_y = min(yvals)
	xvals = map(lambda x: x - min_x, xvals)
	yvals = map(lambda y: y - min_y, yvals)
	xmean = sum(xvals) / len(xvals)
	ymean = sum(yvals) / len(yvals)

	start = (min_x + xmean, min_y + ymean)
	return start, start


HPGL_CMDS = {
	re.compile(r"^PU(-?\d+),(-?\d+)$"): hpgl_goto,
	re.compile(r"^PD(-?\d+),(-?\d+)$"): hpgl_cutto,
	re.compile(r"^PD((-?\d+,-?\d+,)+(-?\d+),(-?\d+))$"): hpgl_cutto2,
	re.compile(r"^PA$"): hpgl_pen_absolute,
	re.compile(r"^PU$"): hpgl_pen_up,
	re.compile(r"^IN:?$"): hpgl_init,
	re.compile(r"^SP(\d+)$"): hpgl_select_pen}


class HPGL:
	def __init__(self, fn):
		self.routes = []
		if fn:
			self.parse(open(fn).read())

	def parse(self, hpgldata):
		commands = hpgldata.split(";")
		routes = []
		path = []
		for command in commands:
			command = command.strip()
			if not command:
				continue
			matched = False
			for CMD, func in HPGL_CMDS.items():
				match = CMD.match(command)
				if match:
					cmd, params = func(match)
					if cmd == HPGL_INIT:
						pass
					elif cmd == HPGL_SELECT_PEN:
						pass
					elif cmd == HPGL_PEN_ABSOLUTE:
						pass
					elif cmd == HPGL_GOTO:
						if path:
							if len(path) > 1:
								routes.append(path)
						path = [params, ]
					elif cmd == HPGL_CUTTO:
						if isinstance(params, list):
							path.extend(params)
						else:
							if path[-1] != params:
								path.append(params)
					else:
						raise Exception("what to do with \"" + cmd + "\" ?")

					matched = True
					break
			if not matched:
				print(repr(command))
		if path:
			if len(path) > 1:
				routes.append(path)
		self.routes = routes

	def getPaths(self):
		return self.routes

	def getBoundingBox(self):
		max_x = None
		max_y = None
		min_x = None
		min_y = None
		for path in self.getPaths():
			for x, y in path:
				if max_x is None or x > max_x:
					max_x = x
				if min_x is None or x < min_x:
					min_x = x

				if max_y is None or y > max_y:
					max_y = y
				if min_y is None or y < min_y:
					min_y = y

		return ((min_x, min_y), (max_x, max_y))

	def bladeOffset(self, offset):
		hpgl_offset = mm2hpgl(offset)

		def _blade_offset(path):
			new_path = []
			new_path.append(path[0])
			for prev, cur, next in zip(path[:-2], path[1:-1], path[2:]):
				print(prev,cur,next)
				angle = vecAngle(prev, cur, next)
				if angle < math.pi / 1.1:
					d2 = vecDist(cur, next)
					ext2 = (4 * hpgl_offset) / d2
					if ext2 <= 1.0:
						d1 = vecDist(prev, cur)
						ext1 = 1 + hpgl_offset / d1
						new_path.append(vecExtend(prev, cur, ext1))
						new_path.append(vecExtend(cur, next, ext2))
					else:
						new_path.append(cur)
				else:
					new_path.append(cur)
			d = vecDist(path[-2], path[-1])
			new_path.append(path[-1])
			return new_path
		self.operate(_blade_offset)

	def optimize(self):
		"""Removes points with the same coordinate and unecesary points on a straight line"""
		def _optimize(path):
			new_path = []
			last = None
			for p in path:
				if p == last:
					continue
				last = p
				new_path.append((int(round(p[0], 0)), int(round(p[1], 0))))
			path = new_path
			new_path = []
			new_path.append(path[0])
			prev = new_path[0]
			for cur, next in zip(path[1:-1], path[2:]):
				if cur == prev:
					continue
				if cur == next:
					continue
				angle = vecAngle(prev, cur, next)
				if angle == math.pi:
					continue
				new_path.append(cur)
				prev = cur
			if new_path[-1] != path[-1]:
				new_path.append(path[-1])
			if len(new_path) == 1:
				return None
			if new_path[0] == new_path[-1]:
				angle = vecAngle(new_path[-2], new_path[0], new_path[1])
				if angle == math.pi:
					new_path.pop(0)
					new_path.pop(-1)
					new_path.append(new_path[0])
			return new_path

		last = None
		paths = self.getPaths()
		self.routes = []
		for path in paths:
			if path[0] == last:
				self.routes[-1].extend(path)
			else:
				self.routes.append(path)
			last = path[-1]
		self.operate(_optimize)

	def optimizeCut(self, offset):
		hpgl_offset = mm2hpgl(offset) * 2
		operations = []

		def _optimizeCut(path):
			if path[0] != path[-1]:
				return path
			index = None
			maxlen = None
			for j, coord in enumerate(zip(path[:-1], path[1:])):
				cur, next = coord
				l = vecDist(cur, next)
				if maxlen is None or maxlen < l:
					maxlen = l
					index = j
			a = vecExtend(path[index], path[index + 1], 0.5)
			d = vecDist(path[index], path[index + 1])
			b = vecExtend(path[index + 1], path[index], 0.5 - min(hpgl_offset / d, 0.5))
			pre = [a, b]
			if path[index + 1] == b:
				pre = [a]
			p = pre + path[index + 1:] + path[1:index + 1] + [a, b]
			return p

		self.operate(_optimizeCut)

	def operate(self, fn):
		routes = []
		for path in self.routes:
			result = fn(path)
			if result:
				routes.append(result)
		self.routes = routes

	def operateXY(self, fn):
		self.operate(lambda path: map(lambda xy: fn(xy[0], xy[1]), path))

	def move(self, xoffset, yoffset):
		self.operateXY(lambda x, y: (x + xoffset, y + yoffset))

	def scale(self, xfactor, yfactor=None):
		if yfactor is None:
			yfactor = xfactor
		self.operateXY(lambda x, y: (x * xfactor, y * yfactor))

	def fit(self):
		min_xy, max_xy = self.getBoundingBox()
		x, y = min_xy
		self.move(-x, -y)

	def scaleToWidth(self, width):
		new_width = mm2hpgl(width)

		self.fit()
		_, max_xy = self.getBoundingBox()
		x, y = max_xy
		factor = new_width / float(x)
		self.scale(factor)

	def exportSVG(self, filename):
		_, max_xy = self.getBoundingBox()
		x, y = max_xy
		svg = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
	xmlns:dc="http://purl.org/dc/elements/1.1/"
	xmlns:cc="http://creativecommons.org/ns#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
	xmlns:svg="http://www.w3.org/2000/svg"
	xmlns="http://www.w3.org/2000/svg"
	units="mm"
	width="{width:.3f}mm"
	height="{height:.3f}mm"
	viewBox="0 0 {width:.3f} {height:.3f}">
""".format(width=hpgl2mm(x), height=hpgl2mm(y))
		last_x = 0
		last_y = 0
		for path in self.getPaths():
			svg += "<path style=\"stroke:#0000ff;stroke-opacity:.8;fill:none;stroke-width:0.1;\" d=\"M %.3f,%.3f L %.3f,%.3f\"></path>\n" % tuple(map(hpgl2mm, (last_x, last_y, path[0][0], path[0][1])))
			last_x = path[-1][0]
			last_y = path[-1][1]
			svg += "<path style=\"stroke:#ff0000;stroke-opacity:.8;fill:none;stroke-width:0.1;\" d=\""
			first = True
			for x, y in path:
				if first:
					first = False
					svg += "M %.3f,%.3f" % (hpgl2mm(x), hpgl2mm(y))
				else:
					svg += " L %.3f,%.3f" % (hpgl2mm(x), hpgl2mm(y))

			svg += "\"></path>\n"
		svg += "<path style=\"stroke:#0000ff;stroke-opacity:.8;fill:none;stroke-width:0.1;\" d=\"M %.3f,%.3f L %.3f,%.3f\"></path>\n" % tuple(map(hpgl2mm, (last_x, last_y, 0, 0)))
		svg += "</svg>"
		open(filename, "w").write(svg)

	def mirrorX(self):
		min_xy, max_xy = self.getBoundingBox()
		self.scale(-1, 1)
		self.move(max_xy[0], 0)

	def mirrorY(self):
		min_xy, max_xy = self.getBoundingBox()
		self.scale(1, -1)
		self.move(0, max_xy[1])

	def addMargin(self, x, y):
		self.move(mm2hpgl(x), mm2hpgl(y))

	def getSize(self):
		_, max_xy = self.getBoundingBox()
		return map(hpgl2mm, max_xy)

	def getLength(self):
		movement = 0
		draw = 0
		last = (0, 0)
		for path in self.getPaths():
			movement += vecDist(last, path[0])
			draw += sum(map(lambda x: vecDist(x[0], x[1]), zip(path, path[1:])))
			last = path[-1]
		movement += vecDist(last, (0, 0))
		return hpgl2mm(movement), hpgl2mm(draw)

	def multiplyX(self, delta, m=2):
		if m < 2:
			return
		deltaHPGL = mm2hpgl(delta)
		original = self.getPaths()
		min_xy, max_xy = self.getBoundingBox()
		x, y = max_xy
		for i in range(m - 1):
			self.move(x + deltaHPGL, 0)
			self.routes = original + self.routes
			

	def multiplyY(self, delta, m=2):
		if m < 2:
			return
		deltaHPGL = mm2hpgl(delta)
		original = self.getPaths()
		min_xy, max_xy = self.getBoundingBox()
		x, y = max_xy
		for i in range(m - 1):
			self.move(0, y + deltaHPGL)
			self.routes = original + self.routes

	def getHPGL(self):
		hpgl = HPGL_INIT
		hpgl += HPGL_PEN_ABSOLUTE
		for route in self.routes:
			first = True
			route = map(lambda a: tuple(map(lambda b: int(round(b, 0)), a)), route)
			goto = route[0]
			route = ",".join(map(lambda a: "%d,%d" % a, route[1:]))
			hpgl += HPGL_GOTO % goto
			hpgl += HPGL_CUTTO_STR % route
			continue
			exit()
			for x, y in route:
				x = int(round(x, 0))
				y = int(round(y, 0))
				if first:
					first = False
					hpgl += HPGL_GOTO % (x, y)
				else:
					hpgl += HPGL_CUTTO % (x, y)
		hpgl += HPGL_GOTO % (0, 0)
		hpgl += HPGL_SELECT_PEN % 0
		hpgl += HPGL_SELECT_PEN % 0
		return hpgl

	def exportHPGL(self, filename):
		open(filename, "w").write(self.getHPGL())

	def rerouteNearest(self, xweight=1, yweight=2, pathfn=path_center):
		last_p = (0, 0)
		paths = self.getPaths()
		self.routes = []
		distance = None
		next_path = None
		next_path_stop = None
		while paths:
			for path in paths:
				path_start, path_stop = pathfn(path)
				d = math. sqrt(((path_start[0] - last_p[0]) * xweight) ** 2 + ((path_start[1] - last_p[1]) * yweight) ** 2)
				if distance is None or distance > d:
					distance = d
					next_path = path
					next_path_stop = path_stop
			if next_path:
				self.routes.append(next_path)
				paths.remove(next_path)
				last_p = next_path_stop
				next_path = None
				distance = None

	def rerouteXY(self, rowsize=600, pathfn=path_start_stop):
		min_xy, max_xy = self.getBoundingBox()
		x, y = max_xy
		_, min_y = min_xy
		rows = [[] for i in xrange(int((y - min_y) // rowsize + 1))]
		for path in self.getPaths():
			start, stop = pathfn(path)
			x, y = start
			row = int((y - min_y) // rowsize)
			rows[row].append((start, path))
		reverse = False
		self.routes = []

		for row in rows:
			if row:
				self.routes.extend(map(lambda a: a[1], sorted(row, reverse=reverse)))
				reverse = not reverse


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser("HPGL modification/optimization tool")
	parser.add_argument("file", type=str, help="the HPGL-file to edit")
	parser.add_argument("-p", "--preview", type=str, help="Generate SVG preview file", metavar="SVG")
	parser.add_argument("-o", "--output", type=str, help="Output HPGL file", metavar="HPGL")
	args = parser.parse_args()

	hpgl = HPGL(args.file)

	if args.preview is not None:
		hpgl.exportSVG(args.preview)
	if args.output is not None:
		hpgl.exportHPGL(args.output)
