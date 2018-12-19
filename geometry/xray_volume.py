
# coding: utf-8

# # Description

# ### Variables:
# 
# * coordinates of surface directly under left edge of detector = (0,0)  
# * coordinates of lower left edge of detector = (h,0)  
# * distance between lower left edge of detector and center of beam = w  
# * detector width = d  
# * detector delX and delY at 45deg = d/SQRT(2) [dd]
# * beam width = s  
# * beam angle = 45deg
# * max angle allowed into detector, past collimator = phiC  
# 
# ### Point-Slope Eqn:  
# 
# * y - y1 = m \* (x - x1)
# 
# ### X-Ray Bounding Lines:
# 
# * [SS] sample surface:
#   * y = 0
# * [MD] maximum depth:
#   * y = -maxZ
# * [RB] right beam line:
#   * y - h = 1 \* (x - (w + 0.5s))
#   * y = x - w - 0.5s + h
# * [CB] center beam line:
#   * y - h = 1 \* (x - w)
#   * y = x - w + h
# * [LB] left beam line:
#   * y - h = 1 \* (x - (w - 0.5s))
#   * y = x - w + 0.5s + h
# * [LD] left det line:
#   * y - h = -tan(45 + phiC) \* (x - 0)
#   * y = -tan(45 + phiC) \* x + h
# * [CD] center det line:
#   * y - (h + 0.5\*d/SQRT(2)) = -1 \* (x - 0.5\*d/SQRT(2))
#   * y = -x + d/SQRT(2) + h
# * [RD] right det line:
#   * y - (h + d/SQRT(2)) = -tan(45 - phiC) \* (x - d/SQRT(2))
#   * y = -tan(45 - phiC) * (x - d/SQRT(2)) + h + d/SQRT(2)
# 
# ### Area:  
# 
# * y <= SS  
# * y >= MD  
# * y >= RB  
# * y <= LB  
# * y >= LD  
# * y <= RD  

# # Imports

# In[225]:

import math
import numpy as np
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')


# # Support Functions

# In[226]:

# Create dictionary for variables

def createG(h, w, s, d, phiC, maxZ):
    g = {}
    g['h'] = h
    g['w'] = w
    g['s'] = s
    g['d'] = d
    g['dd'] = d/math.sqrt(2)
    g['phiC'] = phiC
    g['mLD'] = -math.tan(math.radians(45 + phiC))
    g['mRD'] = -math.tan(math.radians(45 - phiC))
    g['maxZ'] = maxZ
    return g


# In[227]:

# Functions return y-values for given x-values and other parameters

def ySS():
    return 0

def yMD(g):
    return -g['maxZ']

def yRB(x, g):
    # y = x - w - 0.5s + h
    return x - g['w'] - 0.5*g['s'] + g['h']

def yCB(x, g):
    # y = x - w + h
    return x - g['w'] + g['h']

def yLB(x, g):
    # y = x - w + 0.5s + h
    return x - g['w'] + 0.5*g['s'] + g['h']

def yLD(x, g):
    # y = -tan(45 + phiC) * x + h
    return (g['mLD'] * x) + g['h']

def yCD(x, g):
    # y = -x + d/SQRT(2) + h
    return -x + g['dd'] + g['h']

def yRD(x, g):
    # y = -tan(45 - phiC) * (x - d/SQRT(2)) + h + d/SQRT(2)
    return (g['mRD'] * (x - g['dd'])) + g['h'] + g['dd']


# In[228]:

# Functions return x-values for given y-values and parameters

def xRB(y, g):
    # y = x - w - 0.5s + h
    return y + g['w'] + 0.5*g['s'] - g['h']

def xCB(y, g):
    # y = x - w + h
    return y + g['w'] - g['h']

def xLD(y, g):
    # y = -tan(45 + phiC) * x + h
    return (y - g['h']) / g['mLD']

def xCD(y, g):
    # y = -x + d/SQRT(2) + h
    return -y + g['dd'] + g['h']


# In[229]:

# Function to see if a point (x,y) falls in area between lines

def inArea(x, y, g):
    if ((y <= ySS()) &
        (y >= yMD(g)) & 
        (y >= yRB(x, g)) & 
        (y <= yLB(x, g)) &
        (y >= yLD(x, g)) &
        (y <= yRD(x, g))):
        return True
    else:
        return False


# In[241]:

def findPtsInArea(g, spotSize):
    xMin = xLD(0.0, g)
    xMax = xRB(0.0, g)
    yMin = -g['maxZ']
    yMax = 0.0
    xN = int(math.ceil(abs((xMax - xMin) / spotSize)))
    yN = int(math.ceil(abs((yMax - yMin) / spotSize)))
    
    xPtsInArea = []
    yPtsInArea = []
    for i in range(0, xN):
        x = (i * spotSize) + xMin - 0.5*spotSize
        for j in range(0, yN):
            y = (j * spotSize) + yMin - 0.5*spotSize
            if inArea(x, y, g):
                xPtsInArea.append(x)
                yPtsInArea.append(y)
    return (xPtsInArea, yPtsInArea)


