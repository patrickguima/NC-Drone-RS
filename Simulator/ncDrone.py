import pygame
import util
import math
import random
import numpy as np
from functools import reduce
import statistics
import copy
class Drone:
    def __init__(self,x = 0 , y=0,manouvers = 0,direction = (0,0),communication_strategy = False,label = None):
        self.x = x
        self.y = y
        self.posBoard = ((x*19) +5,(y*19) +5)
        self.direction = direction
        self.manouvers = manouvers
        self.communication_strategy = communication_strategy
        self.path_water = []
        self.label = label
        self.max_battery = 40000
        self.battery = self.max_battery
        self.stations = []
        self.closest_station = None
        self.recharging = False
        self.grid_aux = None
        self.grid_aux2 = None
        self.grid_aux3 = []
        self.hover_expense = 200
        self.energy_threshold = 500
        self.num_target_found = 0
        self.time_target_found = []
        self.time_between_recharge = []
        self.fly_time = 0
        self.recharging_time = 0
        self.prev_rechargy = 0
    def moveRight(self):
        if(self.x <14):
            self.x+=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveLeft(self):
        if(self.x >0):
            self.x-=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveUp(self):
        if(self.y >0):
            self.y-=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveDown(self):
        if(self.y <14):
            self.y+=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5]
    def getBoardPos(self):

        return self.posBoard
    def move(self,grid,tick):
        grid_aux = self.grid_aux
        grid_aux2 = self.grid_aux2
        
        if self.recharging_time==12:
            self.battery =self.max_battery
            self.closest_station = None
            self.recharging = False
            self.recharging_time=0
           # print("aki")
        if self.battery == 0 :
            return grid

        #if self.label ==0:
         #   print(list(self.stations))
        if(self.y != -1 and self.x!= -1 and self.x<50):
            grid[self.y][self.x].color=1
            grid[40][10].color = 2
            grid[2][45].color = 2
       
        #chosen_drone = min(myDrones,key = lambda drone: euclidian_distance(drone.y,drone.x,clus.x,clus.y))
        
        if self.recharging ==False:
            self.check_neighbourhood(grid,grid_aux,tick)
            if len(self.path_water)>0:
                #for i in self.path_water:
                 #   grid[i.x][i.y].color = 1
                #self.getSucessor(grid = grid,grid_aux = [])
                if self.path_water[-1].occupied== False:
                    path = self.path_water.pop(-1)
                    x = self.y
                    y = self.x
                    if x+1 == path.x and y ==path.y:
                        path.dir_from_drone = (1,0) #down
                    if x-1 == path.x and y ==path.y:
                        path.dir_from_drone = (0,1) #up
                    if y+1 == path.y and path.x ==x:
                        path.dir_from_drone = (1,1) #right
                    if y-1 == path.y and path.x ==x:
                        path.dir_from_drone = (0,0) #left
                    path.cost = abs((self.direction[0]-path.dir_from_drone[0]) + abs(self.direction[1]-path.dir_from_drone[1]))
                   # print('cost',path.cost)
                   #+(path.cost*100)
                    
                    sucessors = [path]
                else:
                    sucessors = []

            else:
               
                #self.check_station(grid)

                if self.communication_strategy:
                    sucessors = self.getSucessor(grid = grid_aux,grid_aux = grid)
                else : 
                    sucessors = self.getSucessor(grid = grid,grid_aux = grid_aux)
            if len(sucessors)==0:
                return grid,grid_aux

            
            sucessor = random.choice(sucessors)
            sucessor.occupied = True
           # sucessor.visites+=1
            sucessor.u_value +=1
            grid[sucessor.x][sucessor.y].u_value+=1
            grid[sucessor.x][sucessor.y].occupied = True
            self.grid_aux2[sucessor.x][sucessor.y].u_value+=1
           # print(grid[sucessor.x][sucessor.y].u_value)
            #self.grid_aux[sucessor.x][sucessor.y].u_value =  self.grid_aux2[sucessor.x][sucessor.y].u_value
            if self.communication_strategy:
                grid[self.y][self.x].drone = None
                grid_aux[self.y][self.x].occupied = False
                grid[self.y][self.x].occupied = False
                grid[sucessor.x][sucessor.y].occupied = True

            else:
                grid[self.y][self.x].drone = None
                if self.x<50:
                    grid[self.y][self.x].occupied = False

            self.manouvers+=sucessor.cost
            self.direction = sucessor.dir_from_drone
            self.x = sucessor.y
            self.y = sucessor.x
            grid[self.y][self.x].drone = self
            grid[self.y][self.x].intervals.append(tick -grid[self.y][self.x].visita_anterior)
            grid[self.y][self.x].visita_anterior = tick
            self.posBoard = [(self.x*19) +5,(self.y*19) +5] 
            #decrase_uvalue(grid,self.feromone_value)
           # print(grid[self.y][self.x].drone)
            #if self.label==0:
             #   print('manouvers',self.manouvers)
              #  print(self.direction)

            
        if self.closest_station !=None:
        
            if self.x == self.closest_station.y and self.y == self.closest_station.x and self.battery<self.max_battery:
                #print('here2')
                if not self.recharging :
                    self.time_between_recharge.append(tick - self.prev_rechargy)
                    self.prev_rechargy = tick
                self.recharging_time+=1
                self.recharging =True
                self.path_water = []
                #return grid, grid_aux
        if self.recharging == False:
            self.fly_time +=1
            self.battery-=self.hover_expense +(sucessor.cost*25)
            if self.stations != []:
                station = min(self.stations, key = lambda station: euclidian_distance(self.y,self.x,station.x,station.y))
                if self.battery<=(len_station(self,station,grid)*self.hover_expense) +self.energy_threshold:
           #  if self.battery <euclidian_distance(self.y,self.x,self.stations[0].x,self.stations[0].y)*150:
                    self.closest_station = station
                    grid_aux = get_path_station(self,station,grid_aux)
            #print(euclidian_distance(self.y,self.x,self.stations[0].x,self.stations[0].y))
            self.check_neighbourhood(grid,grid_aux,tick)
            if self.label ==0:
                print("#############DATA##############")
                print('manouvers',self.manouvers)
                print('tick',tick)
                print('fly_time',self.fly_time)
                print('charge',self.time_between_recharge)
                print('battery',self.battery)
                print('direction',self.direction)
        return grid

    def getSucessor(self,grid,grid_aux):
        x = self.y
        y = self.x
        sucessors = []
        new_sucessors = []
        if  valide(self,x+1,y,grid,grid_aux,label = self.label):
            grid[x+1][y].dir_from_drone = (1,0)
            sucessors.append(grid[x+1][y])
        if valide(self,x-1,y,grid,grid_aux,label = self.label):
            grid[x-1][y].dir_from_drone = (0,1)
            sucessors.append(grid[x-1][y])
        if valide(self,x,y+1,grid,grid_aux,label = self.label):
            grid[x][y+1].dir_from_drone = (1,1)
            sucessors.append(grid[x][y+1])
        if valide(self,x,y-1,grid,grid_aux,label = self.label):
            grid[x][y-1].dir_from_drone = (0,0)
            sucessors.append(grid[x][y-1])

        #valide(self,x+1,y+1,grid,grid_aux,label = self.label)
        #valide(self,x+1,y-1,grid,grid_aux,label = self.label)
        #valide(self,x-1,y-1,grid,grid_aux,label = self.label)
        #valide(self,x-1,y+1,grid,grid_aux,label = self.label)   




        if len(sucessors)==0:
            return []
        #for suc in sucessors:
          #  if suc.color == 2 and suc not in self.stations:
           #     self.stations.append(suc)

        minimum_uvalue = min(sucessors,key = lambda x: x.u_value).u_value
        new_sucessors = list(filter(lambda x : x.u_value <= minimum_uvalue,sucessors))
        for suc in new_sucessors:
            suc.cost = abs(self.direction[0]-suc.dir_from_drone[0]) + abs(self.direction[1]-suc.dir_from_drone[1])

        cost =  min(new_sucessors, key = lambda x: x.cost).cost
        

        new_sucessors = list(filter(lambda x : x.cost <= cost,new_sucessors))
        return new_sucessors
        
    def check_neighbourhood(self,grid,grid_aux,tick):
        x = self.y
        y = self.x
    
        for i in range(1,4):
            if  valide2(self,x+i,y,grid,grid_aux,label = self.label):
                if grid[x+i][y].color ==2 and grid[x+i][y] not in self.stations:
                    self.stations.append(grid[x+i][y])
                if grid[x+i][y].drone!=None:
                    exchange_information(self,grid[x+i][y].drone,grid,tick)

            if valide2(self,x-i,y,grid,grid_aux,label = self.label):
                if grid[x-i][y].color ==2  and grid[x-i][y] not in self.stations:
                    self.stations.append(grid[x-i][y])
                if grid[x-i][y].drone!=None:
                    exchange_information(self,grid[x-i][y].drone,grid,tick)

            if valide2(self,x,y+i,grid,grid_aux,label = self.label):
                if grid[x][y+i].color ==2  and grid[x][y+i] not in self.stations:
                    self.stations.append(grid[x][y+i])
                if grid[x][y+i].drone!=None:
                    exchange_information(self,grid[x][y+i].drone,grid,tick)

            if valide2(self,x,y-i,grid,grid_aux,label = self.label):
                if grid[x][y-i].color ==2  and grid[x][y-i] not in self.stations:
                    self.stations.append(grid[x][y-i])
                if grid[x][y-i].drone!=None:
                    exchange_information(self,grid[x][y-i].drone,grid,tick)

            for j in range(1,4):      
                if valide2(self,x+j,y+i,grid,grid_aux,label = self.label):
                    if grid[x+j][y+i].color ==2  and grid[x+j][y+i] not in self.stations:
                        self.stations.append(grid[x+j][y+i])
                    if grid[x+j][y+i].drone!=None:
                        exchange_information(self,grid[x+j][y+i].drone,grid,tick)

                if valide2(self,x+j,y-i,grid,grid_aux,label = self.label):
                    if grid[x+j][y-i].color ==2  and grid[x+j][y-i] not in self.stations:
                        self.stations.append(grid[x+j][y-i])
                    if grid[x+j][y-i].drone!=None:
                        exchange_information(self,grid[x+j][y-i].drone,grid,tick)

                if valide2(self,x-j,y-i,grid,grid_aux,label = self.label):
                    if grid[x-j][y-i].color ==2  and grid[x-j][y-i] not in self.stations:
                        self.stations.append(grid[x-j][y-i])
                    if grid[x-j][y-i].drone!=None:
                        exchange_information(self,grid[x-j][y-i].drone,grid,tick)

                if valide2(self,x-j,y+i,grid,grid_aux,label = self.label):  
                    if grid[x-j][y+i].color ==2  and grid[x-j][y+i] not in self.stations:
                        self.stations.append(grid[x-j][y+i])
                    if grid[x-j][y+i].drone!=None:
                        exchange_information(self,grid[x-j][y+i].drone,grid,tick)

        return

