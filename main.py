import sys, os, pygame

from worldgen import world
from rendering import camera

pygame.init()

screenresolution = [16*64,9*64]
cameraresolution = [64*8,36*8]
maxfps = 180

screen = pygame.display.set_mode(screenresolution)

sprites = {}
for file in os.listdir("Sprites"):
    if file.endswith(".png"):
        name = file.split(".")[0]
        sprites[name] = pygame.image.load("Sprites\\"+file).convert()

sprites["selected"] = pygame.image.load("Sprites\\"+"selected.png").convert_alpha()

maincamera = camera(cameraresolution, screenresolution)
mainworld = world(1)
clock = pygame.time.Clock()




#mainworld.generatechunk((0,0))
while True:
    dt = clock.tick(maxfps) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        #maincamera.eventprocess(event)

    #io
    keys = pygame.key.get_pressed()
    mousepos = pygame.mouse.get_pos()


    #camera functions
    
    maincamera.move(keys,dt)
    maincamera.zooming(keys,dt)
    maincamera.selected(mousepos)
    #maincamera.update(dt)



    # world gen  
    if keys[pygame.K_SPACE]:
        camerachunks = maincamera.chunkpos()
        for chunk in camerachunks:
            if not chunk in mainworld.map:
                pos = chunk.split(".")
                pos[0]= int(pos[0])
                pos[1]= int(pos[1])
                #print(f"[WORLD] CREATED NEW CHUNK AT ({pos[0]},{pos[1]})")
                mainworld.generatechunk(pos)

    #maincamera.pos[0] += 1
    screen.fill((230,230,230))
    render = maincamera.render(mainworld.map,sprites)


    pygame.transform.scale(render, screenresolution, screen)
    pygame.display.flip()
    