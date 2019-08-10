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
        self.posBoard = ((x*15) +1,(y*15) +1)
        self.direction = direction
        self.manouvers = manouvers
        self.communication_strategy = communication_strategy
        self.path_water = []
        self.label = label
        self.max_battery = 175824
        self.battery = self.max_battery
        self.stations = []
        self.closest_station = None
        self.recharging = False
        self.grid_aux = None
        self.grid_aux2 = None
        self.grid_aux3 = []
        self.hover_expense = 210
        self.energy_threshold = 29304
        self.num_target_found = 0
        self.time_target_found = []
        self.time_between_recharge = []
        self.fly_time = 0
        self.num_recharges = 0
        self.recharging_time = 0
        self.prev_rechargy = 0
        self.time_target_found_last = 0
        self.stop = 0
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
        
        if self.recharging_time==22:
            self.battery =self.max_battery
            self.closest_station = None
            self.recharging = False
            self.recharging_time=0
           # print("aki")
        if self.battery == 0 :
            self.stop = 1
            return grid

       
        if(self.y != -1 and self.x!= -1 and self.x<50):
            grid[self.y][self.x].color=1
            grid[40][10].color = 2
            grid[2][45].color = 2
       
      
        if self.recharging ==False:

            self.check_neighbourhood(grid,grid_aux,tick)
            if len(self.path_water)>0:
              
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
                   
                    
                    sucessors = [path]
                else:
                    sucessors = []

            else:

                if self.communication_strategy:
                    sucessors = self.getSucessor(grid = grid_aux,grid_aux = grid)
                else : 
                    sucessors = self.getSucessor(grid = grid,grid_aux = grid_aux)
            if len(sucessors)==0:
                return grid,grid_aux

            
            sucessor = random.choice(sucessors)
            sucessor.occupied = True
            sucessor.u_value +=1 
            grid[sucessor.x][sucessor.y].occupied = True
            self.grid_aux2[sucessor.x][sucessor.y].u_value+=1
         
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
            self.posBoard = [(self.x*15) +1,(self.y*15) +1] 
           
            
            self.battery-=self.hover_expense +(sucessor.cost*25)
            if self.stations != []:
                station = min(self.stations, key = lambda station: euclidian_distance(self.y,self.x,station.x,station.y))
                if self.battery<=(len_station(self,station,grid)*self.hover_expense) +self.energy_threshold:
                    self.closest_station = station
                   
                    grid_aux = get_path_station(self,station,grid_aux)
            
            self.check_neighbourhood(grid,grid_aux,tick)
            
        if self.closest_station !=None:
        
            if self.x == self.closest_station.y and self.y == self.closest_station.x and self.recharging_time<22:
               
                if self.recharging == False:
                    self.time_between_recharge.append(tick - self.prev_rechargy)
                    self.prev_rechargy = tick
                    self.num_recharges+=1
                self.recharging_time+=1
                self.recharging =True
                self.path_water = []
            else:
                self.fly_time +=1
        else:
            self.fly_time +=1
            
   

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
   
    grid_size = 50
    if drone2.label == 'target':
        if drone2.found == False:
            drone2.found = True
            drone2.num_found+=1

            drone1.num_target_found+=1
            drone1.time_target_found.append(tick - drone1.time_target_found_last)
            drone1.time_target_found_last = tick
            drone2.interval_found.append(tick - drone2.time_last_found)
            drone2.time_last_found = tick
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
        return False
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
def metrics(drones,target,grid):
    results  = []
    target_results = []
    target_results.append([target.num_found,statistics.mean(target.interval_found)])
    for i in range(len(drones)):
        results.append([i,drones[i].num_target_found,statistics.mean(drones[i].time_target_found),
            drones[i].num_recharges,statistics.mean(drones[i].time_between_recharge),drones[i].manouvers])

    return results,target_results

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
   
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i][j].u_value = drones[0].grid_aux2[i][j].u_value + drones[1].grid_aux2[i][j].u_value +  drones[2].grid_aux2[i][j].u_value +drones[3].grid_aux2[i][j].u_value
           
  
    grid[40][10].color = 2
    grid[2][45].color = 2
    return grid



