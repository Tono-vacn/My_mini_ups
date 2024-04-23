import os
import psycopg2
import socket
import threading
import time

import protocol.world_ups_pb2 as proto_world
import protocol.ups_amazon_pb2 as proto_amazons

from message import *
from communication import *
from manage_db import *
from handler import *

world_host = "67.159.94.27"
world_port = 12345
amazon_port = 9000

database_host = "127.0.0.1"
database_port = 5432

init_db()

# Connect to the world
world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
world_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

while True:
    try:
        world_socket.connect((world_host, world_port))
    except BaseException as e:
        print(e)
        time.sleep(1)  # wait for a second before trying to connect again
    else:
        print("Connected successfully.")
        break
    finally:
        pass
    
# Connect to Amazon
amazon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
amazon.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Socket successfully created")
amazon.bind(('', amazon_port))
print("socket binded to %s" %(amazon_port))

amazon.listen(5)
print("socket is listening")

amazon_socket, addr = amazon.accept()
print('Got connection from', addr)

UAConnect = proto_amazon.AUConnect()
UAConnect = parse_delimited_from(UAConnect, amazon_socket)
connect_world_id = UAConnect.worldid
connect_ack = UAConnect.seqnum

# World initialization
world_id = str(connect_world_id)
truck_num = 50
pos_x = 0
pos_y = 0

world_exist = does_world_exist(world_id)
UConnect = proto_world.UConnect()

while True:
    try:
        if world_exist:
            construct_world(UConnect,  world_id, 0, pos_x, pos_y, 0)
        else:
            truck = get_max_truck()
            max_id = 1
            if truck != None:
                max_id = truck + 1
            construct_world(UConnect, world_id, truck_num, pos_x, pos_y, max_id)
        write_delimited_to(UConnect, world_socket)
        # print(UConnect.worldid)
        # print(UConnect.isAmazon)
        UConnected = proto_world.UConnected()
        UConnected = parse_delimited_from(UConnected, world_socket)
        print(UConnected.worldid)
        print(UConnected.result)
        if UConnected.result != "connected!":
            continue
        world_id = str(UConnected.worldid)
        break
    except (ConnectionRefusedError, ConnectionResetError, ConnectionError, ConnectionAbortedError) as e:
        print(e)
        continue
if not world_exist:
    create_world(world_id, True)
    start_trucks(world_id, pos_x, pos_y, truck_num)
switch_world(world_id)
UCommandspeed = proto_world.UCommands()
UCommandspeed.simspeed = 30000
write_delimited_to(UCommandspeed, world_socket)

UAConnected = proto_amazon.AUCommands()
UAConnected.worldid = connect_world_id
UAConnected.ack = connect_ack
write_delimited_to(UAConnected, amazon_socket)
# ----------------------------------------------------------------------------------
# Step 4 : Start to handle Requests
# ----------------------------------------------------------------------------------
# try:
thread1 = threading.Thread(target=amazon_handler, name="amazon", args=(world_id, amazon_socket, world_socket,))
thread1.start()
thread2 = threading.Thread(target=world_handler, name="world", args=(world_id, world_socket, amazon_socket,))
thread2.start()
while 1:
    pass
# except KeyboardInterrupt as k:
#     print("ctrl c pressed")
#     # disconnect 功能
#     UACommand = ups_amazon_pb2.UACommands()
#     UACommand.disconnect = True
#     send_msg(UACommand, amazon_socket)
#     UDisconn = ups_world_pb2.UCommands()
#     UDisconn.disconnect = True
#     send_msg(UDisconn, world_socket)