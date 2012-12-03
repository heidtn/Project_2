from delta_robot import *

def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L


xmax = 0
ymax = 0
zmax = 0

xmin = 0
ymin = 0
zmin = 0


for x in frange(-15, 15, .1):
    if(x == 0):
        continue
    for y in frange(-15, 15, .1):
        if(y == 0):
            continue
        for z in frange(0, 15, .1):
            if(z == 0):
                continue
            status = delta_calcInverse(x, y, z)
            if(-1 in status):
                dummy = 1
            else:
                print status