class patch: 
    
    def __init__(self,u_value = 0,x = None , y=None,color = 0,dir_from_drone = (0,0),cost = 0,intervals = [],visites = 0,visita_anterior = 0):
        self.u_value = u_value
        self.x = x
        self.y = y
        self.color = color
        self.dir_from_drone = dir_from_drone
        self.cost = cost
        self.intervals = intervals
        self.visites = visites
        self.visita_anterior = visita_anterior
        self.occupied = False
        self.drone = None


def exchange_information(drone1, drone2,grid,tick):
    #if drone1.stations
   # print("TROCANDO INFO")
    #print(drone1.label)
    #print(drone2.label)
    grid_size = 50
    if drone2.label == 'target':
        drone2.found = True
        print("HERE",tick)
        drone2.num_found+=1
        drone1.num_target_found+=1
        drone1.time_target_found.append(tick)
        return

    for station in drone1.stations:
        if station not in drone2.stations:
            drone2.stations.append(station)

    for station in drone2.stations:
        if station not in drone1.stations:
            drone1.stations.append(station)
    
    for i in range(grid_size):
        for j in range(grid_size):
            drone1.grid_aux3[drone1.label][i][j].u_value = drone1.grid_aux2[i][j].u_value
            drone2.grid_aux3[drone2.label][i][j].u_value = drone2.grid_aux2[i][j].u_value

            drone1.grid_aux3[drone2.label][i][j].u_value = drone2.grid_aux2[i][j].u_value
            drone2.grid_aux3[drone1.label][i][j].u_value = drone1.grid_aux2[i][j].u_value

         
            drone1.grid_aux[i][j].u_value = drone1.grid_aux3[0][i][j].u_value + drone1.grid_aux3[1][i][j].u_value+ drone1.grid_aux3[2][i][j].u_value+ drone1.grid_aux3[3][i][j].u_value
            drone2.grid_aux[i][j].u_value = drone2.grid_aux3[0][i][j].u_value + drone2.grid_aux3[1][i][j].u_value+ drone2.grid_aux3[2][i][j].u_value+ drone2.grid_aux3[3][i][j].u_value
    return 
