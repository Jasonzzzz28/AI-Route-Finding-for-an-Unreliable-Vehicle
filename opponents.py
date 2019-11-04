"""
File: opponents.py -- Dana Nau, Oct. 16, 2019
Some simple opponent programs for Project 2.
"""

import math
import random                 # for use in opponent0

infinity = float('inf')


def opponent1(p, z, finish, walls):
	"""
	p is the current location; z is the new velocity chosen by the user.
	finish and walls are the finish line and walls.
	If possible, find an error (q,r) that will cause a crash. Otherwise, choose
	an error (q,r) that will put the user as close to a wall as possible.
	"""
	if z == (0,0):
		# velocity is 0, so there isn't any error
		return (0,0)
	# calculate the position we'd go to if there were no error
	x = p[0] + z[0]
	y = p[1] + z[1]
	ebest = None                # best error found so far
	dbest = infinity            # min. distance to wall if we use error ebest
	for q in range(-1,2):           # i.e., q = -1, 0, 1	
		for r in range(-1,2):       # i.e., r = -1, 0, 1
			for w in walls:
				xe = x + q
				ye = y + r
				# how close will wall w be if the error is (xe,ye)?
				d = edistf_to_line((xe,ye), w, finish)
				if d < dbest:
					dbest = d
					ebest = (q,r)
	return ebest


def opponent0(p, z, finish, walls):
	"""
	p is the current location; z is the new velocity chosen by the user.
	finish and walls are the finish line and walls.
	opponent0 just chooses an error (q,r) at random.
	"""
	q = random.randint(-1,1)
	r = random.randint(-1,1)
	return (q,r)

				
				
def edistf_to_line(point, edge, f_line):
	"""
	straight-line distance from (x,y) to the line ((x1,y1),(x2,y2)).
	Return infinity if there's no way to do it without intersecting f_line
	"""
#	if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#		return 0
	(x,y) = point
	((x1,y1),(x2,y2)) = edge
	if x1 == x2:
		ds = [math.sqrt((x1-x)**2 + (yy-y)**2) \
			for yy in range(min(y1,y2),max(y1,y2)+1) \
			if not intersect([(x,y),(x1,yy)], f_line)]
	else:
		ds = [math.sqrt((xx-x)**2 + (y1-y)**2) \
			for xx in range(min(x1,x2),max(x1,x2)+1) \
			if not intersect([(x,y),(xx,y1)], f_line)]
	ds.append(infinity)
	return min(ds)


def intersect(e1,e2):
	"""Test whether edges e1 and e2 intersect"""	   
	
	# First, grab all the coordinates
	((x1a,y1a), (x1b,y1b)) = e1
	((x2a,y2a), (x2b,y2b)) = e2
	dx1 = x1a-x1b
	dy1 = y1a-y1b
	dx2 = x2a-x2b
	dy2 = y2a-y2b
	
	if (dx1 == 0) and (dx2 == 0):		# both lines vertical
		if x1a != x2a: return False
		else: 	# the lines are collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
	if (dx2 == 0):		# e2 is vertical (so m2 = infty), but e1 isn't vertical
		x = x2a
		# compute y = m1 * x + b1, but minimize roundoff error
		y = (x2a-x1a)*dy1/float(dx1) + y1a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	elif (dx1 == 0):		# e1 is vertical (so m1 = infty), but e2 isn't vertical
		x = x1a
		# compute y = m2 * x + b2, but minimize roundoff error
		y = (x1a-x2a)*dy2/float(dx2) + y2a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	else:		# neither line is vertical
		# check m1 = m2, without roundoff error:
		if dy1*dx2 == dx1*dy2:		# same slope, so either parallel or collinear
			# check b1 != b2, without roundoff error:
			if dx2*dx1*(y2a-y1a) != dy2*dx1*x2a - dy1*dx2*x1a:	# not collinear
				return False
			# collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
		# compute x = (b2-b1)/(m1-m2) but minimize roundoff error:
		x = (dx2*dx1*(y2a-y1a) - dy2*dx1*x2a + dy1*dx2*x1a)/float(dx2*dy1 - dy2*dx1)
		# compute y = m1*x + b1 but minimize roundoff error
		y = (dy2*dy1*(x2a-x1a) - dx2*dy1*y2a + dx1*dy2*y1a)/float(dy2*dx1 - dx2*dy1)
	return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 


def collinear_point_in_edge(point, edge):
	"""
	Helper function for intersect, to test whether a point is in an edge,
	assuming the point and edge are already known to be collinear.
	"""
	(x,y) = point
	((xa,ya),(xb,yb)) = edge
	# point is in edge if (i) x is between xa and xb, inclusive, and (ii) y is between
	# ya and yb, inclusive. The test of y is redundant unless the edge is vertical.
	if ((xa <= x <= xb) or (xb <= x <= xa)) and ((ya <= y <= yb) or (yb <= y <= ya)):
	   return True
	return False
		

