import pygame, time, random
from pygame.locals import *
import os
from math import atan2, degrees, pi, sin, cos 
import math
from pygame import mixer
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
        self.gravityOff = False
        self.duration = -1
    def draw(self, surface):
        if(self.dragging):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.center = (mouse_x, mouse_y)
            surface.blit(self.image, self.rect.topleft)
            
        else:
            surface.blit(self.image, self.rect.topleft)
    def handle_event(self,event,sidebar, simulatePhysics):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and simulatePhysics == False:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return 1
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and simulatePhysics == False:
            if self.dragging:
                self.dragging = False
                if(sidebar.rect.collidepoint(event.pos)):
                    self.inSidebar = True
                    sidebar.giveBack(self)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if(not self.dragging):
                if(self.rect.collidepoint(event.pos)):
                    if(self.isLit == False):
                        self.isLit = True
                        mixer.Channel(0).set_volume(0.7)
                        mixer.Channel(0).play(pygame.mixer.Sound("fuse.ogg"))
                        self.timer = 80
                    return 3

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
    def isOnPlatform(self,platform):
        if(self.rect.bottomright[1] >= (platform.rect.topleft[1]-10) and self.rect.bottomright[1] <= platform.rect.topleft[1]+30 and self.rect.bottomleft[0] >= platform.rect.topleft[0] and self.rect.bottomright[0] <= platform.rect.topright[0] and self.velocity[1] >= 0):
            return True
        else:
            return False
    def simulateExplosion(self, level):
        if(level == 4):
            self.image=self.image = pygame.transform.scale(object_image, (90, 90))
        elif(level == 3):
            self.image = pygame.transform.scale(object_image, (92, 92))
        elif(level == 2):
            self.image = pygame.transform.scale(object_image, (94, 94))
        elif(level == 1):
            self.image = pygame.transform.scale(object_image, (96, 96))
    def simulateAfter(self,level):
        if(level == 4):
            self.image.set_alpha(self.image.get_alpha()-50)
        elif(level == 3):
            self.image.set_alpha(self.image.get_alpha()-50)
        elif(level == 2):
            self.image.set_alpha(self.image.get_alpha()-50)
        elif(level == 1):
            self.image.set_alpha(self.image.get_alpha()-50)
 ## depending on the level, (counting backward from 4), switch the image


class Sidebar:

    def __init__(self, width, height, num_objects):
        self.rect = pygame.Rect(0, 0, width, height)
        self.object_count = num_objects
        self.mini_objects = [DraggableObject(mini_image, (10, 10 + i * 80)) for i in range(self.object_count)]
    
    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)
        for i in range(len(self.mini_objects)):
            self.mini_objects[i].draw(surface)

    def handle_event(self, event,simulatePhysics):
        for i in range(len(self.mini_objects)):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and simulatePhysics == False:
                if self.mini_objects[i].rect.collidepoint(event.pos):
                    self.mini_objects[i].dragging = True
                    self.mini_objects[i].inSidebar = False
                    return self.mini_objects.pop(i)
        return None
    def giveBack(self,obj):
        self.mini_objects.append(obj)
class Wall:
    def __init__(self,left,top,width,height, image):
        self.rect = pygame.Rect(left,top,width,height)
        self.image =image
        self.isExploded = False
def explodeObj(objectList, ignoreInd, targets):
    for i in range(len(targets)):
        x1 = targets[i].rect.center[0]
        y1 = targets[i].rect.center[1]
        x2 = objectList[ignoreInd].rect.center[0]
        y2 = objectList[ignoreInd].rect.center[1]
        dist = pygame.math.Vector2(x1,y1).distance_to((x2,y2))
        if(dist < 150):
            targets[i].isExploded = True
    for i in range(len(objectList)):
        if(i == ignoreInd):
            continue
        else:
            x1 = objectList[ignoreInd].rect.center[0]
            y1 = objectList[ignoreInd].rect.center[1]
            x2 = objectList[i].rect.center[0]
            y2 = objectList[i].rect.center[1]
            dist = pygame.math.Vector2(x1,y1).distance_to((x2,y2))
            if(dist < 150):
                if(objectList[i].isLit == False):
                    objectList[i].isLit =True
                    objectList[i].timer = 90
                mixer.Channel(0).set_volume(0.7)
                mixer.Channel(0).play(pygame.mixer.Sound("boom.ogg"))
                dx = x2-x1
                dy = y2-y1
                rads = atan2(-dy, dx)
                rads %= 2 * pi
                total_force = 5 + ((200-dist)*0.25)
                x_comp = 0.7 * total_force * cos(rads)
                y_comp = total_force * sin(rads) + (0.2 * total_force * sin(rads))
                objectList[i].velocity[0] +=(x_comp)
                objectList[i].velocity[1] -= (y_comp + 10)
                continue
            else:
                continue
