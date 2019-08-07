import pygame
from ncDrone import *
import copy
def select_initial_state(drones,target,grid,grids,grids2,ticks,run,communication_strategy):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    PURPLE = (150, 50, 150)

    WIDTH =14
    HEIGHT = 14
 
    grid_size = 50
    MARGIN = 5
    
 
    pygame.init()
 
    WINDOW_SIZE = [1100, 1100]
    screen = pygame.display.set_mode(WINDOW_SIZE)

    # Set title of screen
    pygame.display.set_caption("NC drone")
    image = pygame.image.load('falcon.png')
# Loop until the user clicks the close button.
    done = False
    image = pygame.transform.scale(image,[12,12])
    image = pygame.transform.rotate(image,-90)
# Used to manage how fast the screen updates
    clock = pygame.time.Clock()

   

    tick = 0
    beginNC = False
    communication_time = 1



# -------- Main Program Loop -----------
    while not done:


        path = []

        for event in pygame.event.get():  

            if event.type == pygame.QUIT:  
                done = True  
            elif pygame.mouse.get_pressed()[0]:  
                pos = pygame.mouse.get_pos()
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
            
                grid[row][column].color = 1
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
                grid[row][column].color = 3
           
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE  and beginNC == False:
                    beginNC = True
                elif event.key == pygame.K_SPACE  and beginNC == True:
                    beginNC = False
                elif event.key == pygame.K_DOWN:
                    grid = get_path_to_cluster(drones[1],grid[40][40],grid)                    
                elif event.key == pygame.K_RIGHT:
                    run = False
                    if communication_strategy == True:
                        for k,drone in enumerate(drones):
                            if tick_to_go(tick,k):
                                grid = drone.move(grid = grid,tick = tick)
                        #if tick %communication_time ==0:    
                        grid = target.move(grid = grid,tick = tick)   
                        grid = update_grid(grid,drones)
                    else:
                       for k,drone in enumerate(drones):
                            #print(k)
                            if tick_to_go(tick,k):
                                grid,_ = drone.move(grid = grid,tick = tick,grid_aux = [])
                                #print(k,drone.battery)
                                #print(drones[].x,' ',drones[1].y )
                    
                    tick+=1     



        if(tick >= ticks):
            done = True
        if(beginNC ):
            done = True

        
        if(run):
            if communication_strategy == True:
                
                for k,drone in enumerate(drones):
                    if tick_to_go(tick-1,k):
                        grid = drone.move(grid = grid,tick = tick)
                grid = target.move(grid = grid,tick = tick)
                #grid = update_grid(grid,drones)
            else:
                for k,drone in enumerate(drones):
                    if tick_to_go(tick,k):
                        grid,_ = drone.move(grid = grid,tick = tick,grid_aux = [])
                        print(k,drone.battery)
                
            tick+=1

        font = pygame.font.Font(None, 20)
    #text = font.render("1", True, BLACK)
        #size_obstacles(grid)
       
        screen.fill(BLACK)
        # Draw the grid
        for row in range(grid_size):
            for column in range(grid_size):
                color = WHITE
                text = font.render(str(grid[row][column].u_value), True, BLACK)
                if grid[row][column].color == 1:
                    color = GREEN
                if grid[row][column].color == 2:
                    color = BLUE
                if grid[row][column].color == 3:
                    color = RED
                if grid[row][column].color == 4:
                    color = PURPLE
                pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])
                screen.blit(text,((10+(19* grid[row][column].y )) - text.get_width()//2 ,(12 + (19 * grid[row][column].x )) -text.get_height()//2))
                
    # Limit to 60 frames per second
       # DRONE = drone[0]
        #x = drones[0]
        #screen.blit(image, (x,y))
        for i in range(len(drones)):
            screen.blit(image, (drones[i].posBoard[0], drones[i].posBoard[1]))
        screen.blit(image, (target.posBoard[0], target.posBoard[1]))

        clock.tick(20)

        pygame.display.flip()
 

    pygame.quit()
    if(beginNC ):
        return grid

   

