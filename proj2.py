"""
I pledge on my honor that I have not given or received
any unauthorized assistance on this project.
Siyuan Zhang UID 115299634
Project 2 CMSC421

This file contains a function "main" that runs a limited depth alpha beta game-tree search
to produce the best choice for velocity.
The function takes three arguments: state, fline, walls.
   - state is the current state. It should have the form ((x,y), (u,v)), where
      (x,y) is the current location and (u,v) is the current velocity.
   - fline is the finish line. It should have the form ((x1,y1), (x2,y2)),
      where (x1,y1) and (x2,y2) are the two endpoints, and it should be either
      either vertical (x1 == x2) or horizontal (y1 == y2).
   - walls is a list of walls, each wall having the form ((x1,y1), (x2,y2))

"""
import racetrack_example as racetrack
import math
import sys
import json
from collections import deque

# global variables
infinity = float('inf')
negainfinity = float('-inf')
g_fline = False
g_walls = False
grid = []
global xm, ym  # max x and max y


def main(state, finish, walls):
    """
    main will use a limited depth alpha beta game-tree search with cycle dectection
    to produce the best choice for the current state.

    :param: state, fline, walls
    :return: print choice of velocity to file
    """
    ((x, y), (u, v)) = state

    # Retrieve the grid data that the "initialize" function stored in data.txt
    data_file = open('data.txt', 'r')
    grid = json.load(data_file)
    data_file.close()

    choices_file = open('choices.txt', 'w')

    # read the frontier for cycle checking
    data2 = open('data2.txt', 'r')
    frontier = json.load(data2)
    data2.close()

    n2fline = nearfl(finish)  # compute the near fline points
    nfline = listfl(finish)  # compute the on fline points
    res = (u, v)
    cost = infinity
    global xm, ym
    xm = max([max(x, x0) for ((x, y), (x0, y0)) in walls])
    ym = max([max(y, y0) for ((x, y), (x0, y0)) in walls])

    # loop through all the possible velocity options and call alpha beta
    # game-tree search on its resulting states, and pick the best choice(smallest cost)
    for m in range(u - 2, u + 3):
        for n in range(v - 2, v + 3):
            ns = ((x + m, y + n), (m, n))
            value = LDabSearch(ns, finish, walls, 1, negainfinity, infinity, True)
            if value < cost:
                (px, py) = oppChoice(ns, finish, walls, n2fline)  # compute opponent's choice
                # check if the opponent's choice can result in a crash and check for
                # visiting repeating states
                if not oppcrashcheck((x, y), (x + m, y + n), walls, n2fline) \
                        and not [[x + m, y + n], [m, n]] in frontier:
                    # if next state is near fline, then update
                    if (x + m, y + n) in nfline:
                        cost = value
                        res = (m, n)
                    # more detailed cycle checking if not near fline
                    elif not [px, py] in frontier and not [x + m, y + n, 0] in frontier:
                        cost = value
                        res = (m, n)

    cyclecheck = open('data2.txt', 'w')
    (i, j) = res
    k = (x, y)
    newstate = ((x + i, y + j), res)

    # add states to frontier
    if not [x, y] in frontier:
        frontier.append((x, y))
    if not [x + i, y + j, 0] in frontier:
        frontier.append((x + i, y + j, 0))
    if not [[x + i, y + j], [i, j]] in frontier:
        frontier.append(newstate)
    json.dump(frontier, cyclecheck)
    cyclecheck.close()

    print(res, file=choices_file, flush=True)


def oppcrashcheck(prev, state, walls, n2finish):
    """
    oppcrashcheck will take into account of the error and check if with the error the path from
    previous state to current state crashes.

    :param: prev, state, walls, n2finish: near fline points
    :return: if path from prev to current state crashes.
    """
    (x1, y1) = prev
    (x2, y2) = state
    # check if it's near fline and its velocity if (0, 0)
    if state in n2finish and prev == state:
        return False
    for i in range(x2 - 1, x2 + 2):
        for j in range(y2 - 1, y2 + 2):
            # check if it crashes
            if racetrack.crash([(x1, y1), (i, j)], walls):
                return True
    return False


def oppChoice(state, fline, walls, n2finish):
    """
     oppChoice will give the opponent's choice after the state

     :param: state, fline, walls, n2finish: near fline points
     :return: the choice of the opponent
     """
    ((x, y), (u, v)) = state
    # check if it's near fline and its velocity if (0, 0)
    if (x, y) in n2finish and u == 0 and v == 0:
        return state
    cx = x
    cy = y
    cost = negainfinity
    # finds the state with the largest cost
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            newS = ((i, j), (u, v))
            nc = h_opp(newS, fline, walls)
            if nc > cost:
                cost = nc
                cx = i
                cy = j
    return cx, cy


