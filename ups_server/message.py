import protocol.world_ups_pb2 as proto_world

def construct_world(UConnect, world_id, truck_num, pos_x, pos_y, start_id):
    for i in range(0, truck_num):
        truck = UConnect.trucks.add()
        truck.id = start_id
        truck.x = pos_x
        truck.y = pos_y
        start_id += 1
    UConnect.isAmazon = False
    if world_id != None:
        UConnect.worldid = int(world_id)