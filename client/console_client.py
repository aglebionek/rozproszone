#!/usr/bin/python3

# Client program

from socket import socket, AF_INET, SOCK_STREAM
import json

# Set the socket parameters
host = "localhost"
port = 8080
buf = 1024
addr = (host, port)

# Create socket
sock = socket(AF_INET, SOCK_STREAM)

print ("\n===Enter message to send to server===\n")

sock.connect(addr)
# Send messages
data = {"user": None, "command": "", "data": {}}
while True:
    user_input = input('>> ')
    data["command"] = user_input
    if not user_input:
        break
    else:
        bin_data = json.dumps(data).encode()
        if(sock.sendto(bin_data, addr)):
            print ("Sending message '{}'.....".format(user_input))

# Close socket
sock.close()