def LDabSearch(state, fline, walls, d, a, b, mx):
    """
     LDabSearch is the python version of limited-depth alpha beta game-tree search

     :param: state, fline, walls, d: depth, a: alpha, b: beta, mx: max or min's turn
     :return: the cost of the state
     """
    ((x, y), (u, v)) = state
    if x < 0 or x > xm or y < 0 or y > ym: return infinity  # check if it exceeds the race space
    if d == 0:
        return h_opp(state, fline, walls)
    if h_opp(state, fline, walls) == negainfinity:
        return negainfinity

    # max's turn is the opponent's since the opp is trying to maximize the cost
    if mx:
        if u == 0 and v == 0:
            return h_opp(state, fline, walls)
        cost = negainfinity
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                newS = ((i, j), (u, v))
                cost = max(cost, LDabSearch(newS, fline, walls, d - 1, a, b, False))
                if cost >= b:
                    return cost
                else:
                    a = max(a, cost)
        return cost
    # min's turn is the player's turn since it's trying to minimize the cost
    else:
        cost = infinity
        for m in range(u - 2, u + 3):
            for n in range(v - 2, v + 3):
                news = ((x + m, y + n), (m, n))
                cost = min(cost, LDabSearch(news, fline, walls, d - 1, a, b, True))
                if cost <= a:
                    return cost
                else:
                    b = min(b, cost)
        return cost


def initialize(state, fline, walls):
    """
        Call bfs to initialize the grid for h_opp, then write the data, in
        json format, to the file "data.txt" so it won't be lost when the process exits

        :param: state, fline, walls
        :return: none (set up the grid and cycle detection)
        """
    # use bfs to set up the grid and write it to data
    bfs(fline, walls)
    data_file = open('data.txt', 'w')
    json.dump(grid, data_file)
    data_file.close()

    # set up data2 for cycle checking
    d2 = open('data2.txt', 'w')
    f = []
    json.dump(f, d2)
    d2.close()


def bfs(fline, walls):
    """
        Use a breath-first-search from the fline to compute costs for points on the grid
        (combine edistw_to_finish and edist_grid into one time traversal of the nodes;
        significantly reduce the runtime)
        :param: fline, walls
        :return: return the grid
        """
    global grid, g_fline, g_walls, xmax, ymax
    xmax = max([max(x, x0) for ((x, y), (x0, y0)) in walls])
    ymax = max([max(y, y0) for ((x, y), (x0, y0)) in walls])
    grid = [[infinity for i in range(ymax + 1)] for j in range(xmax + 1)]
    ((x1, y1), (x2, y2)) = fline
    frontier = deque([])
    visited = []

    # set the points on fline as 0 in the grid
    # and put all neighbors of the fline in the frontier
    if x1 == x2:
        for y3 in range(min(y1, y2), max(y1, y2) + 1):
            grid[x1][y3] = 0
            visited.append((x1, y3))

        for y3 in range(min(y1, y2), max(y1, y2) + 1):
            for n in range(max(0, y3 - 1), min(ymax + 1, y3 + 2)):
                for m in range(max(0, x1 - 1), min(xmax + 1, x1 + 2)):
                    if frontier.count((m, n)) == 0 and grid[m][n] == infinity:
                        frontier.append((m, n))
    else:
        for x3 in range(min(x1, x2), max(x1, x2) + 1):
            grid[x3][y1] = 0
            visited.append((x3, y1))

        for x3 in range(min(x1, x2), max(x1, x2) + 1):
            for n in range(max(0, y1 - 1), min(ymax + 1, y1 + 2)):
                for m in range(max(0, x3 - 1), min(xmax + 1, x3 + 2)):
                    if frontier.count((m, n)) == 0 and grid[m][n] == infinity:
                        frontier.append((m, n))

    # use breath-first-search to compute the costs in the grid
    while frontier:
        (v1, v2) = frontier.popleft()
        visited.append((v1, v2))
        grid[v1][v2] = edistw_to_finish((v1, v2), fline, walls)

        # check if edistw_to_finish is able to compute the cost
        # if not, compute the cost using its non-infinity neighbors
        if grid[v1][v2] == infinity:

            for g in range(max(0, v1 - 1), min(xmax + 1, v1 + 2)):
                for h in range(max(0, v2 - 1), min(ymax + 1, v2 + 2)):
                    if grid[g][h] != infinity and not racetrack.crash(((v1, v2), (g, h)), walls):
                        if g == v1 or h == v2:
                            d = grid[g][h] + 1
                        else:

                            d = grid[g][h] + 1.4142135623730951
                        if d < grid[v1][v2]:
                            grid[v1][v2] = d

        if grid[v1][v2] != infinity:
            for i in range(max(0, v1 - 1), min(xmax + 1, v1 + 2)):
                for j in range(max(0, v2 - 1), min(ymax + 1, v2 + 2)):
                    if frontier.count((i, j)) == 0 and visited.count((i, j)) == 0:  ##and grid[i][j] == infinity:
                        frontier.append((i, j))

    g_fline = fline
    g_walls = walls
    return grid


