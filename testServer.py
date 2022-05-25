from websocket import create_connection

ipadress = ''

def TestServer():
   # Get Connection To server
   ws = create_connection("ws://"+ipadress+":3001/")
   #Send a message
   ws.send("python hello!")
   #Get message back
   print (ws.recv())
   #Close Connection
   ws.close()

TestServer()
