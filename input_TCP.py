


#!/usr/bin/python
import pickle
import socket
from json import dumps as json_dumps


mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.bind(("0.0.0.0",8080))
mySocket.listen(2)

client = None

while True:
  input_in = raw_input("enter a list to send seperated by commas: ")
  sendlist = [float(x) for x in input_in.split(',')]
  print sendlist
  if client is None:
    client,addr = mySocket.accept()

  try:
    pickledList = json_dumps(sendlist)
    client.send(pickledList)
  except Exception, ex:
    print str(ex)
    client = None


