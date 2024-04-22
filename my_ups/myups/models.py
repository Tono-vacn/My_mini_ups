from django.db import models
from django.contrib.auth.models import User

class World(models.Model):
    world_id = models.CharField(max_length=100, primary_key=True)
    world_name = models.CharField(max_length=100, default="None")
    active_status = models.BooleanField(default=True)
    
class Account_tmp(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  account_world = models.ForeignKey(World, on_delete=models.CASCADE)
  
class Truck_Set(models.Model):
    truck_id = models.AutoField(primary_key=True)
    STATUS = (('I',"IDLE"),('A',"ARRIVED"),('T', 'TRAVELING'),('L',"LOADING"),('D',"DELIVERING"))
    truck_status = models.CharField(max_length=1, choices=STATUS, default='I')
    pos_x = models.CharField(max_length=30)
    pos_y = models.CharField(max_length=30)
    truck_world = models.ForeignKey(World, on_delete=models.CASCADE)
    a_seq = models.IntegerField(null=True)#for delivery request
    
class Package_tmp(models.Model):
    pkg_id = models.CharField(max_length=100, primary_key=True)
    pkg_user = models.ForeignKey(Account_tmp, null= True, on_delete=models.CASCADE)
    pkg_truck = models.ForeignKey(Truck_Set, null= True, on_delete=models.CASCADE)
    wharehouse_id = models.CharField(max_length=100)
    wharehouse_x = models.CharField(max_length=30)
    wharehouse_y = models.CharField(max_length=30)
    dst_x = models.CharField(max_length=30)
    dst_y = models.CharField(max_length=30)
    STATUS = (('T',"TO PICK UP"),('LED',"LOADED"),('LING',"LOADING"),('DING','DELIVERING'), ('DED','DELIVERED'))
    pkg_status = models.CharField(max_length=4, choices=STATUS)
    pkup_time = models.CharField(max_length=30)
    ld_time = models.CharField(max_length=30)
    del_time = models.CharField(max_length=30)
    world = models.ForeignKey(World, on_delete=models.CASCADE)
    a_seq = models.IntegerField(null=True)# for call truck request
    