def euclidian_distance(x1,y1,x2,y2):
    return math.sqrt( ((x1-x2)**2) +((y1-y2)**2))
def decrase_uvalue(grid,feromone_value):
    for row in grid:
        for column in row:
           #print("u_value", column.u_value)
            column.u_value -= feromone_value   
    return grid


    return
def get_path_station(drone,cluster,grid):
    x_total=  cluster.x - drone.y 
    y_total = cluster.y - drone.x
       # path_water = [] 
    for i in range(abs(x_total)):
        if(x_total)<0:
            k = i
        else:
            k = -i 
        drone.path_water.append(grid[cluster.x+k][cluster.y])
    for i in range(abs(y_total)):
        if y_total <0:
            k = i
        else :
            k= -i
        drone.path_water.append(grid[drone.y][cluster.y+k])
    return grid

def len_station(drone,cluster,grid):
    x_total=  cluster.x - drone.y 
    y_total = cluster.y - drone.x
    path_water = [] 
    for i in range(abs(x_total)):
        if(x_total)<0:
            k = i
        else:
            k = -i 
        path_water.append(grid[cluster.x+k][cluster.y])
    for i in range(abs(y_total)):
        if y_total <0:
            k = i
        else :
            k= -i
        path_water.append(grid[drone.y][cluster.y+k])
    return len(path_water)