# In[231]:

def findTotalArea(nPts, spotSize):
    return (spotSize**2) * nPts


# # Plotting Functions

# In[232]:

def beamAreaOutline(g, xMin, xMax):
    x_pts = [xMin, xMax, xMax, xMin]
    y_pts = [yLB(xMin, g), yLB(xMax, g), yRB(xMax, g), yRB(xMin, g)]
    return (x_pts, y_pts)

def beamCenterline(g, xMin, xMax):
    x_pts = [xCB(0.0, g), xMax]
    y_pts = [0.0, yCB(xMax, g)]
    return (x_pts, y_pts)


# In[233]:

def detectorAreaOutline(g, xMin, xMax):
    x_pts = [0, xMax, xMax, g['dd']]
    y_pts = [yLD(0, g), yLD(xMax, g), yRD(xMax, g), yRD(g['dd'], g)]
    return (x_pts, y_pts)

def detectorCenterline(g, xMin, xMax):
    x_pts = [0.5*g['dd'], xCD(0.0, g)]
    y_pts = [yCD(0.5*g['dd'], g), 0.0]
    return (x_pts, y_pts)


# In[239]:

def plotGeometry(g, padding, pWidth, pts=([],[])):
    xMin = 0.0 - padding
    xMax = g['w'] + 0.5*g['s'] + padding
    xSpan = xMax - xMin
    
    yMin = -g['maxZ'] - padding
    yMax = g['h'] + g['dd'] + padding
    ySpan = yMax - yMin
    
    pHeight = pWidth * (ySpan / xSpan)
    
    x_BA, y_BA = beamAreaOutline(g, xMin, xMax)
    x_BC, y_BC = beamCenterline(g, xMin, xMax)
    x_DA, y_DA = detectorAreaOutline(g, xMin, xMax)
    x_DC, y_DC = detectorCenterline(g, xMin, xMax)
    
    fig = plt.figure(figsize=(pWidth, pHeight))
    ax = fig.add_subplot(111)
    
    rectSample = plt.Rectangle([xMin, yMin], xSpan, -yMin, facecolor='#feff86', edgecolor='#feff86')
    rectDet = plt.Rectangle([0,g['h']], 2*xMin, g['d'], angle=-45.0, facecolor='#6d6d6d', edgecolor='black')
    ax.add_patch(rectSample)
    ax.add_patch(rectDet)
    
    ax.plot(x_BA, y_BA, ls='solid', lw=1.5, c='green')
    ax.plot(x_BC, y_BC, ls='dashed', lw=1.5, c='green')
    ax.plot(x_DA, y_DA, ls='solid', lw=1.5, c='steelblue')
    ax.plot(x_DC, y_DC, ls='dashed', lw=1.5, c='steelblue')
    ax.plot([xMin, xMax], [ySS(), ySS()], ls='solid', lw=1.5, c='black')
    ax.plot([xMin, xMax], [yMD(g), yMD(g)], ls='solid', lw=1.5, c='#ff5d00')
    ax.scatter(pts[0], pts[1], c='red', zorder=50.0)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_xlim([xMin, xMax])
    ax.set_ylim([yMin, yMax])
    plt.show()


# # Main Functions

# In[242]:

def areaByZ(maxZvals, h, w, s, d, phiC):
    areaVals = []
    spotSize = 0.01
    for maxZ in maxZvals:
        g = createG(h, w, s, d, phiC, maxZ)
        xPts, yPts = findPtsInArea(g, spotSize)
        area = findTotalArea(len(xPts), spotSize)
        areaVals.append(area)
    return areaVals


# # Testing and Visualizing

# In[240]:

h = 0.25 # Default = 0.25
w = 1.1
s = 1.0 
d = 0.798
phiC = 10.0
maxZ = 0.2

g = createG(h, w, s, d, phiC, maxZ)

spotSize = 0.01
xPts, yPts = findPtsInArea(g, spotSize)
area = findTotalArea(len(xPts), spotSize)
print('Total Area: {:.2f}'.format(area))

plotGeometry(g, padding=1.0, pWidth=12.0, pts=(xPts,yPts))


# In[248]:

zStep = 0.1
maxZval = 2.0
nSteps = int(maxZval / zStep)
maxZvals = [(zStep*i + zStep) for i in range(0,nSteps)]

h1 = 0.25
h2 = 0.35

a1 = areaByZ(maxZvals, h1, w, s, d, phiC)
a2 = areaByZ(maxZvals, h2, w, s, d, phiC)

fig = plt.figure(figsize=(12.0, 6.0))
ax = fig.add_subplot(111)
ax.scatter(maxZvals, a1, label='h1')
ax.scatter(maxZvals, a2, label='h2')
plt.show()

