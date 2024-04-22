from communication import *
from tb_controller import *
from message import *
import protocol.world_ups_pb2 as proto_world
import protocol.ups_amazon_pb2 as proto_amazon
import sys, os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import smtplib

seqnum = 1
seq_mutex = threading.Lock()
# locks = []  # lock the packages when need to change their status

acks = [] # store ack message
ack_mutex = threading.Lock()
# lock for acks[]

### Handler for world
def get_truck_info(completion):
    return completion.truckid, completion.x, completion.y

def deliver_complete(completion, world_id, world_socket):
    send_world_ack(world_socket, completion.seqnum)
    truck_id, addr_x, addr_y = get_truck_info(completion)
    modify_truck_status(truck_id, "I", addr_x, addr_y, world_id)
    return

def arrive_complete(completion, world_id, world_socket):
    # get truck_id, wh_location, truck status
    # change truck status to "l"
    # send truck_arrived to Amazon
    send_world_ack(world_socket, completion.seqnum)
    truck_id, addr_x, addr_y = get_truck_info(completion)
    modify_truck_status(truck_id, "L", addr_x, addr_y, world_id)
    # TODO: send truck_arrived to Amazon
    UACommand = ups_amazon_pb2.UACommands()
    # print("when arrive at warehouse")
    # print(UACommand)
    # find package id
    pack_id = req_package_to_pack(truck_id, wh_x, wh_y, world_id)
    amazon_truck_arrive(UACommand, wh_x, wh_y, truck_id, pack_id)
    send_msg(UACommand, amazon_socket)
    # print("after send")
    return

def completion_handler(completion, world_id, amazon_socket, world_socket):
    if completion.status == "IDLE":
        deliver_complete(completion, world_id, world_socket)
    else:
        print("enter arrive handler")
        arrive_complete(completion, world_id, amazon_socket, world_socket)
    return
    

def world_handler(world_id, world_socket, amazon_socket):
    num_threads = 5
    pool = ThreadPoolExecutor(num_threads)
    while 1:
        # set the number of threads as you want
        UResponse = proto_world.UResponses() 
        UResponse = parse_delimited_from(UResponse, world_socket)
        print("recv from world")
        print(UResponse)
        print("recv finished")
        for a in range(0, len(UResponse.completions)):
            pool.submit(completion_handler, UResponse.completions[a], world_id, amazon_socket, world_socket)
        for b in range(0, len(UResponse.delivered)):
            pool.submit(Deliver_Handler, UResponse.delivered[b], world_id, amazon_socket, world_socket)
        for c in range(0, len(UResponse.truckstatus)):
            pool.submit(Query_Handler, UResponse.truckstatus[c], world_id)
        if len(UResponse.acks):
            pool.submit(Ack_Handler, UResponse.acks)
        for d in range(0, len(UResponse.error)):
            pool.submit(Error_Handler, UResponse.error[d], world_id)
        if UResponse.HasField("finished"):
            pool.submit(Disconnect_amazon, UResponse.finished, world_id)
    return

