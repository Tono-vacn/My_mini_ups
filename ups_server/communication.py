from google.protobuf.internal.encoder import _VarintEncoder, _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

import protocol.world_ups_pb2 as proto_world
import protocol.ups_amazon_pb2 as proto_amazon

from message import *
DEBUG = 1

# Encode and decode messages
def write_delimited_to(message, socket):
    print(f"Sending message: {message}") if DEBUG else None
    serialized_message = message.SerializeToString()
    # print(len(serialized_message))
    # print(serialized_message)
    size = _VarintBytes(len(serialized_message))
    socket.sendall(size + serialized_message)

def parse_delimited_from(message, socket):
    raw_varint32 = b''
    raw_varint32 += socket.recv(1)
    size = _DecodeVarint32(raw_varint32, 0)[0]
    serialized_message = b''
    while len(serialized_message) < size:
        serialized_message += socket.recv(size - len(serialized_message))
    message.ParseFromString(serialized_message)

    return message

# World specifics
def send_world_ack(world_socket, ack):
    print(f"entry send_world_ack: {ack}") if DEBUG else None
    UCommands = proto_world.UCommands()
    world_ack(UCommands, ack)
    write_delimited_to(UCommands, world_socket)

def gen_world_truck_pkup(truck_id, wh_id, seqnum):
    UCommands = proto_world.UCommands()
    pkup = UCommands.pickups.add()
    pkup.truckid = int(truck_id)
    pkup.whid = int(wh_id)
    pkup.seqnum = int(seqnum)
    return UCommands

def gen_ua_truck_arrive(whnum, truck_id, pack_id, a_seq):
    
    print(f"gen_ua_truck_arrive: {whnum}, {truck_id}, {pack_id}, {a_seq}") if DEBUG else None
    UAresponse = proto_amazon.UAResponse()
    UAresponse.type = 0
    UAresponse.ack = a_seq
    print(UAresponse) if DEBUG else None
    truck_arrive = proto_amazon.UATruckArrive()
    print(f"truck_arrive init") if DEBUG else None
    truck_arrive.truckid = int(truck_id)
    truck_arrive.packageid = int(pack_id)
    truck_arrive.whnum = int(whnum)
    print(truck_arrive) if DEBUG else None
    UAresponse.ua_truck_arrive.CopyFrom(truck_arrive)
    print(UAresponse) if DEBUG else None
    return UAresponse

def gen_ua_delivered(pack_id, dest_x, dest_y, a_seq):
    UAresponse = proto_amazon.UAResponse()
    UAresponse.type = 1
    UAresponse.ack = a_seq
    
    delivered = proto_amazon.UADelivered()
    delivered.packageid = int(pack_id)
    delivered.destx = int(dest_x)
    delivered.desty = int(dest_y)
    
    UAresponse.ua_delivered.CopyFrom(delivered)
    
    return UAresponse
    
    

def gen_world_truck_deliver(truck_id, seqnum, pkg_id, dst_x, dst_y):
    UCommands = proto_world.UCommands()
    print(f"gen_world_truck_deliver: {truck_id}, {seqnum}, {pkg_id}, {dst_x}, {dst_y}") if DEBUG else None
    deliver = UCommands.deliveries.add()
    print(f"deliver init") if DEBUG else None
    deliver.truckid = int(truck_id)
    pkg_pos = deliver.packages.add()
    print(f"pkg_pos init") if DEBUG else None
    pkg_pos.packageid = int(pkg_id)
    pkg_pos.x = int(dst_x)
    pkg_pos.y = int(dst_y)
    deliver.seqnum = int(seqnum)
    print(f"deliver: {deliver}") if DEBUG else None
    print(f"UCommands: {UCommands}") if DEBUG else None
    return UCommands

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