def valide(drone,x,y,grid,grid_aux,label = 0):
    
    if (x <0 or x >49 or y <0 or y> 49):
        return False
    if grid[x][y].color==3:
        return False
    if grid[x][y].color==2:
     #   drone.stations.add(grid[x][y])
        return False
    #if grid[x][y] in in_cluster:
     #   return True
    if grid[x][y].occupied:
        return False
    if len(grid_aux)>0:
        if grid_aux[x][y].color==3:
            return False
        if grid_aux[x][y].color==2:
            return False
        if grid_aux[x][y].occupied:
            return False


    return True 

def valide2(drone,x,y,grid,grid_aux,label = 0):
    
    if (x <0 or x >49 or y <0 or y> 49):
        return False
    if grid[x][y].color==3:
        return False
    return True

def sdf(grid):
    sdf = 0
    frequencies = []
    for row in grid:
        aux  =list(filter(lambda x: x.color != 3  ,row))
        aux  =list(filter(lambda x: x.color != 2 ,aux))      
        for column in aux:
            frequencies.append(column.u_value)

    #f_avg = np.mean(frequencies)
    f_avg = statistics.mean(frequencies)
    for freq in frequencies:
        sdf += (freq - f_avg)**2
    #print(len(frequencies))
    sdf = math.sqrt(sdf / len(frequencies))
    #print("SDF") 
    #print(sdf)
    #print("media",np.mean(f_avg))
    return sdf
    
def qmi(grid,tick):
    qmi = 0
    interval =0 
    #print("MQI: ")
    total_intervals = 0

    total_cells= 0
    for row in grid:
        aux  =list(filter(lambda x: x.color != 3 and x.color != 2 ,row))     
        for column in aux:
            interval = 0
            total_intervals+= len(column.intervals)
            for i in column.intervals:
                interval+= (i**2)
            total_cells+=interval
                
            #interval += (reduce((lambda x,y: y-x),column.intervals))**2
    #print(total_cells)
    #print(total_intervals)
    qmi = math.sqrt(total_cells/total_intervals)
    #print(qmi)
    return qmi

def ncc (grid):
    #print("ncc: ")
    min_ncc = []
    aux = []
    minimo = 0

    for row in grid:
        aux = []
        aux  =list(filter(lambda x: x.color != 3 ,row))
        aux  =list(filter(lambda x: x.color != 2 ,aux)) 
        #print(aux[0].u_value)                  
        minimo = min(aux, key = lambda x : x.u_value ).u_value
        min_ncc.append(minimo)
   # print(min(min_ncc))
    ncc = min(min_ncc)
    return ncc