def title_screen(window):
    mixer.init()
    mixer.music.load("TitleScreen.ogg")
    mixer.music.set_volume(0.3)
    mixer.music.play(loops=-1)
    
    One = pygame.image.load("1.png")
    two = pygame.image.load("2.png")
    three = pygame.image.load("3.png")
    four = pygame.image.load("4.png")
    bg_image = pygame.image.load('bg.png')
    window.blit(pygame.transform.scale(bg_image, (1280, 720)), (0, 0))
    pygame.display.update()
    images = [One,two,three,four]
    selections = [Wall(200, 640, 50,50,One), Wall(500,640, 50, 50, two), Wall(800,640,50,50,three),Wall(1100,640,50,50,four)]
    quit = False
    pygame.font.init() 
    my_font = pygame.font.SysFont('Comic Sans MS', 50)
    font2= pygame.font.SysFont('Comic Sans MS', 20)
    out = -1
    while not quit:
        for i in range(len(selections)):
            window.blit(pygame.transform.scale(images[i], (selections[i].rect.width, selections[i].rect.height)), (selections[i].rect.left,selections[i].rect.top))
        text_surface = my_font.render('Launchpad', False, (0, 0, 0))
        text_surf2 = font2.render('A simple game about launching bombs to a goal.', False, (0,0,0))
        text_surf3 = font2.render('Rules:', False, (0,0,0))
        text_surf4 = font2.render("1. Press 'P' to start simulation(enables gravity, explosion timer)", False, (0,0,0))
        text_surf5 = font2.render("2. Press 'R' to reset the game.", False, (0,0,0))
        text_surf6= font2.render("3. You cannot drop bombs from above the lowest goal.", False, (0,0,0))
        text_surf7 = font2.render("4.Right click to light a bomb.", False, (0,0,0))
        text_surf8= font2.render("5. Explode bombs on the goal (highlighted in yellow)!", False, (0,0,0))
        window.blit(text_surface, (SCREEN_WIDTH/2-125,50))
        window.blit(text_surf2, (SCREEN_WIDTH/2-300,150))
        window.blit(text_surf3, ((SCREEN_WIDTH/2-600,180)))
        window.blit(text_surf4, ((SCREEN_WIDTH/2-600,230)))
        window.blit(text_surf5, ((SCREEN_WIDTH/2-600,280)))
        window.blit(text_surf6, ((SCREEN_WIDTH/2-600,330)))
        window.blit(text_surf7, ((SCREEN_WIDTH/2-600,380)))
        window.blit(text_surf8, ((SCREEN_WIDTH/2-600,430)))
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            elif event.type == VIDEORESIZE:
                window = pygame.display.set_mode(
                    event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
                window.blit(pygame.transform.scale(bg_image, event.dict['size']), (0, 0))
                pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if(event.button == 1):
                    for i in range(len(selections)):
                        if(selections[i].rect.collidepoint(event.pos)):
                            mixer.music.stop()
                            out = main(window,i+1)
                            if(out == -1):
                                return
        
        pygame.display.update()
        clock.tick(32)
def main(window,l):
    mixer.init()
    
    mixer.music.load("TitleScreen.ogg")
    mixer.music.set_volume(0.1)
    mixer.music.play(loops=-1)
    pygame.font.init() 
    font2 = pygame.font.SysFont('Comic Sans MS', 50)
    surface2 = font2.render('Paused', False, (0, 0, 0))
    #********** Game variables **********
    quit = False
    bg_image = pygame.image.load('bg.png')
    window.blit(pygame.transform.scale(bg_image, (1280, 720)), (0, 0))
    pygame.display.update()
    log = pygame.image.load('log.png')
    goal = pygame.image.load('goal2.png')
    level = l
    # sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 5)
    ground = Wall(0,SCREEN_HEIGHT-75, 5, 5, None)
    ceiling = Wall(0,-100, 5, 5, None)
    images = [log]
    targets = []
    platforms = []
    images = []
    numObjects = 0
    objectsList = []
    simulatePhysics = False
    setSideBar = False
    won = False
    #********** Start game loop **********
    while not quit:
        if(level == 1):
            if(not setSideBar):
                sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 5)
                targets = [Wall(600,300,150, 150, goal)]
                max_height = -1
                for target in targets:
                    if(target.rect.top > max_height):
                        max_height = target.rect.top
                ceiling = Wall(0,max_height, 5, 5, None)
                setSideBar=True
            platforms = [Wall(400, 550, 200,150, log)]
            images = [log]
        elif(level == 2):
            if(not setSideBar):
                sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 3)
                setSideBar = True
                targets = [Wall(875,350,150, 150, goal)]
                max_height = -1
                for target in targets:
                    if(target.rect.top > max_height):
                        max_height = target.rect.top
                ceiling = Wall(0,max_height, 5, 5, None)
            platforms = [Wall(600, 350, 200,150, log),Wall(450,450, 200,150, log), Wall(600,550, 200,150, log)]
            images = [log,log,log]
        elif(level == 3):
            if(not setSideBar):
                sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT, 3)
                setSideBar = True
                targets = [Wall(600,300,150, 150, goal),Wall(800,300,150, 150, goal)]
                max_height = -1
                for target in targets:
                    if(target.rect.top > max_height):
                        max_height = target.rect.top
                ceiling = Wall(0,max_height, 5, 5, None)
            platforms = [Wall(600, 550, 200,150, log)]
            images = [log]
        elif(level == 4):
            if(not setSideBar):
                sidebar = Sidebar(SIDEBAR_WIDTH, SCREEN_HEIGHT,3)
                setSideBar=True
                targets = [Wall(1100,400,150, 150, goal)]
                max_height = -1
                for target in targets:
                    if(target.rect.top > max_height):
                        max_height = target.rect.top
                ceiling = Wall(0,max_height, 5, 5, None)
            platforms = [Wall(600, 550, 200,150, log),Wall(600,200,200, 150, log)]
            images = [log,log]
        else:
            quit = True 
        mx, my = pygame.mouse.get_pos()
        pygame.event.pump()
        window.blit(pygame.transform.scale(bg_image, (1280, 720)), (0, 0))
        if(won):
            pygame.font.init()
            my_font = pygame.font.SysFont('Comic Sans MS', 50)
            text_surface = my_font.render('Click for next level...', False, (0, 0, 0))
            window.blit(text_surface, (SCREEN_WIDTH/2-125,50))
        if(simulatePhysics == False):
            window.blit(surface2, (SCREEN_WIDTH/2-125,50))
        for i in range(len(images)):
            window.blit(pygame.transform.scale(images[i], (platforms[i].rect.width, platforms[i].rect.height)), (platforms[i].rect.left,platforms[i].rect.top - 70))
        for i in range(len(targets)):
            window.blit(pygame.transform.scale(goal, (targets[i].rect.width, targets[i].rect.height)), (targets[i].rect.left,targets[i].rect.top - 70))
        sidebar.draw(window)
        for i in range(len(objectsList)):
            if(objectsList[i].isAtGround(ground)):
                if(objectsList[i].gravityOff == False):
                    objectsList[i].velocity[1] = 0 
                    objectsList[i].accel[1] = 0
                    objectsList[i].gravityOff = True
                else:
                    objectsList[i].accel[1] = 2
                    objectsList[i].gravityOff = False   

            if(simulatePhysics and objectsList[i].dragging == False):
                ## gravity
                if(objectsList[i].isAtGround(ground)):
                    if(objectsList[i].gravityOff == False):
                        objectsList[i].velocity[1] = 0
                        objectsList[i].accel[1] = 0
                        objectsList[i].gravityOff = True
                    objectsList[i].velocity[0] -= 0.3 * objectsList[i].velocity[0]
                else:
                    objectsList[i].accel[1] = 2
                    objectsList[i].gravityOff = False
                ## end gravity
            if(objectsList[i].isAtCeiling(ceiling)):
                objectsList[i].velocity[1] = 0
                objectsList[i].velocity[0] -= 0.3 * objectsList[i].velocity[0]
            for platform in platforms:
                if(objectsList[i].isOnPlatform(platform)):
                    if(objectsList[i].gravityOff == False):
                        objectsList[i].velocity[1] = 0
                        objectsList[i].accel[1] = 0
                        objectsList[i].gravityOff = True
                        objectsList[i].rect.bottom = platform.rect.top
                    objectsList[i].velocity[0] -= 0.3 * objectsList[i].velocity[0]
                else:
                    objectsList[i].accel[1] = 2
                    objectsList[i].gravityOff = False
            for platform in targets:
                if(objectsList[i].isOnPlatform(platform)):
                    if(objectsList[i].gravityOff == False):
                        objectsList[i].velocity[1] = 0
                        objectsList[i].accel[1] = 0
                        objectsList[i].gravityOff = True
                        objectsList[i].rect.bottom = platform.rect.top
                    objectsList[i].velocity[0] -= 0.3 * objectsList[i].velocity[0]
                else:
                    objectsList[i].accel[1] = 2
                    objectsList[i].gravityOff = False
            if(objectsList[i].isLit):
                if(objectsList[i].timer <= 0):
                    if(simulatePhysics):
                        explodeObj(objectsList, i,targets)
                        mixer.Channel(0).play(pygame.mixer.Sound("boom.ogg"))
                    won = True
                    for target in targets:
                        if(target.isExploded == False):
                            won = False

                    objectsList[i].isLit = False
                    objectsList[i].timer = -1
                    objectsList[i].exploded = True
                    objectsList[i].duration = 32
                elif(objectsList[i].timer % 20 == 0):
                    if(simulatePhysics):
                        objectsList[i].simulateExplosion(objectsList[i].timer//20)
                        objectsList[i].timer -=1
                else:
                    if(simulatePhysics):
                        objectsList[i].timer -=1
            if(objectsList[i].exploded):
                if(objectsList[i].duration <= 0):
                    objectsList[i].duration= -1
                elif(objectsList[i].duration % 8 == 0):
                    if(simulatePhysics):
                        objectsList[i].simulateAfter(objectsList[i].duration//8)
                        objectsList[i].duration -= 1
                else:
                    if(simulatePhysics):
                        objectsList[i].duration -=1
            if(simulatePhysics):
                objectsList[i].velocity[1] += objectsList[i].accel[1]
                objectsList[i].velocity[0] += objectsList[i].accel[0]
                objectsList[i].rect.center = (objectsList[i].rect.center[0] + objectsList[i].velocity[0], objectsList[i].rect.center[1] + objectsList[i].velocity[1])
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
            elif ((event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.MOUSEBUTTONUP)):
                if(won):
                    if(level < 4):
                        level +=1
                        for i in range(len(objectsList)-1, -1, -1):
                            del objectsList[i]
                        setSideBar=False
                        won = False
                    else:
                        title_screen(window)
                out = sidebar.handle_event(event,simulatePhysics)
                if(out is not None):
                    objectsList.append(out)
                for object in objectsList:
                    out = object.handle_event(event,sidebar,simulatePhysics)
                    if(out == 1):
                        break
                    if(out == 3):
                        break
            elif (event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_p):
                    simulatePhysics = (not simulatePhysics)
                    if(simulatePhysics == False):
                        max_height = -1
                        for target in targets:
                            if(target.rect.top > max_height):
                                max_height = target.rect.top
                        ceiling = Wall(0,max_height, 5, 5, None)
                    else:
                        ceiling = ceiling = Wall(0,-100, 5, 5, None)

                elif(event.key == pygame.K_r):
                    for i in range(len(objectsList)-1, -1, -1):
                        del objectsList[i]
                    setSideBar=False
                    mixer.Channel(4).set_volume(0.5)
                    mixer.Channel(4).play(pygame.mixer.Sound("reset.ogg"))
                    for target in targets: 
                        target.isExploded = False

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
        clock.tick(32)
    return -1                                  # Run the game at 25 frames per second

#********** Initialise & run the game **********
if __name__ == "__main__":                             # Set screen width,height
    pygame.init()                                       # Start graphics system
    pygame.mixer.init()                                 # Start audio system
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)   # Create window
    clock = pygame.time.Clock()                        # Create game clock
    title_screen(window)
    pygame.quit()