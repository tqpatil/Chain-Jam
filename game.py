import pygame, time, random
from pygame.locals import *
import os
from math import atan2, degrees, pi, sin, cos 
import math
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SIDEBAR_WIDTH = 100
object_image = pygame.image.load('bomb.png')
mini_image = pygame.transform.scale(object_image, (80, 80))
class DraggableObject:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.dragging = False
        self.inSidebar = True
        self.velocity = [0,0]
        self.accel = [0,0]
        self.isLit = False
        self.timer = -1
        self.exploded = False
        self.duration = -1
    def draw(self, surface):
        if(self.dragging):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.center = (mouse_x, mouse_y)
            surface.blit(self.image, self.rect.topleft)
            
        else:
            surface.blit(self.image, self.rect.topleft)
    def handle_event(self,event,sidebar):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return 1
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                if(sidebar.rect.collidepoint(event.pos)):
                    self.inSidebar = True
                    sidebar.giveBack(self)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if(not self.dragging):
                if(self.rect.collidepoint(event.pos)):
                    self.isLit = True
                    self.timer = 100

        return 0 
    def isAtGround(self,ground):
        if(self.rect.bottomright[1] >= ground.rect.topleft[1]):
            self.rect.bottomright = (self.rect.bottomright[0],ground.rect.topleft[1])
            return True
        else:
            return False
    def isAtCeiling(self,ceiling):
        if(self.rect.topright[1] <= ceiling.rect.bottomright[1]):
            self.rect.topright = (self.rect.topright[0],ceiling.rect.bottomright[1])
            return True
        return False
    def simulateExplosion(self, level):
        return ## depending on the level, (counting backward from 4), switch the image