def metrics(drones,target,grid,tick):
#    print("### MATRICS ###")
    results  = []
    for i in range(len(drones)):
        results.append([i,drones[i].num_target_found,statistics.mean(drones[i].time_target_found)])
    return results,target.num_found

def simulation(drone,grid,tick):
    drone.move(grid,tick)
def tick_to_go(tick,k):
    if tick>=k:
        return True
    return False


def update_grid(grid,drones):
    grid_size = 50
    u_value_total =  0 
    visites_total = 0
   # grid = []
    grid1 = drones[0].grid_aux2
    grid2 = drones[1].grid_aux2
    grid3 = drones[2].grid_aux2
    grid4 = drones[3].grid_aux2
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i][j].u_value = drones[0].grid_aux[i][j].u_value #+ drones[1].grid_aux2[i][j].u_value +  drones[2].grid_aux2[i][j].u_value +drones[3].grid_aux2[i][j].u_value
            if grid[i][j].u_value >0:
                grid[i][j].color = 1
            #print(grid[i][j].visites)
  
    grid[40][10].color = 2
    grid[2][45].color = 2
    return grid

def size_obstacles(grid):
    obs = []
    for row in grid:
        for column in row:
            if column.color ==3:
                obs.append((column.x,column.y))

    
    print(len(obs))
    return
def get_obstacles(grid):
    obs = []
    for row in grid:
        for column in row:
            if column.color ==3:
                obs.append((column.x,column.y))

    
    #print(obs)
    #print(len(obs))
    return
def make_obstacles1(grid):
    obs = [(0, 26), (0, 27), (0, 28), (0, 29), (0, 30), (0, 31), (0, 32), (0, 33), (0, 34), (0, 35), (0, 36), (0, 37), (0, 38), (1, 26), (1, 27), (1, 28), (1, 29), (1, 30), (1, 31), (1, 32), (1, 33), (1, 34), (1, 35), (1, 36), (1, 37), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 26), (2, 27), (2, 28), (2, 29), (2, 30), (2, 31), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 26), (3, 27), (3, 28), (3, 29), (3, 30), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 26), (4, 27), (4, 28), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 26), (5, 27), (5, 28), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 26), (6, 27), (6, 28), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (11, 4), (11, 5), (11, 6), (11, 7), (11, 8), (15, 39), (15, 40), (15, 41), (15, 42), (15, 43), (15, 44), (16, 39), (16, 40), (16, 41), (16, 42), (16, 43), (16, 44), (17, 39), (17, 40), (17, 41), (17, 42), (17, 43), (17, 44), (17, 45), (18, 40), (18, 41), (18, 42), (18, 43), (18, 44), (18, 45), (19, 41), (19, 42), (19, 43), (19, 44), (19, 45), (20, 41), (20, 42), (20, 43), (20, 44), (20, 45), (21, 43), (21, 44), (21, 45), (22, 43), (22, 44), (22, 45), (23, 43), (23, 44), (23, 45), (24, 9), (24, 10), (24, 11), (24, 12), (24, 13), (24, 14), (24, 43), (24, 44), (25, 9), (25, 10), (25, 11), (25, 12), (25, 13), (25, 14), (25, 43), (25, 44), (26, 9), (26, 10), (26, 11), (26, 12), (26, 13), (26, 14), (27, 9), (27, 10), (27, 11), (27, 12), (27, 13), (27, 14), (28, 9), (28, 10), (28, 11), (29, 9), (29, 10), (29, 11), (30, 9), (30, 10), (30, 11), (31, 10), (31, 11), (41, 15), (41, 16), (41, 17), (41, 18), (41, 19), (41, 20), (41, 21), (41, 22), (41, 23), (41, 24), (41, 25), (41, 26), (41, 27), (41, 28), (42, 12), (42, 13), (42, 14), (42, 15), (42, 16), (42, 17), (42, 18), (42, 19), (42, 20), (42, 21), (42, 22), (42, 23), (42, 24), (42, 25), (42, 26), (42, 27), (42, 28), (43, 11), (43, 12), (43, 13), (43, 14), (43, 15), (43, 16), (43, 17), (43, 18), (43, 19), (43, 20), (43, 21), (43, 22), (43, 23), (43, 24), (43, 25), (43, 26), (43, 27), (43, 28), (44, 12), (44, 13), (44, 14), (44, 15), (44, 16), (44, 17), (44, 18), (44, 19), (44, 20), (44, 21), (44, 22), (44, 23), (44, 24), (44, 25), (44, 26), (44, 27)]
    for ob in obs:
        grid[ob[0]][ob[1]].color=3
    return




