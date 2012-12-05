from joy import *
from delta_robot import *
import pickle
from socket import socket, AF_INET, SOCK_STREAM, error as SocketError
import threading
import time
import select
from json import loads as json_loads
import numpy
import ckbot.logical as L
import math
import transform


ZDIST = 10
MMTOIN = 0.0393701

square_list = [[[1.0, 1.0], [1.0, 5.0]],[[1.0, 5.0], [5.0, 5.0]], [[5.0, 5.0], [5.0, 1.0]], [[5.0, 1.0], [1.0, 1.0]]]

stroke_list = [ 
 [(18,10), (10,22)], [(18,35), (27,24)], [(19,10), (27,25)], [(18,35), (10,22)],
 [(29,37), (30,11)], [(42,36), (42,12)], [(29,12), (41,36)], [(14,46), (13,70)], [(31,45), (20,58)], [(22,58), (32,70)], [(45,46), (33,54)], [(38,70), (49,61)], [(34,55), (49,62)] ]



manual_mode = True

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


class robotController( Plan ):
  def __init__(self, app, *arg, **kw):

    Plan.__init__(self, app, *arg, **kw)
    self.FIRST = self.robot.at.FIRST
    self.SECOND = self.robot.at.SECOND
    self.THIRD = self.robot.at.THIRD

    
    self.FIRST.set_speed(4)
    self.SECOND.set_speed(4)
    self.THIRD.set_speed(4)

    self.FIRST.set_pos(-1300)
    self.SECOND.set_pos(-1300)
    self.THIRD.set_pos(-1300)

    self.app = app

    self.draw_square = False
    self.draw_strokes = False
    
    self.X = [0.0, 0.0, 8.0]
    self.Y = [0.0, 0.0, 8.0]
    self.Po = [0.0, 0.0, 8.0]
    self.Rot = numpy.asarray([[1.0, 0.0, 0.0],
       [0.0, 1.0, 0.0],
       [0.0, 0.0, 1.0]])


  def behavior( self ):
    while True:
      if self.draw_square:
        progress("drawing square")
        yield self.drawer(square_list)
        self.draw_square = False
      elif self.draw_strokes:
        progress("drawing strokes")
        yield self.drawer(stroke_list)
        self.draw_strokes = False
      else:
        yield
        continue
  
  def drawer( self, point_list ):
    progress("starting drawer")
    self.FIRST.set_pos(-1300)
    self.SECOND.set_pos(-1300)
    self.THIRD.set_pos(-1300)

    self.FIRST.set_pos(-1300)
    self.SECOND.set_pos(-1300)
    self.THIRD.set_pos(-1300)
    
    self.goto_xy(point_list[0][0][0], point_list[0][0][1], 5.0)


    yield self.forDuration(4)
    for pairs in point_list:
      pairs = list(pairs)
      self.x_start = pairs[0][0]
      self.y_start = pairs[0][1]
  
      self.x_end = pairs[1][0]
      self.y_end = pairs[1][1]

      if self.draw_strokes:
        self.steps_per_inch = 1.0
      else:
        self.steps_per_inch = 30.0
      self.inches = math.sqrt(math.pow(self.x_start - self.x_end, 2.0) + math.pow(self.y_start - self.y_end, 2.0))
      self.steps = int(self.steps_per_inch * self.inches)

      self.x_steps = numpy.linspace(self.x_start, self.x_end, self.steps)
      self.y_steps = numpy.linspace(self.y_start, self.y_end, self.steps)
      progress("steps made")
      progress("X: %s  Y: %s  Z: %s" % (str(self.X), str(self.Y), str(self.Po)))      

      self.FIRST.set_speed(1)
      self.SECOND.set_speed(1)
      self.THIRD.set_speed(1)
      yield self.forDuration(.1)

      self.goto_xy(self.x_steps[0], self.y_steps[0], 1.0)
      yield self.forDuration(1)
      self.goto_xy(self.x_steps[0], self.y_steps[0])

      self.FIRST.set_speed(4)
      self.SECOND.set_speed(4)
      self.THIRD.set_speed(4)
      yield self.forDuration(.5)
      
      for i in range(self.steps):
        self.goto_xy(self.x_steps[i], self.y_steps[i]) 
        yield self.forDuration(.01)
      
      

    progress("ending square drawing, entering manual mode")
    manual_mode = True
            
  def goto_xy(self, x, y, z = .15):
    self.use_rot = False
    self.test = False

    self.z = z

    if self.draw_strokes:
      x = x*MMTOIN
      y = y*MMTOIN 

    if self.use_rot:
      z = self.Po[2]
      x = x
      y = y
      x += self.Po[1]
      y += self.Po[0]

      progress("x: %s  y: %s  z: %s" % (str(x),  str(y), str(z)))
      self.points = numpy.asarray(x, y, 0)
      self.points = self.points*self.Rot

      thetas = delta_calcInverse(x, y, z)
      self.FIRST.set_pos(thetas[0] * 100)
      self.SECOND.set_pos(thetas[1] * 100)
      self.THIRD.set_pos(thetas[2] * 100)

    else:


      self.x_unit = [self.X[0]-self.Po[0],
         self.X[1]-self.Po[1],
         self.X[2]-self.Po[2]]
      
      self.x_unit = [i/5.0 for i in self.x_unit]

      self.y_unit = [self.Y[0]-self.Po[0],
         self.Y[1]-self.Po[1],
         self.Y[2]-self.Po[2]]

      self.y_unit = [j/5.0 for j in self.y_unit] 

      self.z_unit = numpy.cross(numpy.asarray(self.y_unit), numpy.asarray(self.x_unit)).tolist()


      self.x_p = x*self.x_unit[0] + y*self.y_unit[0] + self.z*self.z_unit[0] + self.Po[0]
      self.y_p = x*self.x_unit[1] + y*self.y_unit[1] + self.z*self.z_unit[1] + self.Po[1]
      self.z_p = x*self.x_unit[2] + y*self.y_unit[2] + self.z*self.z_unit[2] + self.Po[2]


      self.thetas = delta_calcInverse(self.x_p, self.y_p, self.z_p)
      self.FIRST.set_pos(self.thetas[0] * 100)
      self.SECOND.set_pos(self.thetas[1] * 100)
      self.THIRD.set_pos(self.thetas[2] * 100)

      


    # progress("1: %s 2:%s 3:%s" % (str(thetas[0]), str(thetas[1]), str(thetas[2])))


