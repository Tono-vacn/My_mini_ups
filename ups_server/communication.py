from google.protobuf.internal.encoder import _VarintEncoder, _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

import protocol.world_ups_pb2 as proto_world
import protocol.ups_amazon_pb2 as proto_amazon


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