def make_obstacles2(grid):
    obs = [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 31), (5, 32), (5, 33), (5, 34), (5, 35), (5, 36), (5, 37), (5, 38), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 31), (6, 32), (6, 33), (6, 34), (6, 35), (6, 36), (6, 37), (6, 38), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 38), (7, 39), (7, 40), (7, 41), (7, 42), (7, 43), (7, 44), (7, 45), (7, 46), (7, 47), (7, 48), (7, 49), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 38), (8, 39), (8, 40), (8, 41), (8, 42), (8, 43), (8, 44), (8, 45), (8, 46), (8, 47), (8, 48), (8, 49), (9, 38), (9, 39), (9, 40), (9, 41), (9, 42), (9, 43), (9, 44), (9, 45), (9, 46), (9, 47), (9, 48), (9, 49), (10, 38), (10, 39), (10, 40), (10, 41), (10, 42), (10, 43), (10, 44), (10, 45), (10, 46), (10, 47), (10, 48), (10, 49), (11, 38), (11, 39), (11, 40), (11, 41), (11, 42), (11, 43), (11, 44), (11, 45), (11, 46), (11, 47), (11, 48), (11, 49), (12, 38), (12, 39), (12, 40), (12, 41), (12, 42), (12, 43), (12, 44), (12, 45), (12, 46), (12, 47), (12, 48), (12, 49), (13, 38), (13, 39), (13, 40), (13, 41), (13, 42), (13, 43), (13, 44), (13, 45), (13, 46), (13, 47), (13, 48), (13, 49), (26, 5), (26, 6), (26, 7), (26, 8), (26, 9), (26, 10), (26, 30), (26, 31), (26, 32), (27, 5), (27, 6), (27, 7), (27, 8), (27, 9), (27, 10), (27, 30), (27, 31), (27, 32), (28, 5), (28, 6), (28, 7), (28, 8), (28, 9), (28, 10), (28, 30), (28, 31), (28, 32), (29, 5), (29, 6), (29, 7), (29, 8), (29, 9), (29, 10), (29, 30), (29, 31), (29, 32), (30, 5), (30, 6), (30, 7), (30, 8), (30, 9), (30, 10), (30, 25), (30, 26), (30, 27), (30, 28), (30, 29), (30, 30), (30, 31), (30, 32), (31, 5), (31, 6), (31, 7), (31, 8), (31, 9), (31, 10), (31, 25), (31, 26), (31, 27), (31, 28), (31, 29), (31, 30), (31, 31), (31, 32), (31, 33), (31, 34), (32, 25), (32, 26), (32, 27), (32, 28), (32, 29), (32, 30), (32, 31), (32, 32), (32, 33), (32, 34), (33, 25), (33, 26), (33, 27), (33, 28), (33, 29), (33, 30), (33, 31), (33, 32), (33, 33), (33, 34), (34, 25), (34, 26), (34, 27), (34, 28), (34, 29), (34, 30), (34, 31), (34, 32), (34, 33), (34, 34)]
    for ob in obs:
        grid[ob[0]][ob[1]].color=3
    return

