import pygame
from ncDrone import *
from pygame_run import *
import copy
import random
from dataxlsm import *
import numpy as np
import time

def valide_start_point(grid):
    valide = []
    for row in grid:
        aux = []
        
        aux = list(filter(lambda x:x.color !=3,row))
        for i in aux:
            valide.append((i.y,i.x))

    #print(valide)
    return valide





def go():
  

    #NUMERO DE TICKS
    ticks =10000
    #ESTRATEGIAS ADOTADAS
    simulation_on_screen = True
    time_strategy =False
    evaporation_strategy = False
    quandrant_strategy = False

    #PARAMETROS DE SIMULAÇAO
    evap_time = 0
    evap_factor =  0
    threshold_time = 0
    num_simulations = 2
    #NUMERO DE VANTs
    number_drones = 4

    #TRUE PARA RODAR E FALSE PARA RODAR PASSO A PASSO 
    run = True


    #OUTRAS ESTRATEGIAS QUE FORAM DESCARTADAS
    communication_strategy = True
    watershed_strategy = False



   
    #INICIALIZAÇAO
    #water = watershed(water_threshold = water_threshold,communication_strategy = communication_strategy)
    #water.water_threshold = 0
    #water.communication_strategy = communication_strategy
    metrics_results = []
    grid_size = 50
    initial_grid = []
   

    for row in range(grid_size):
        initial_grid.append([])
        for column in range(grid_size):     
            aux_patch = patch(u_value = 0,x = row,y = column,color = 0,intervals = [],visites = 0,visita_anterior = 0)
            initial_grid[row].append(aux_patch)


    for i in range(num_simulations):
        grid = []
        grids = []
        grids2 = []
        #grids3 = []

        grid = copy.deepcopy(initial_grid)

        grid[40][10].color = 2
        grid[2][45].color = 2
        #ADCIONAR OBSTACULOS (BASTA DESCOMENTAR)

        #make_obstacles1(grid)
        #make_obstacles2(grid)
        #make_obstacles3(grid)
        if communication_strategy == True:    
            for j in range(number_drones):
                grids.append(copy.deepcopy(initial_grid))
                grids2.append(copy.deepcopy(initial_grid))
               # grids3.append(copy.deepcopy(initial_grid))
            
        drones  = []
        while(1):
            x = int(random.uniform(0, 49))
            y = int(random.uniform(0, 49))
            print(x,y)
            if valide(drone = None,x = y,y = x,grid=grid,grid_aux = [],label = None):
                break

        target = Target(x = x,y = y,label = 'target',manouvers = 0, direction =(1,1),mode = 1)
        grid[target.y][target.x].drone = target
        grid[target.y][target.x].occupied = True

        for num in range(number_drones):
            drone  = Drone(x = -1,y = 49,label = num,manouvers = 0, direction =(1,1),communication_strategy = communication_strategy)
                #drone.stations.add(grid[40][10])
                #drone.stations.add(grid[2][45])
            drone.grid_aux = grids[num]
            drone.grid_aux2 = grids2[num]
            for d in range(number_drones):
                drone.grid_aux3.append(copy.deepcopy(initial_grid))
                #drone.grid_aux3 = grids3[num]
                #drone.grid_aux4 = grids4[num]
            drones.append(drone)

        

        if simulation_on_screen:
            select_initial_state(drones = drones, target = target,grid = grid,grids = grids,grids2 = grids2,ticks = ticks, run  =run   ,communication_strategy = communication_strategy)

        else:    
            for tick in range(ticks):
               # print(tick)
                if communication_strategy == True:
                    for k,drone in enumerate(drones):
                        if tick_to_go(tick,k):
                            grid = drone.move(grid = grid,tick = tick)

                    grid = target.move(grid = grid, tick = tick)
                    #grid = update_grid(grid,drones) 
                else:
                    for k,drone in enumerate(drones):
                        if tick_to_go(tick,k):
                            grid,_ = drone.move(grid = grid,tick = tick,grid_aux = [])
                   
        
            #grid = update_grid(grid,drones)
        #size_obstacles(grid)
        soma_manobras = 0      
        for drone in drones:
            soma_manobras += drone.manouvers
        results, target_found =  metrics(drones,target,grid,ticks)
        print("results: ")
        for k in range(len(drones)):
            print(results[k])
        print("target_found: ",target_found)
        #print("ncc: ",ncc)
        ##print("manobras",soma_manobras)
        #metrics_results.append([i,qmi,sdf,ncc,soma_manobras])
        grid.clear()
        drones.clear()
        if communication_strategy:
            for i in range(number_drones):
                grids[i].clear()
                grids2[i].clear()

   # write_xlsm(metrics_results)
    return








if '__main__' == __name__:
    inicio = time.time()
    go()
    fim = time.time()
    print('tempo de execução = ',fim - inicio)


    #colocar alvos estatico, movel aleatorio e movel direçao contraria
    #coloacr modelos de energia
    #colocar parametros de avaliação (tempo de voo, tempo entre recargas, numero de vezes que um alvo foi encontrado e tempo de encontro )