class Sidebar:

    def __init__(self, width, height, num_objects):
        self.rect = pygame.Rect(0, 0, width, height)
        self.object_count = num_objects
        self.mini_objects = [DraggableObject(mini_image, (10, 10 + i * 80)) for i in range(self.object_count)]
    
    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)
        for i in range(len(self.mini_objects)):
            self.mini_objects[i].draw(surface)

    def handle_event(self, event):
        for i in range(len(self.mini_objects)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.mini_objects[i].rect.collidepoint(event.pos):
                    self.mini_objects[i].dragging = True
                    self.mini_objects[i].inSidebar = False
                    return self.mini_objects.pop(i)
        return None
    def giveBack(self,obj):
        self.mini_objects.append(obj)
class Wall:
    def __init__(self,left,top,width,height):
        self.rect = pygame.Rect(left,top,width,height)

def explodeObj(objectList, ignoreInd):
    for i in range(len(objectList)):
        if(i == ignoreInd):
            continue
        else:
            x1 = objectList[ignoreInd].rect.center[0]
            y1 = objectList[ignoreInd].rect.center[1]
            x2 = objectList[i].rect.center[0]
            y2 = objectList[i].rect.center[1]
            dist = pygame.math.Vector2(x1,y1).distance_to((x2,y2))
            if(dist < 200):
                dx = x2-x1
                dy = y2-y1
                rads = atan2(-dy, dx)
                rads %= 2 * pi
                total_force = 1 + ((200-dist)*0.1)
                x_comp = total_force * cos(rads)
                y_comp = total_force * sin(rads)
                objectList[i].accel[0] +=x_comp
                objectList[i].accel[1] += y_comp
                continue
            else:
                continue
            
def main(window):
    #********** Game variables **********
    quit = False
    bg_image = pygame.image.load('bg.png')
    window.blit(pygame.transform.scale(bg_image, (500, 500)), (0, 0))
    pygame.display.update()
    sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 5)
    ground = Wall(0,SCREEN_HEIGHT-75, 5, 5)
    ceiling = Wall(0,10, 5, 5)
    numObjects = 0
    objectsList = []
    simulatePhysics = True
    #********** Start game loop **********
    while not quit:
        mx, my = pygame.mouse.get_pos()
        pygame.event.pump()
        window.blit(pygame.transform.scale(bg_image, (1280, 720)), (0, 0))
        sidebar.draw(window)
        for i in range(len(objectsList)):
            if(objectsList[i].isAtGround(ground)):
                objectsList[i].velocity[1] = 0 
                objectsList[i].accel[1] = 0
            if(simulatePhysics and objectsList[i].dragging == False):
                ## gravity
                if(objectsList[i].isAtGround(ground)):
                    objectsList[i].velocity[1] = 0
                    objectsList[i].accel[1] = 0
                else:
                    objectsList[i].accel[1] = 2
                if(objectsList[i].accel[0] > 0):
                    objectsList[i].accel[0] -= 0.1 * objectsList[i].accel[0]
                ## end gravity
                objectsList[i].rect.center = (objectsList[i].rect.center[0] + objectsList[i].velocity[0], objectsList[i].rect.center[1] + objectsList[i].velocity[1])
            if(objectsList[i].isAtCeiling(ceiling)):
                objectsList[i].velocity[1] = 0
                objectsList[i].accel[1] = 0
                if(objectsList[i].accel[0] > 0):
                    objectsList[i].accel[0] -= 0.5 * objectsList[i].accel[0]
            if(objectsList[i].isLit):
                if(objectsList[i].timer <= 4):
                    explodeObj(objectsList, i)
                    objectsList[i].isLit = False
                    objectsList[i].timer = -1
                    objectsList[i].exploded = True
                    objectsList[i].duration = 64
                else:
                    objectsList[i].timer -=1
            if(objectsList[i].exploded):
                if(objectsList[i].duration % 16 == 0):
                    objectsList[i].simulateExplosion(objectsList[i].duration//16)
                    objectsList[i].duration -= 1
                elif(objectsList[i].duration <= 0):
                    objectsList[i.duration]= -1
                else:
                    objectsList[i].duration -=1
            if(simulatePhysics):
                objectsList[i].velocity[1] = objectsList[i].velocity[1] + objectsList[i].accel[1]
                objectsList[i].velocity[0] = objectsList[i].velocity[0] + objectsList[i].accel[0]
        for i in range(len(objectsList)):
            objectsList[i].draw(window)
        # window.fill((0,0,0))                            # Reset screen to black
        #********** Process events *********
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            elif event.type == VIDEORESIZE:
                window = pygame.display.set_mode(
                    event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
                window.blit(pygame.transform.scale(bg_image, event.dict['size']), (0, 0))
                pygame.display.update()
            # elif(simulatePhysics == False):
            elif (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.MOUSEBUTTONUP):
                out = sidebar.handle_event(event)
                if(out is not None):
                    objectsList.append(out)
                for object in objectsList:
                    out = object.handle_event(event,sidebar)
                    if(out == 1):
                        break
            elif (event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_p):
                    simulatePhysics = (not simulatePhysics)
                elif(event.key == pygame.K_r):
                    for i in range(len(objectsList)-1, -1, -1):
                        del objectsList[i]
                    sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 5)

        for i in range(len(objectsList)-1, -1 ,-1):
            if(objectsList[i].inSidebar == True):
                del objectsList[i]
            elif(objectsList[i].exploded):
                if(objectsList[i].duration < 0):
                    del objectsList[i]
        # for object in objectsList:
        #     object.draw(window)
                
            


        #********** Your game logic here **********

        #********** Update screen **********
       
        pygame.display.update()                         # Actually does the screen update
        clock.tick(32)                                  # Run the game at 25 frames per second

#********** Initialise & run the game **********
if __name__ == "__main__":                             # Set screen width,height
    pygame.init()                                       # Start graphics system
    pygame.mixer.init()                                 # Start audio system
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)   # Create window
    clock = pygame.time.Clock()                        # Create game clock
    main(window)
    pygame.quit()