def make_obstacles3(grid):
    obs = [(0, 0), (0, 1), (0, 2), (0, 14), (0, 15), (0, 16), (0, 17), (0, 18), (0, 19), (0, 20), (0, 21), (0, 22), (0, 23), (0, 24), (0, 25), (0, 44), (0, 45), (0, 46), (0, 47), (1, 0), (1, 1), (1, 2), (1, 14), (1, 15), (1, 16), (1, 17), (1, 18), (1, 19), (1, 20), (1, 21), (1, 22), (1, 23), (1, 24), (1, 25), (1, 44), (1, 45), (1, 46), (1, 47), (2, 0), (2, 1), (2, 2), (2, 14), (2, 15), (2, 16), (2, 17), (2, 18), (2, 23), (2, 24), (2, 25), (2, 45), (2, 46), (2, 47), (3, 0), (3, 1), (3, 2), (3, 14), (3, 15), (3, 16), (3, 17), (3, 23), (3, 24), (3, 25), (3, 45), (3, 46), (3, 47), (4, 0), (4, 1), (4, 2), (4, 14), (4, 15), (4, 16), (4, 17), (4, 23), (4, 24), (4, 25), (4, 45), (4, 46), (4, 47), (5, 0), (5, 1), (5, 2), (5, 14), (5, 15), (5, 16), (5, 17), (5, 23), (5, 24), (5, 25), (6, 14), (6, 15), (6, 16), (6, 17), (6, 23), (6, 24), (6, 25), (7, 14), (7, 15), (7, 16), (7, 17), (7, 23), (7, 24), (7, 25), (22, 21), (22, 22), (22, 23), (22, 24), (22, 25), (23, 17), (23, 18), (23, 19), (23, 20), (23, 21), (23, 22), (23, 23), (23, 24), (23, 25), (23, 26), (24, 17), (24, 18), (24, 19), (24, 20), (24, 21), (24, 22), (24, 23), (24, 24), (24, 25), (24, 26), (25, 17), (25, 18), (25, 19), (25, 20), (25, 21), (25, 22), (25, 23), (25, 24), (25, 25), (25, 26), (25, 27), (26, 18), (26, 19), (26, 20), (26, 21), (26, 22), (26, 23), (26, 24), (26, 25), (26, 26), (26, 27), (27, 19), (27, 20), (27, 21), (27, 22), (27, 23), (27, 24), (27, 25), (27, 26), (36, 37), (36, 38), (36, 39), (37, 37), (37, 38), (37, 39), (38, 7), (38, 8), (38, 9), (38, 10), (38, 11), (38, 12), (38, 13), (38, 37), (38, 38), (38, 39), (39, 6), (39, 7), (39, 8), (39, 9), (39, 10), (39, 11), (39, 12), (39, 13), (39, 37), (39, 38), (39, 39), (40, 6), (40, 7), (40, 8), (40, 9), (40, 10), (40, 11), (40, 12), (40, 13), (40, 37), (40, 38), (40, 39), (40, 40), (40, 41), (40, 42), (40, 43), (40, 44), (40, 45), (41, 6), (41, 7), (41, 8), (41, 9), (41, 10), (41, 11), (41, 12), (41, 13), (41, 37), (41, 38), (41, 39), (41, 40), (41, 41), (41, 42), (41, 43), (41, 44), (41, 45), (42, 6), (42, 7), (42, 8), (42, 9), (42, 10), (42, 11), (42, 12), (42, 13), (42, 37), (42, 38), (42, 39), (42, 40), (42, 41), (42, 42), (42, 43), (42, 44), (42, 45), (43, 7), (43, 8), (43, 9), (43, 10), (43, 11), (43, 12), (43, 13), (43, 37), (43, 38), (43, 39), (43, 40), (43, 41), (43, 42), (43, 43), (43, 44), (43, 45)]
    for ob in obs:
        grid[ob[0]][ob[1]].color=3
    return

