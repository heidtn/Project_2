from joy import *
from delta_robot import *

class inputListener( Plan ):
  def __init__


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
    
    self.manual_mode = True
    self.point_mode = False
    
    # Store output specifier for later use
    self.spec = spec
    
  def onStart(self):
    # This function is called when the JoyApp is ready to start up,
    # i.e. after all PyGame devices have been activated, robot Cluster
    # is populated, scratch interface is live, etc.
    self.output = self.setterOf(self.spec)

  def onEvent(self,evt):
    # All unknown events --> punt to superclass
    if evt.type != MIDIEVENT:
      return JoyApp.onEvent(self,evt)

    if(self.manual_mode):
      if(evt.kind=='slider' and evt.index==1):
          self.robot.at.FIRST.set_torque((evt.value - 63.5)/127.0)
      elif(evt.kind=='slider' and evt.index==2):
          self.robot.at.SECOND.set_torque((evt.value - 63.5)/127.0)
      elif(evt.kind=='slider' and evt.index==3):
          self.robot.at.THIRD.set_torque((evt.value - 63.5)/127.0)   
    

    # If we reach this line, it was a MOUSEMOTION with button pressed
    #   so we send the value out to the output
    # self.output( evt.pos[1] )
    
  
app = HelloJoyApp("#output ")
app.run()