class inputListener( Plan ):
  def __init__(self, app, *arg, **kw):
    Plan.__init__(self, app, *arg, **kw)
    self.app = app


    self.sock = None
    self.peer = ("127.0.0.1", 8080)


  def _connect( self ):
    s = socket(AF_INET, SOCK_STREAM)
    try:
      s.connect( self.peer )
    except SocketError, se:
      progress("Failed to connect: "+str(se))
      return
    s.setblocking(0)
    self.sock = s

  def stop( self ):
    if self.sock is not None:
      self.sock.close()
    self.sock = None

  def behavior( self ):
    while True:
      if self.sock is None:
        self._connect()
      if self.sock is None:
        yield self.forDuration(0.1)
        continue

      try:
        msg = self.sock.recv(1024)
      except SocketError, se:
        if se.errno != 11:
          progress("Connection failed: "+str(se))
          self.sock.close()
          self.sock = None
        yield
        continue
 
      msg = json_loads(msg)

      
      assert type(msg) is list
      progress( "received message: %s" % str(msg))

      if manual_mode is False:
        progress("not in manual mode")
        yield
        continue

      positions = delta_calcInverse(msg[0], msg[1], msg[2])

      if -1 in positions:
        progress("impossible position")
        yield
        continue     

      progress("angles %s" % str(positions))

      self.robot.at.FIRST.set_pos(positions[0] * 100)
      self.robot.at.SECOND.set_pos(positions[1] * 100)
      self.robot.at.THIRD.set_pos(positions[2] * 100) 
    
      yield self.forDuration(.1)