class Target:
    def __init__(self,x = 0 , y=0,manouvers = 0,direction = (0,0),label = None,mode = 0):
        self.x = x
        self.y = y
        self.posBoard = ((x*19) +5,(y*19) +5)
        self.direction = direction
        self.manouvers = manouvers
        self.watershed_mode = False
        self.label = label
        self.found = False
        self.num_found = 0
        self.mode = mode
    def moveRight(self):
        if(self.x <14):
            self.x+=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveLeft(self):
        if(self.x >0):
            self.x-=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveUp(self):
        if(self.y >0):
            self.y-=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5] 
    def moveDown(self):
        if(self.y <14):
            self.y+=1
            self.posBoard = [(self.x*37) +5,(self.y*37) +5]
    def getBoardPos(self):

        return self.posBoard
    def move(self,grid,tick):
        if self.found == True:
            self.found = False
            while(1):

                x = int(random.uniform(0, 49))
                y = int(random.uniform(0, 49))
                print(x,y)
                if valide(drone = None,x = y,y = x,grid=grid,grid_aux = [],label = self.label):
                    grid[self.y][self.x].occupied = False
                    grid[self.y][self.x].drone = None
                    self.x = x
                    self.y = y
                    grid[self.y][self.x].occupied = True
                    grid[self.y][self.x].drone = self
                    self.posBoard = [(self.x*19) +5,(self.y*19) +5] 
                    return grid

        if(self.y != -1 and self.x!= -1 and self.x<50):
            grid[self.y][self.x].color=4
            grid[40][10].color = 2
            grid[2][45].color = 2
       
            
        if self.mode ==0:
            return grid
        if self.mode == 2:
            self.check_neighbourhood(grid,[])

        sucessors = self.getSucessor(grid = grid,grid_aux = [])
        if len(sucessors)==0:
            return grid

            
        sucessor = random.choice(sucessors)
        sucessor.occupied = True
       
        grid[self.y][self.x].drone = None
        if self.x<50:
            grid[self.y][self.x].occupied = False

        self.manouvers+=sucessor.cost
        self.direction = sucessor.dir_from_drone
        self.x = sucessor.y
        self.y = sucessor.x
        grid[self.y][self.x].drone = self
        grid[self.y][self.x].intervals.append(tick -grid[self.y][self.x].visita_anterior)
        grid[self.y][self.x].visita_anterior = tick
        self.posBoard = [(self.x*19) +5,(self.y*19) +5] 
        #decrase_uvalue(grid,self.feromone_value)
        #print('#######TARGET######')
        #print(self.num_found)
        if self.mode == 2:
            self.check_neighbourhood(grid,[])
        return grid

    def getSucessor(self,grid,grid_aux):
        x = self.y
        y = self.x
        sucessors = []
        new_sucessors = []
        if  valide(self,x+1,y,grid,grid_aux,label = self.label):
            grid[x+1][y].dir_from_drone = (1,0)
            sucessors.append(grid[x+1][y])
        if valide(self,x-1,y,grid,grid_aux,label = self.label):
            grid[x-1][y].dir_from_drone = (0,1)
            sucessors.append(grid[x-1][y])
        if valide(self,x,y+1,grid,grid_aux,label = self.label):
            grid[x][y+1].dir_from_drone = (1,1)
            sucessors.append(grid[x][y+1])
        if valide(self,x,y-1,grid,grid_aux,label = self.label):
            grid[x][y-1].dir_from_drone = (0,0)
            sucessors.append(grid[x][y-1])

        if len(sucessors)==0:
            return []

        if self.mode==1:
            return sucessors
        #minimum_uvalue = min(sucessors,key = lambda x: x.u_value).u_value
        #new_sucessors = list(filter(lambda x : x.u_value <= minimum_uvalue,sucessors))
        for suc in sucessors:
            suc.cost = abs(self.direction[0]-suc.dir_from_drone[0]) + abs(self.direction[1]-suc.dir_from_drone[1])

        cost =  min(sucessors, key = lambda x: x.cost).cost
        

        new_sucessors = list(filter(lambda x : x.cost <= cost,sucessors))
        return new_sucessors
        
    def check_neighbourhood(self,grid,grid_aux):
        x = self.y
        y = self.x
    
        for i in range(1,5):
            if  valide2(self,x+i,y,grid,grid_aux,label = self.label):
                if grid[x+i][y].drone!=None:
                    self.change_direction()

            if valide2(self,x-i,y,grid,grid_aux,label = self.label):
                if grid[x-i][y].drone!=None:
                    self.change_direction()

            if valide2(self,x,y+i,grid,grid_aux,label = self.label):
                if grid[x][y+i].drone!=None:
                    self.change_direction()

            if valide2(self,x,y-i,grid,grid_aux,label = self.label):
                if grid[x][y-i].drone!=None:
                    self.change_direction()

            for j in range(1,5):      
                if valide2(self,x+j,y+i,grid,grid_aux,label = self.label):
                    if grid[x+j][y+i].drone!=None:
                        self.change_direction()

                if valide2(self,x+j,y-i,grid,grid_aux,label = self.label):
                    if grid[x+j][y-i].drone!=None:
                        cself.change_direction()

                if valide2(self,x-j,y-i,grid,grid_aux,label = self.label):
                    if grid[x-j][y-i].drone!=None:
                        self.change_direction()

                if valide2(self,x-j,y+i,grid,grid_aux,label = self.label):  
                    if grid[x-j][y+i].drone!=None:
                        self.change_direction()

        return
    def change_direction(self):
        self.direction = (abs(self.direction[0] - 1),abs(self.direction[1] - 1))
        
        return