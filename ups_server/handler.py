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

### utils for handler

def generate_seqnum():
    global seqnum
    seq_mutex.acquire()
    cur_seq = seqnum
    seqnum += 1
    seq_mutex.release()
    return cur_seq

def err_handler(err_message, source):
    print(source+" error: "+err_message)
    return 

def chck_ack(cur_seq):
    global acks
    return True if cur_seq in acks else False
        

def send_blk(msg, socket, cur_seq):
    while True:
        write_delimited_to(msg, socket)
        time.sleep(10)
        if chck_ack(cur_seq):
            break
    return

def send_email(email_addr, content):
    host = "smtp.gmail.com"
    port = 587
    From = "DukeUpsOfficial@gmail.com"
    pwd = "UpsOfficial+1s"
    s = smtplib.SMTP(host, port)
    s.starttls()
    s.login(From, pwd)
    SUBJECT = "UPS Notification!"
    message = 'Subject: {}\n\n{}'.format(SUBJECT, content)
    s.sendmail(From, email_addr, message)
    s.quit()
    return

### Handler for Amazon

def call_truck_handler(au_call_truck, world_id, amazon_socket ,world_socket):
    cur_seq = generate_seqnum()
    pkg_id = au_call_truck.packageid
    dstx = au_call_truck.destx
    dsty = au_call_truck.desty
    whid = au_call_truck.whnum
    acc = au_call_truck.order.ups_userid
    truck_id = get_truck(world_id)
    while truck_id == None:
        truck_id = get_truck(world_id)
    init_pkg(pkg_id, acc, truck_id, whid, None, None, dstx, dsty, world_id)
    UCommand = gen_world_truck_pkup(truck_id, whid, cur_seq)
    modify_truck_status(truck_id, "T", None, None, world_id)
    send_blk(UCommand, world_socket, cur_seq)
    pass

def ready_deliver_handler(au_ready_deliver, world_id, amazon_socket, world_socket):
    cur_seq = generate_seqnum()
    truck_id = au_ready_deliver.truckid
    pkg_id = au_ready_deliver.packageid
    dstx = au_ready_deliver.destx
    dsty = au_ready_deliver.desty
    whid = au_ready_deliver.whnum
    
    # check the package status with local data
    tkid, dx, dy = get_pkg_truckid(pkg_id, world_id)
    if tkid!=truck_id or dx!=dstx or dy!=dsty:
        print("package status not match", "amazon")

    # modify the package status
    
    UCommand = gen_world_truck_deliver(truck_id, cur_seq, pkg_id, dstx, dsty)
    modify_truck_status(truck_id, "D", None, None, world_id)
    load_deliver_pkg(pkg_id, world_id)
    email_addr = get_pkg_email(pkg_id, world_id)
    send_email(email_addr, "Your package is on the way") if email_addr!=None else None
    send_blk(UCommand, world_socket, cur_seq)
    pass

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
    UACommand = proto_amazon.UACommands()
    # print("when arrive at warehouse")
    # print(UACommand)
    # find package id
    pack_id = get_single_pkg_to_pkup(truck_id, world_id, addr_x, addr_y)
    gen_amazon_arrive(UACommand, wh_x, wh_y, truck_id, pack_id)
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

def amazon_handler(world_id, amazon_socket, world_socket):
    num_threads = 5
    pool = ThreadPoolExecutor(num_threads)
    while 1:
        AUCommands = proto_amazon.AUCommands()
        AUCommands = parse_delimited_from(AUCommands, amazon_socket)
        print("recv from amazon")
        print(AUCommands)
        print("recv finished")
        if AUCommands.HasField("au_call_truck"):
            pool.submit(call_truck_handler, AUCommands.au_call_truck, world_id, amazon_socket, world_socket)
            pass
        if AUCommands.HasField("au_ready_deliver"):
            pool.submit(ready_deliver_handler, AUCommands.au_ready_deliver, world_id, amazon_socket, world_socket)
            pass
        if AUCommands.HasField("err"):
            pool.submit(err_handler, AUCommands.err, "amazon")
            pass