class HelloJoyApp( JoyApp ):
  """HelloJoyApp
  
     The "hello world" of JoyApp programming.
     This JoyApp pipes the y coordinate of mouse positions (while left
     button is pressed) to a specified setter. By default this setter is
     given by "#output " -- i.e. it is a debug message. 
     
     See JoyApp.setterOf() for a specification of possible outputs
  """
  
  def __init__(self,spec,*arg,**kw):
    # This is a "constructor". It initializes the JoyApp object.
    # Because we added an additional parameter, we extend the 
    # JoyApp constructor. The first step is to call the superclass
    # constructor so that we'll have a valid JoyApp instance.
    JoyApp.__init__(self, robot = {'count':3}, *arg,**kw)
    
    # JoyApp.__init__(self, *arg,**kw)
    
    self.manual_mode = True
    self.point_mode = False

    self.collect_points = False   

    self.Po = [0.0, 0.0, 8.0]
    self.Rot = numpy.asarray([[1.0, 0.0, 0.0],
       [0.0, 1.0, 0.0],
       [0.0, 0.0, 1.0]])


    self.points = []

    # Store output specifier for later use
    self.spec = spec
    
  def onStart(self):
    # This function is called when the JoyApp is ready to start up,
    # i.e. after all PyGame devices have been activated, robot Cluster
    # is populated, scratch interface is live, etc.
    self.listener = inputListener(self, robot = self.robot)
    self.listener.start()

    self.controller = robotController(self, robot = self.robot)
    self.controller.start()

    self.output = self.setterOf(self.spec)

  def onEvent(self,evt):
    # All unknown events --> punt to superclass
    if evt.type is MIDIEVENT:

      if(self.manual_mode):
        if(evt.kind=='slider' and evt.index==1):
          self.robot.at.FIRST.set_pos((evt.value - 63.5)/127.0)
        elif(evt.kind=='slider' and evt.index==2):
          self.robot.at.SECOND.set_pos((evt.value - 63.5)/127.0)
        elif(evt.kind=='slider' and evt.index==3):
          self.robot.at.THIRD.set_pos((evt.value - 63.5)/127.0)   
   
    if evt.type is KEYDOWN and evt.key in [ord('q'), 27]:
      self.stop()

    if evt.type is KEYDOWN:
      if evt.key is ord('s'):
        self.listener.manual_mode = False
        self.controller.draw_square = True
      if evt.key is ord('d'):
        self.listener.manual_mode = False
        self.controller.draw_strokes = True
      if evt.key is ord('o'):
        self.theta_first = self.robot.at.FIRST.get_pos()/100.0
        self.theta_second = self.robot.at.SECOND.get_pos()/100.0
        self.theta_third = self.robot.at.THIRD.get_pos()/100.0
        self.Po = delta_calcForward(self.theta_first, self.theta_second, self.theta_third)
        self.controller.Po = self.Po
        progress("new origin: %s" % repr(self.Po))

      if evt.key is ord('c'):
        if(self.collect_points):
          self.collect_points = not self.collect_points
          self.points = numpy.array(self.points)
          progress("points: %s" % repr(self.points))
          latent, self.Rot, score = transform.princomp( self.points )
          progress("points collected %s" % repr(self.Rot))
          self.controller.Rot = self.Rot
          self.points = []
        else:
          self.robot.at.FIRST.go_slack()
          self.robot.at.SECOND.go_slack()
          self.robot.at.THIRD.go_slack()
          self.collect_points = True

      if evt.key is ord('x'):
        self.theta_first = self.robot.at.FIRST.get_pos()/100.0
        self.theta_second = self.robot.at.SECOND.get_pos()/100.0
        self.theta_third = self.robot.at.THIRD.get_pos()/100.0
        self.X = delta_calcForward(self.theta_first, self.theta_second, self.theta_third)
        self.controller.X = self.X
        progress("new X: %s" % repr(self.X))

      if evt.key is ord('y'):
        self.theta_first = self.robot.at.FIRST.get_pos()/100.0
        self.theta_second = self.robot.at.SECOND.get_pos()/100.0
        self.theta_third = self.robot.at.THIRD.get_pos()/100.0
        self.Y = delta_calcForward(self.theta_first, self.theta_second, self.theta_third)
        self.controller.Y = self.Y
        progress("new Y: %s" % repr(self.Y))



    if evt.type is TIMEREVENT:
      if self.collect_points:
        self.theta_first = self.robot.at.FIRST.get_pos()/100.0
        self.theta_second = self.robot.at.SECOND.get_pos()/100.0
        self.theta_third = self.robot.at.THIRD.get_pos()/100.0
        self.point = delta_calcForward(self.theta_first, self.theta_second, self.theta_third)
        if(self.point != -1):
          self.points.append( list(self.point) )
  #def behavior(self):
    
    # If we reach this line, it was a MOUSEMOTION with button pressed
    #   so we send the value out to the output
    # self.output( evt.pos[1] )
    
  
app = HelloJoyApp("#output ")
app.run()