class Target:
    def __init__(self,x = 0 , y=0,manouvers = 0,direction = (0,0),label = 'target',mode = 0):
        self.x = x
        self.y = y
        self.posBoard = ((x*15) +1,(y*15) +1)
        self.direction = direction
        self.manouvers = manouvers
        self.watershed_mode = False
        self.label = label
        self.found = False
        self.num_found = 0
        self.mode = mode
        self.drones_directions = []
        self.time_change_direction = 0
        self.time_change_direction_total = 30
        self.interval_found = []
        self.time_last_found = 0
   
    def getBoardPos(self):

        return self.posBoard
    def move(self,grid,tick):
        if self.found == True:
            self.found = False
            while(1):

                x = int(random.uniform(0, 49))
                y = int(random.uniform(0, 49))
                #print(x,y)
                if valide(drone = None,x = y,y = x,grid=grid,grid_aux = [],label = self.label):
                    grid[self.y][self.x].occupied = False
                    grid[self.y][self.x].drone = None
                    self.x = x
                    self.y = y
                    grid[self.y][self.x].occupied = True
                    grid[self.y][self.x].drone = self
                    self.posBoard = [(self.x*15) +1,(self.y*15) +1] 
                    return grid

        if(self.y != -1 and self.x!= -1 and self.x<50):
            grid[self.y][self.x].color=4
            grid[40][10].color = 2
            grid[2][45].color = 2
       
            
        if self.mode ==0:
            return grid
      
        sucessors = self.getSucessor(grid = grid,grid_aux = [])
        if len(sucessors)==0:
            return grid

            
        sucessor = random.choice(sucessors)
        sucessor.occupied = True
        sucessor.u_value+=1
        grid[self.y][self.x].drone = None
        if self.x<50:
            grid[self.y][self.x].occupied = False

        self.manouvers+=sucessor.cost
        self.direction = sucessor.dir_from_drone
        self.x = sucessor.y
        self.y = sucessor.x
        grid[self.y][self.x].drone = self
        grid[self.y][self.x].color = 4
        grid[self.y][self.x].intervals.append(tick -grid[self.y][self.x].visita_anterior)
        grid[self.y][self.x].visita_anterior = tick
        self.posBoard = [(self.x*15) +1,(self.y*15) +1] 
        
        if self.mode == 2:
            self.check_neighbourhood(grid,[])
            if self.drones_directions== []:
                if self.time_change_direction >= self.time_change_direction_total:
                    self.time_change_direction_total = int(random.uniform(30, 50))
                    self.time_change_direction = 0
                    self.direction = random.choice([(0,0),(0,1),(1,0),(1,1)])
            

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
        minimum_uvalue = min(sucessors,key = lambda x: x.u_value).u_value
        new_sucessors = list(filter(lambda x : x.u_value <= minimum_uvalue,sucessors))
        for suc in sucessors:
            suc.cost = abs(self.direction[0]-suc.dir_from_drone[0]) + abs(self.direction[1]-suc.dir_from_drone[1])

        cost =  min(sucessors, key = lambda x: x.cost).cost
        

        new_sucessors = list(filter(lambda x : x.cost <= cost,sucessors))
        return new_sucessors
        
    def check_neighbourhood(self,grid,grid_aux):
        x = self.y
        y = self.x

    
        for i in range(1,6):
            if  valide2(self,x+i,y,grid,grid_aux,label = self.label):
                #grid[x+i][y].color=4
                if grid[x+i][y].drone!=None:#down
                    self.drones_directions.append((1,0))

            if valide2(self,x-i,y,grid,grid_aux,label = self.label):
               # grid[x-i][y].color = 4
                if grid[x-i][y].drone!=None:#UP
                    self.drones_directions.append((0,1))

            if valide2(self,x,y+i,grid,grid_aux,label = self.label):
               # grid[x][y+i].color = 4
                if grid[x][y+i].drone!=None: #right
                    self.drones_directions.append((1,1))

            if valide2(self,x,y-i,grid,grid_aux,label = self.label):
                
                if grid[x][y-i].drone!=None: #left
                    self.drones_directions.append((0,0))

            for j in range(1,6):      
                if valide2(self,x+j,y+i,grid,grid_aux,label = self.label):
                   
                    if grid[x+j][y+i].drone!=None: #down-right
                        self.drones_directions.append((1,0))
                        self.drones_directions.append((1,1))

                if valide2(self,x+j,y-i,grid,grid_aux,label = self.label):
                    if grid[x+j][y-i].drone!=None: #down-left
                        self.drones_directions.append((1,0))
                        self.drones_directions.append((0,0))

                if valide2(self,x-j,y-i,grid,grid_aux,label = self.label):
                    if grid[x-j][y-i].drone!=None: #up-left
                        self.drones_directions.append((0,1))
                        self.drones_directions.append((0,0))

                if valide2(self,x-j,y+i,grid,grid_aux,label = self.label): 
                    #grid[x-j][y+i].color = 4
                    if grid[x-j][y+i].drone!=None:#up-right
                        self.drones_directions.append((0,1))
                        self.drones_directions.append((1,1))
        if self.drones_directions !=[]:
            self.time_change_direction =0
            self.change_direction()
        else:
          
            self.time_change_direction+=1
            
        return
    def change_direction(self):
        
        directions = [(0,0),(1,1),(1,0),(0,1)]
        new_direction = list(filter(lambda x : x not in self.drones_directions,directions))
        if new_direction != []:
            if self.direction not in new_direction:
                self.direction = random.choice(new_direction)
        self.drones_directions.clear()
        return