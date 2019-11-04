"""
File: env.py -- Dana Nau, Oct. 16, 2019
A simple environment for running Project 2.
"""

# system modules
import math, sys
import multiprocessing as mp
import ast                    # get ast.literal_eval

# modules provided with the project
import time

import sample_probs
import tdraw, turtle          # Code to use Python's "turtle drawing" package
import opponents as op        # File containing some simple opponent programs

# You must provide this yourself
import proj2                  # File containing your program for Project 2


def main(problem=sample_probs.rhook32b, max_search_time=5, max_init_time=5, \
         opponent=op.opponent1, verbose=1, draw=1):
    """
    First call proj2.initialize (if it exists) and wait max_init_time (default 5)
    seconds. Then repeatedly do the following steps until you win or lose:
    - Call proj2.main, and wait max_search_time (default 5) number of seconds.
    - Kill proj2.main, and read the last velocity it put into choices.txt.
    - If it isn't a legal velocity, exit with 'lose'.
    - If velocity = (0,0) and distance from finish line <= 1, exit with 'win'.
    - Call the opponent to add an error to the velocity.
    - Draw the move in the graphics window.
    - If the move crashes into a wall, exit with 'lose'. 
    """ 
    if verbose:
        print(problem)
    (title, p0, f_line, walls) = problem
    
    if draw:
        turtle.Screen()             # open the graphics window
        tdraw.draw_problem((p0, f_line, walls), title=title)
    
    (x,y) = p0
    (u,v) = (0,0)

    # If proj2 includes an initialization procedure, call it to cache some data
    if 'initialize' in dir(proj2):
        if verbose:
            print('Calling proj2.initialize.')
        p = mp.Process(target=proj2.initialize, \
            args = (((x,y),(u,v)), f_line, walls, ))
        p.start()
        # Wait for max_init_time seconds
        p.join(max_init_time)
        if p.is_alive():
            if verbose:
                print('\nWarning: terminating proj2.initialize at {} seconds.'.format(max_init_time))
                print('This means its output may be incomplete.')
        p.terminate()
    elif verbose:
        print("Note: proj2.py doesn't contain an initialize program.")

    while True:

        if goal_test((x,y), (u,v), f_line):
            if verbose:
                print('\nYou win.')
            return 'win'

        (u, v, ok) = get_proj2_choice((x,y), (u,v), f_line, walls, max_search_time)
        if ok == False:
            if verbose:
                print("\nYour program produced an incorrect move, so you lose.")
            return 'wrong move'

        if draw:
            draw_edge(((x,y), (x+u, y+v)), 'green') 
        error = opponent((x,y), (u,v), f_line, walls)
        (xnew,ynew) = (x+u+error[0], y+v+error[1])
        if verbose:
            print('proj2 velocity {}, opponent error {}, result is {}'.format( \
                (u,v), error, (xnew,ynew)))
        edge = ((x,y), (xnew, ynew))
        if draw:
            draw_edge(edge, 'red')
        #time.sleep(1.0) # my own addin
        if crash(edge, walls):
            if verbose:
                print('\nYou crashed, so you lose.')
            return 'crash'
        (x,y) = (xnew, ynew)


def get_proj2_choice(position, velocity, f_line, walls, max_search_time):
    """
    Start proj2.main as a process, wait until max_search_time and terminate it,
    then read the last choice it produced.
    """
    
    # Start proj2.main as a process
    p = mp.Process(target=proj2.main, \
        args = ((position,velocity), f_line, walls, ))
    p.start()
    # Wait for proj2.main until max_search_time
    p.join(max_search_time)
    if p.is_alive():
        print('Terminating proj.main at max_search_time = {} seconds.'.format(max_search_time))
    p.terminate()

    with open('choices.txt') as fp:
        line = None
        got_value = False
        # read and evaluate lines until we've gotten the last one
        for line in iter(fp.readline, ''):
            try:
                (u,v) = ast.literal_eval(line)  # safer than doing a full eval
                got_value = True
            except TypeError:
                print("\nIn choices.txt, this line isn't a velocity (u,v):")
                print(line)
            except ValueError:
                print("\nIn choices.txt, this line isn't a velocity (u,v):")
                print(line)
            except SyntaxError:
                print("\nIn choices.txt, this line is syntactically wrong:")
                print(line)
                print("Maybe your program ran out of time while printing it?")
            
    if got_value == False:
        print("\nError: Couldn't read (u,v). Either proj2.main produced bad output,")
        print("or it ran out of time before getting an answer. If it ran out of")
        print("time, try increasing max_search_time to more than {}.".format(max_search_time))
        return (-1, -1, False)

    return (u, v, True)


def draw_edge(edge,color):
    tdraw.draw_lines([edge], width=2, color=color,dots=6)


########################################################
# functions copied from the Project 1 racetrack.py file
########################################################

def goal_test(point,velocity,f_line):
    """Test whether state is with distance 1 of the finish line and has velocity (0,0)"""
    return velocity == (0,0) and edist_to_line(point, f_line) <= 1


def edist_to_line(point, edge):
    """
    Euclidean distance from point to edge, if edge is either vertical or horizontal.
    """
    (x,y) = point
    ((x1,y1),(x2,y2)) = edge
    if x1 == x2:
        ds = [math.sqrt((x1-x)**2 + (y3-y)**2) \
            for y3 in range(min(y1,y2),max(y1,y2)+1)]
    else:
        ds = [math.sqrt((x3-x)**2 + (y1-y)**2) \
            for x3 in range(min(x1,x2),max(x1,x2)+1)]
    return min(ds)
                

def crash(move,walls):
    """Test whether move intersects a wall in walls"""
    for wall in walls:
        if intersect(move,wall): return True
    return False


def intersect(e1,e2):
    """Test whether edges e1 and e2 intersect"""       
    
    # First, grab all the coordinates
    ((x1a,y1a), (x1b,y1b)) = e1
    ((x2a,y2a), (x2b,y2b)) = e2
    dx1 = x1a-x1b
    dy1 = y1a-y1b
    dx2 = x2a-x2b
    dy2 = y2a-y2b
    
    if (dx1 == 0) and (dx2 == 0):       # both lines vertical
        if x1a != x2a: return False
        else:   # the lines are collinear
            return collinear_point_in_edge((x1a,y1a),e2) \
                or collinear_point_in_edge((x1b,y1b),e2) \
                or collinear_point_in_edge((x2a,y2a),e1) \
                or collinear_point_in_edge((x2b,y2b),e1)
    if (dx2 == 0):      # e2 is vertical (so m2 = infty), but e1 isn't vertical
        x = x2a
        # compute y = m1 * x + b1, but minimize roundoff error
        y = (x2a-x1a)*dy1/float(dx1) + y1a
        return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
    elif (dx1 == 0):        # e1 is vertical (so m1 = infty), but e2 isn't vertical
        x = x1a
        # compute y = m2 * x + b2, but minimize roundoff error
        y = (x1a-x2a)*dy2/float(dx2) + y2a
        return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
    else:       # neither line is vertical
        # check m1 = m2, without roundoff error:
        if dy1*dx2 == dx1*dy2:      # same slope, so either parallel or collinear
            # check b1 != b2, without roundoff error:
            if dx2*dx1*(y2a-y1a) != dy2*dx1*x2a - dy1*dx2*x1a:  # not collinear
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
        

