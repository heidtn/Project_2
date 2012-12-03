import ckbot.logical as L
import delta_robot
import sys
import time

SPEED = 10


c = L.Cluster()
c.populate(3)

FIRST = c.at.Nx15
SECOND = c.at.Nx16
THIRD = c.at.Nx17

FIRST.set_speed(SPEED)
SECOND.set_speed(SPEED)
THIRD.set_speed(SPEED)


mode = -1

while True:
  if mode == 1:
    positions = raw_input("enter positions seperated by commas: ")
    pos_list = [float(x) for x in positions.split(',')]
    target_angles = delta_robot.delta_calcInverse(pos_list[0], pos_list[1], pos_list[2])
    print target_angles
    if(-1 in target_angles):
      print "impossible position"
      continue
    else:
      FIRST.set_pos(target_angles[0]*100)
      SECOND.set_pos(target_angles[1]*100)
      THIRD.set_pos(target_angles[2]*100)
    mode = -1
  elif mode == 5:
    FIRST.set_pos(-13*100)
    SECOND.set_pos(-13*100)
    THIRD.set_pos(-13*100)

    time.sleep(5)  

    FIRST.go_slack()
    SECOND.go_slack()
    THIRD.go_slack()
    
    sys.exit(1)
  else:

    mode = input("select mode number:  \n  1. manual\n  2. calibrate\n  3. square\n  4. strokes\n  5. exit\ntype mode: ")

  
