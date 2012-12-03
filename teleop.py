import ckbot.logical as L
import delta_robot

c = L.Cluster()
c.populate(3)

c.at.Nx15.set_speed(10)
c.at.Nx16.set_speed(10)
c.at.Nx17.set_speed(10)


while True:
  positions = raw_input("enter positions seperated by commas: ")
  pos_list = [float(x) for x in positions.split(',')]
  target_angles = delta_robot.delta_calcInverse(pos_list[0], pos_list[1], pos_list[2])
  print target_angles
  if(-1 in target_angles):
    print "impossible position"
    continue
  else:
    c.at.Nx15.set_pos(target_angles[0]*100)
    c.at.Nx16.set_pos(target_angles[1]*100)
    c.at.Nx17.set_pos(target_angles[2]*100)
