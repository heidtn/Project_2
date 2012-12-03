from joy import *
from delta_robot import *
import pickle
from socket import socket, AF_INET, SOCK_STREAM, error as SocketError
import threading
import time
import select
from json import loads as json_loads

FIRST = None
SECOND = None
THIRD = None

square_list = [[[0.0, 0.0], [0.0, 4.0]],[[0.0, 4.0], [4.0, 4.0]], [[4.0, 4.0], [4.0, 0.0]], [[4.0, 0.0], [0.0, 0.0]]]

stroke_list = None

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
    self.app = app

    self.draw_square = False
    self.draw_strokes = False

  def behavior( self ):
    while True:
      if self.draw_square:
        self.square_drawer(square_list)
      else:
        yield
        continue
  
  def drawer( self, point_list ):
    for pairs in point_list:
      self.x_start = pairs[0][0]
      self.y_start = pairs[0][1]

      self.x_end = pairs[1][0]
      self.y_end = pairs[1][1]

            
  

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

      if self.manual_mode is False:
        progress("not in manual mode")
        yield
        continue

      positions = delta_calcInverse(msg[0], msg[1], msg[2])

      if -1 in positions:
        progress("impossible position")
        yield
        continue     

      progress("angles %s" % str(positions))

 
    
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
    # joyapp.__init__(self, robot = {'count':3}, *arg,**kw)
    
    JoyApp.__init__(self, *arg,**kw)
    
    self.manual_mode = True
    self.point_mode = False
    
    # Store output specifier for later use
    self.spec = spec
    
  def onStart(self):
    # This function is called when the JoyApp is ready to start up,
    # i.e. after all PyGame devices have been activated, robot Cluster
    # is populated, scratch interface is live, etc.
    self.listener = inputListener(self)
    self.listener.start()

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
   
    if evt.type is KEYDOWN and evt.ket in [ord('q'), 27]:
      self.stop()

    if evt.type is KEYDOWN:
      if evt.key is ord('s'):
        self.listener.manual_mode = False
  #def behavior(self):
    
    # If we reach this line, it was a MOUSEMOTION with button pressed
    #   so we send the value out to the output
    # self.output( evt.pos[1] )
    
  
app = HelloJoyApp("#output ")
app.run()
