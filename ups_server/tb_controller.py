from manage_db import *
import time
DEBUG = 1

def create_world(world_id, curr):
  # insert new world into world
  session = session_local()
  try:
    world = World()
    world.world_id = world_id
    world.world_name = "default_world"
    world.active_status = curr
    session.add(world)
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  pass

def check_world(world_id):
  # check if world exist
  session = session_local()
  try:
    world = session.query(World).filter(World.world_id == world_id).first()
    return world is not None
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  pass


def get_max_truck():
  session = session_local()
  try:
    truck = session.query(Truck).order_by(Truck.truck_id.desc()).first()
    if truck == None:
      return None
    return truck.truck_id
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  
def check_acc(user_name):
  session = session_local()
  try:
    acc = session.query(BaseUser).filter(BaseUser.username == user_name).first()
    return acc is not None
  except Exception as e:
    print(f"An error occurred: {e}")
    # session.rollback()
  finally:
    session.close()
    
def switch_world(world_id):
  session = session_local()
  try:
    world = session.query(World).filter(World.active_status == True).first()
    world.active_status = False
    session.commit()
    world = session.query(World).filter(World.world_id == world_id).first()
    world.active_status = True
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  pass

def start_trucks(world_id, pos_x, pos_y, truck_num):
  session = session_local()
  try:
    for i in range(truck_num):
      truck = Truck()
      truck.truck_status = "I"
      truck.pos_x = pos_x
      truck.pos_y = pos_y
      truck.truck_world_id = world_id
      session.add(truck)
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  pass

def modify_truck_status(truck_id, status, pos_x, pos_y, world_id):
  session = session_local()
  try:
    truck = session.query(Truck).filter(Truck.truck_id == truck_id, Truck.truck_world_id == world_id).first()
    truck.truck_status = status
    truck.pos_x = pos_x if pos_x != None else truck.pos_x
    truck.pos_y = pos_y if pos_y != None else truck.pos_y
    # truck.a_seq = a_seq if a_seq != None else truck.a_seq
    # truck.truck_world
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
  pass

def init_pkg(pkg_id, user_id, truck_id, wh_id, wh_x, wh_y, dst_x, dst_y, world_id, a_seq):
  session = session_local()
  try:
    pkg = Package()
    pkg.pkg_id = pkg_id
    cur_user_id = session.query(BaseUser).filter(BaseUser.username == user_id).first().id
    cur_acc_id = session.query(Account).filter(Account.user_id == cur_user_id).first().id
    pkg.pkg_user_id = cur_acc_id
    pkg.pkg_truck_id = truck_id
    pkg.wharehouse_id = wh_id
    pkg.wharehouse_x = wh_x
    pkg.wharehouse_y = wh_y
    pkg.dst_x = dst_x
    pkg.dst_y = dst_y
    pkg.pkg_status = "T"
    pkg.pkup_time = time.ctime(time.time())
    pkg.world_id = world_id
    pkg.a_seq = a_seq
    session.add(pkg)
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
def load_deliver_pkg(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    pkg.pkg_status = "DING"
    pkg.ld_time = time.ctime(time.time())
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()  
    
def deliver_done_pkg(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    pkg.pkg_status = "DED"
    pkg.del_time = time.ctime(time.time())
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    

def modify_destination(pkg_id, pos_x, pos_y, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    pkg.dst_x = pos_x
    pkg.dst_y = pos_y
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
def get_pkg_truckid(pkg_id, world_id):
  session = session_local()
  print(f"enter pkg truckid: {pkg_id}, {world_id}") if DEBUG else None
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    print(f"pkg_truck_id: {pkg.pkg_truck_id}, pkg_x: {pkg.dst_x}, pkg_y: {pkg.dst_y}") if DEBUG else None
    return (pkg.pkg_truck_id, pkg.dst_x, pkg.dst_y) if pkg is not None else (None, None, None)
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
def get_pkg_email(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    acc = session.query(Account).filter(Account.id == pkg.pkg_user_id).first()
    cur_user = session.query(BaseUser).filter(BaseUser.id == acc.user_id).first()
    return cur_user.email if cur_user is not None else None
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
def get_single_pkg_to_pkup(truck_id, world_id, wh_x, wh_y):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_status == "T", Package.world_id == world_id, Package.wharehouse_x == wh_x, Package.wharehouse_y == wh_y, Package.pkg_truck_id == truck_id).first()
    return pkg.pkg_id if pkg != None else None
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
def get_truck(world_id):
  print(f"in get_truck") if DEBUG else None
  session = session_local()
  print_table(Truck) if DEBUG else None
  try:
    truck = session.query(Truck).filter(Truck.truck_world_id == world_id, Truck.truck_status == "I").first()
    return truck.truck_id if truck != None else None
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    session.close()

def get_pkg_status(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    return (pkg.pkg_status, pkg.pkg_truck_id) if pkg is not None else (None, None)
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    session.close()

def get_pkg_time(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    return (pkg.pkup_time, pkg.ld_time, pkg.del_time) if pkg is not None else (None, None, None)
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    session.close()
    
    
def get_pkg_whid(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    return pkg.wharehouse_id if pkg != None else None
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    session.close()
    
def get_seqnum(pkg_id, world_id):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    return pkg.a_seq if pkg != None else None
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    session.close()
    
def set_pkg_seq(pkg_id, world_id, seq):
  session = session_local()
  try:
    pkg = session.query(Package).filter(Package.pkg_id == pkg_id, Package.world_id == world_id).first()
    pkg.a_seq = seq
    session.commit()
  except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
  finally:
    session.close()
    
# def get_seqnum_deliver(truck_id, world_id):
#   session = session_local()
#   try:
#     truck = session.query(Truck).filter(Truck.truck_id == truck_id and Truck.truck_world == world_id).first()
#     return truck.a_seq if truck != None else None
#   except Exception as e:
#     print(f"An error occurred: {e}")
#   finally:
#     session.close()