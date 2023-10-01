from time import perf_counter_ns
from collections import deque
from queue import PriorityQueue

# AI Project #1
# by Max DeJesus 

# This program implements six different search algorithms, and with a set of given files creates a map
# of local cities and adjacent citites in Kansas. The user is prompted to enter a city to depart from 
# and a city to travel to, followed by the algorithm to use to find a path. It will then search for 
# a valid path to said city, returning the path, time elapsed, and the distance traveled from node to node.
# It does not allow cities not in the database, but does account for a path not found.

# This function will doubly link any items in a dict if they are not already
def symmetrize(targetdict):
    copy = targetdict.copy()
    for k,v in targetdict.items():
        for i in v:
            if i not in copy:
                copy[i] = []
            if k not in copy[i]:
                copy[i].append(k)      
    return copy

# This function calculates a Manhattan distance based on the cities dict, used for algorithims requiring weight
def dist(a, b):
    one = cities[a]
    two = cities[b]
    out = abs(one[0] - two[0]) + abs(one[1] - two[1])
    return out

# Main run function for a given start, end, and algorithm
def run(start, end, alg):
    match alg:
        case 1:
            ts = perf_counter_ns()
            r = bruteforce(start, end)
            te = perf_counter_ns()
        case 2:
            ts = perf_counter_ns()
            r = dfs(start, end)
            te = perf_counter_ns()
        case 3:
            ts = perf_counter_ns()
            r = bfs(start, end)
            te = perf_counter_ns()
        case 4:
            ts = perf_counter_ns()
            r = bestfirst(start, end)
            te = perf_counter_ns()
        case 5:
            ts = perf_counter_ns()
            r = id_dfs(start, end)
            te = perf_counter_ns()
        case 6:
            ts = perf_counter_ns()
            r = astar(start, end)
            te = perf_counter_ns()
    if r == False:
        print('Path not found')
    else:
        print("Path from start to goal: ", r)
        print('Distance traveled:')
        distance = 0.0
        for i in range(0,len(r)-1):
            distance += dists[(r[i],r[i+1])]
        print(distance)
    print('Time elapsed:', te-ts, 'ns')
    

# Dicts for city coordinates and the adjacencies (from the files), alongside the dict for path weights
cities = {}
adj = {}
dists = {}

# Load in cities from file
cfile = open('coordinates.csv', 'r')
clines = cfile.read().splitlines()
cfile.close()

for l in clines:
    spl = l.split(',')
    cities[spl[0]] = [float(spl[1]), float(spl[2])]

# Load in adjacencies from file and symmetrize
afile = open("Adjacencies.txt",'r')
alines = afile.read().splitlines()
afile.close()
  
for l in alines:
    spl = l.split(' ')
    if spl[0] in adj:
        adj[spl[0]].append(spl[1])
    else:
        adj[spl[0]] = [spl[1]]
        
adj = symmetrize(adj)

# Compute distance weights for k/v pairs
for k, v in adj.items():
    for c in v:
        dists[(k,c)] = dist(k,c)


#
# Search algorithims
#

# Brute-force search
def bruteforce(start, end):
    global solution
    solution = []
    
    def explore(city, cs):
        currsolution = cs.copy()
        if city not in currsolution:
            currsolution.append(city)
        if end in currsolution:
            global solution
            solution = currsolution.copy()
            return
        else:
            for neighbor in adj[city]:
                if neighbor not in currsolution and end not in currsolution:
                    explore(neighbor, currsolution)
            return False
                    
    while end not in solution:
        currentSolution = [start]
        explore(start, currentSolution)
    if end in solution:
        return solution
    return False

# Depth-first search
def dfs(start, end):
    opened = deque()
    closed = deque()
    
    opened.append((start, [start]))
    
    while len(opened) != 0:
        c, p = opened.pop()
        if c == end:
            return p
        else:
            for v in reversed(adj[c]):
                if v in closed:
                    continue
                else:
                    opened.append((v, p + [v]))
            closed.append(c)
    return False

# Bretdh-first search (virtually the same as dfs, just does FIFO instead)
def bfs(start, end):
    opened = deque()
    closed = deque()
    
    opened.append((start, [start]))
    
    while len(opened) != 0:
        c, p = opened.popleft()
        if c == end:
            return p
        else:
            for v in reversed(adj[c]):
                if v in closed:
                    continue
                else:
                    opened.append((v, p + [v]))
            closed.append(c)
    return False

# Best-first search
def bestfirst(start, end):
    opened = PriorityQueue()
    closed = []
    opened.put((0,start, [start]))
    
    while opened.empty() == False:
        c = opened.get()
        if c[1] == end:
            return c[2]
        else:
            for v in reversed(adj[c[1]]):
                if v in closed:
                    continue
                else:
                    opened.put((dists[(c[1],v)], v, c[2] + [v]))
            closed.append(c[1])
    return False

# ID-DFS search
def id_dfs(start, end):
    maxdepth = 0
    
    def dfs_depth(node, end, maxdepth, c):
        closed = c.copy()
        if node == end:
            closed.append(node)
            return closed
        if maxdepth <= 0:
            return False
        
        closed.append(node)

        for city in adj[node]:
            if city not in closed:
                result = dfs_depth(city, end, maxdepth - 1, closed)
                if type(result) is list:
                    return result
        return False
    
    while True:
        c = []
        result = dfs_depth(start, end, maxdepth, c)
        if type(result) is list:
            break
        maxdepth += 1
    return result

# A* search
def astar(start, end):
    opened = PriorityQueue()
    closed = []
    opened.put((0,start, [start]))
    
    while opened.empty() == False:
        c = opened.get()
        if c[1] == end:
            return c[2]
        else:
            for v in reversed(adj[c[1]]):
                if v in closed:
                    continue
                else:
                    opened.put((c[0] + dists[(c[1],v)], v, c[2] + [v]))
            closed.append(c[1])
    return False


# Start the user interaction with program
print('Search algorithims for Kansas cities')
print('Valid cities: ')
for i in cities.keys(): print(f'{i}, ', end='')
print()

# While loop for choosing start city
valid = False
while not valid:
    city1 = input('Choose a city to depart from: ')
    if city1 not in cities.keys():
        print('Choose a valid city.')
        continue
    else:
        valid = True
    
# While loop for choosing end city    
valid = False
while not valid:
    city2 = input('Choose a city to travel to: ')
    if city2 not in cities.keys():
        print('Choose a valid city.')
        continue
    else:
        valid = True

# While loop for choosing algorithm
valid = False
while not valid:
    print("Choose a search algorithm: \n1 : Brute-force search\n2 : Depth-first search\n3 : Breadth-first search\n4 : Best-first search\n5 : ID-DFS search\n6 : A* search\n")
    alg = input('> ')
    try:
        alg = int(alg)
    except:
        print('Choose a valid algorithm')
        continue
    match alg:
        case 1:
            run(city1, city2, 1)
            valid = True
        case 2:
            run(city1, city2, 2)
            valid = True
        case 3:
            run(city1, city2, 3)
            valid = True
        case 4:
            run(city1, city2, 4)
            valid = True
        case 5:
            run(city1, city2, 5)
            valid = True
        case 6:
            run(city1, city2, 6)
            valid = True
        case _:
            print('Choose valid algorithm')
            continue
            