def edistw_to_finish(point, fline, walls):
    """
        The function from h_walldist:
        straight-line distance from (x,y) to the finish line ((x1,y1),(x2,y2)).
        Return infinity if there's no way to do it without intersecting a wall
        :param a: point, fline, walls
        :return: straight-line distance from point to finish line (considering walls)
        """

    (x, y) = point
    ((x1, y1), (x2, y2)) = fline
    # make a list of distances to each reachable point in fline
    if x1 == x2:  # fline is vertical, so iterate over y
        ds = [math.sqrt((x1 - x) ** 2 + (y3 - y) ** 2) \
              for y3 in range(min(y1, y2), max(y1, y2) + 1) \
              if not racetrack.crash(((x, y), (x1, y3)), walls)]
    else:  # fline is horizontal, so iterate over x
        ds = [math.sqrt((x3 - x) ** 2 + (y1 - y) ** 2) \
              for x3 in range(min(x1, x2), max(x1, x2) + 1) \
              if not racetrack.crash(((x, y), (x3, y1)), walls)]
    ds.append(infinity)  # for the case where ds is empty
    return min(ds)


def h_opp(state, fline, walls):
    """
    The first time this function is called, it will use optimized breath first search to find the cost for all the
    points on the grid.
    On all subsequent calls, this function will retrieve the cached value and add an
    estimate of how long it will take to stop.
    :param a: state, fline, walls
    :return: estimate cost of the step
    """
    global g_fline, g_walls

    if fline != g_fline or walls != g_walls or grid == []:
        bfs(fline, walls)
    ((x, y), (u, v)) = state
    if x > xm or x < 0 or y > ym or y < 0: return infinity  # add on
    ((h1, w1), (h2, w2)) = fline
    li = listfl(fline)
    hval = float(grid[x][y])

    au = abs(u)
    av = abs(v)
    sdu = au * (au - 1) / 2.0
    sdv = av * (av - 1) / 2.0
    sd = max(sdu, sdv)

    if u < 0: sdu = -sdu
    if v < 0: sdv = -sdv
    sx = x + sdu
    sy = y + sdv

    # check if it has already found a solution path
    # if yes, stop exploring other nodes
    if li.count((x, y)) > 0 and u == 0 and v == 0:
        return negainfinity

    # add a small penalty to favor short stopping distances
    penalty = sd

    # compute location after stop, and add a penalty if it goes through a wall
    if racetrack.crash([(x, y), (sx, sy)], walls):
        penalty += 1.1 * math.sqrt(au ** 2 + av ** 2)
    else:
        penalty -= sd / 10.0

    # compute the slowest stopping distance
    if au % 2 == 0:
        ssu = (au - 2) * au / 4
    else:
        ssu = (au - 1) * au / 4
    if av % 2 == 0:
        ssv = (av - 2) * av / 4
    else:
        ssv = (av - 1) * av / 4
    if u < 0: ssu = -ssu
    if v < 0: ssv = -ssv
    ssx = x + int(ssu)
    ssy = y + int(ssv)

    if not racetrack.crash([(x, y), (ssx, ssy)], walls):
        # check if the slowest stop point land on the fline
        # if yes, significantly reduce the return cost
        if (ssx, ssy) in li:
            penalty -= sd / 4.0
        # check if the slowest stopping x or y point is on the fline and reduce the return cost
        elif li.count((h1, ssy)) > 0 or li.count((h2, ssy)) > 0 or li.count((ssx, w1)) > 0 or li.count((ssx, w2)) > 0:
            penalty -= sd / 10.0

    hval += penalty

    return hval


def nearfl(a):
    """
        This helper function finds near the nodes on fline
        :param a: fline
        :return: list of nodes close to fline
        """
    ((x1, y1), (x2, y2)) = a
    res = []
    if x1 == x2:
        for y3 in range(min(y1, y2) - 2, max(y1, y2) + 3):
            res.append((x1, y3))
            res.append((x1 - 1, y3))
            res.append((x1 + 1, y3))
            res.append((x1 - 2, y3))
            res.append((x1 + 2, y3))

    else:
        for x3 in range(min(x1, x2) - 2, max(x1, x2) + 3):
            res.append((x3, y1))
            res.append((x3, y1 - 1))
            res.append((x3, y1 + 1))
            res.append((x3, y1 - 2))
            res.append((x3, y1 + 2))

    return res


def listfl(a):
    """
        This helper function finds all the nodes on fline
        :param a: fline
        :return: list of nodes on fline
        """
    ((x1, y1), (x2, y2)) = a
    res = []
    if x1 == x2:
        for y3 in range(min(y1, y2) - 1, max(y1, y2) + 2):
            res.append((x1, y3))
            res.append((x1 - 1, y3))
            res.append((x1 + 1, y3))

    else:
        for x3 in range(min(x1, x2) - 1, max(x1, x2) + 2):
            res.append((x3, y1))
            res.append((x3, y1 - 1))
            res.append((x3, y1 + 1))
    return res
