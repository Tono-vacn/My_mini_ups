from google.protobuf.internal.encoder import _VarintEncoder, _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

import protocol.world_ups_pb2 as proto_world
import protocol.ups_amazon_pb2 as proto_amazon

from message import *

# Encode and decode messages
def write_delimited_to(message, socket):
    serialized_message = message.SerializeToString()
    print(len(serialized_message))
    print(serialized_message)
    size = _VarintBytes(len(serialized_message))
    socket.sendall(size + serialized_message)

def parse_delimited_from(message, socket):
    raw_varint32 = b''
    while True:
        raw_varint32 += socket.recv(1)
        try:
            size = _DecodeVarint32(raw_varint32, 0)[0]
            break
        except IndexError:
            continue
    print(size)
    serialized_message = socket.recv(size)
    message.ParseFromString(serialized_message)

    return message

# World specifics
def send_world_ack(ack, world_socket):
    UCommands = proto_world.UCommands()
    world_ack(UCommands, ack)
    write_delimited_to(UCommands, world_socket)

def gen_world_truck_pkup(truck_id, wh_id, seqnum):
    UCommands = proto_world.UCommands()
    pkup = UCommands.pickup.add()
    pkup.truckid = truck_id
    pkup.whid = wh_id
    pkup.seqnum = seqnum
    return UCommands

def gen_ua_truck_arrive(whnum, truck_id, pack_id, a_seq):
    UAresponse = proto_amazon.UAResponse()
    UAresponse.type = 0
    UAresponse.ack = a_seq
    truck_arrive = UAresponse.ua_truck_arrive.add()
    truck_arrive.whnum = whnum
    truck_arrive.truckid = truck_id
    truck_arrive.packageid = pack_id
    return UAresponse

def gen_ua_delivered(pack_id, a_seq):
    UAresponse = proto_amazon.UAResponse()
    UAresponse.type = 1
    UAresponse.ack = a_seq
    delivered = UAresponse.ua_delivered.add()
    delivered.packageid = pack_id
    return UAresponse
    
    

def gen_world_truck_deliver(truck_id, seqnum, pkg_id, dst_x, dst_y):
    UCommands = proto_world.UCommands()
    deliver = UCommands.deliveries.add()
    deliver.truckid = truck_id
    pkg_pos = deliver.packages.add()
    pkg_pos.packageid = pkg_id
    pkg_pos.x = int(dst_x)
    pkg_pos.y = int(dst_y)
    deliver.seqnum = seqnum
    return UCommands

# send amazon message

def gen_amazon_arrive(UACommands, whnum, truck_id, pack_id):
    arrive = UACommands.ua_truck_arrive.add()
    arrive.whnum = whnum
    arrive.truckid = truck_id
    arrive.packageid = pack_id
    # return UACommands

if __name__ == "__main__":
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    server_address = ('localhost', 12345)  # replace with your server's address
    sock.connect(server_address)

    message = proto_world.UInitTruck()
    message.id = 1
    message.x = 0
    message.y = 0
    write_delimited_to(message, sock)
    message_recv = proto_world.UInitTruck()
    parse_delimited_from(message_recv, sock)
    print(message_recv.id, message_recv.x, message_recv.y)