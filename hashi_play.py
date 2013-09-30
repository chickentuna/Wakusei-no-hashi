import os.path
import pygame, sys, random
from pygame.locals import *
sys.path.append(".")
from hashi import *
import sector
from ship import Ship

display_text = True
#font=None
font_size = 20

# set up the colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

selected_node = None

#Display vars
cell_size = 50
grid_offset = (10,10)
cell_offset = (9,7)
cursor_radius = 10
cursor_width = 1

def cellCenter(pos):
    return tuple([pos[0]*cell_size+cell_size/2, pos[1]*cell_size+cell_size/2])

def vectorAdd(xs,ys):
    return tuple(x + y for x, y in zip(xs, ys))
def vectorMult(xs,ys):
    if isinstance(xs, (int,float)):
        return tuple([y * xs for y in ys])
    else:
        return tuple(x * y for x, y in zip(xs, ys))

def drawBackground(windowSurface, background):
    windowSurface.blit(background,(0,0))
    


def drawGrid(surface, grid, bridgeSurface):
    global selected_node
    if not isinstance(grid, GuessGrid):
        raise TypeError('drawGrid needs a grid')

    bridgeSurface.fill((0,0,0,0))

    for x in range(0,grid.width):
        for y in range(0,grid.height):
            n = grid.nodes[x][y]
            #pygame.draw.rect(surface, RED, Rect(vectorAdd(grid_offset, [x*cell_size,y*cell_size]),(cell_size,cell_size)))
            if (n.type == ISLAND):
                col = WHITE
                if n.getNum() == (n.up+n.left+n.right+n.down):
                    col = RED
                if n is grid.center:
                    col = GREEN
                drawString(surface, str(n.getNum()),vectorAdd(grid_offset, vectorAdd(cell_offset, [x*cell_size, y*cell_size])),col)
                drawBridges(bridgeSurface, n)

            elif (n.type == BRIDGE):
                drawBridges(bridgeSurface, n)

            if (n is selected_node):
                pygame.draw.circle(surface, RED, vectorAdd(grid_offset, cellCenter([x,y])), cursor_radius, cursor_width)
    return bridgeSurface



def drawSingleBridge(surface, x, y, coef):
    orign = vectorAdd(grid_offset, vectorAdd(cellCenter([x,y]), [cell_size*coef[0], cell_size*coef[1]]))
    desti = vectorAdd(grid_offset, vectorAdd(cellCenter([x,y]), [cell_size*coef[2], cell_size*coef[3]]))
    pygame.draw.line(surface, WHITE, orign, desti)
            
def drawFromParams(surface, x, y, params):
    options = {'up' : ([0, 0, 1/2., 0], None),
                'up2' : ([0, -1/6., 1/2., -1/6.],[0, 1/6., 1/2., 1/6.]),
                'down' : ([0, 0, -1/2., 0], None),
                'down2' : ([0, -1/6., -1/2., -1/6.],[0, 1/6., -1/2., 1/6.]),
                'right' : ([0, 0, 0, 1/2.], None),
                'right2' : ([-1/6., 0, -1/6., 1/2.],[1/6., 0, 1/6., 1/2.]),
                'left' : ([0, 0, 0, -1/2.], None),
                'left2' : ([-1/6., 0, -1/6., -1/2.],[1/6., 0, 1/6., -1/2.])
    }

    for i in range(len(params.ids)):
        for k in range(params.numbs[i]):
            drawSingleBridge(surface, x, y, options[params.ids[i]][k])


def drawBridges(surface, n):
    x = n.y
    y = n.x
    drawFromParams(surface, x, y, n.getBridgeParams())
    


def drawString(surface,string,pos,color=WHITE):
    global display_text
    if display_text:
        text=sector.font.render(string,1,color)
        surface.blit(text, pos)

def updateStatus(guess):
    global running, game_state
    guess.updateHappiness()

    if guess.checkTruth():
        running = False       #Replace with a victory alarm + input block
        game_state = 'won'



'''
   Main
   params: [size] [complexity]
'''

def main():
    global selected_node, running, game_state, display_text

    if not os.path.exists(pygame.font.get_default_font()):
        display_text = False
    
    if len(sys.argv)>1:
        size = int(sys.argv[1])
    else:
        size = 10
    if len(sys.argv)>2:
            complexity = int(sys.argv[2])
    else:
            complexity = size*size/2
    
    
    # set up pygame
    pygame.init()
    mainClock = pygame.time.Clock()
    sector.font = pygame.font.Font(pygame.font.get_default_font(),font_size)

    # set up the window
    MINSIZE = size*cell_size
    WINDOWWIDTH = MINSIZE+2*grid_offset[0]
    WINDOWHEIGHT = MINSIZE+2*grid_offset[1]+60
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
    
    '''
    uchuu = espace/univers/cosmos
    wakusei = planete
    ginga = galaxie
    '''
    pygame.display.set_caption('Wakusei no hashi')
    
    sector.visible_sprites = pygame.sprite.LayeredUpdates()

    all = pygame.sprite.Group()

    Bubble.container = all
    Bubble.images_happy = load_images('happy1.png', 'happy2.png')
    Bubble.images_sad = load_images('sad1.png', 'sad2.png')
    
    Planet.container = all
    Planet.images = load_sequence('planets/planet', Planet.planet_amount, '.png')

    Ship.container = all
    Ship.images = load_images('ships/ship1.png')


    # set up the data structures
    g = Grid(size, size)
    guess = Grid(g.width, g.height)
    g.placeStartIsland()
    for x in range(0, int(complexity)):
        iteration = 0
        while not g.attachRandomIsland():
            iteration +=1
            if iteration>size**4:
                break
    guess = GuessGrid(g)
    Ship(guess.center)

    running = True
    game_state = 'running'
    
    SCREENRECT = Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT)
    background = load_image('back.png')
    bridgeSurface = pygame.Surface(SCREENRECT.size, flags=pygame.SRCALPHA)

    # run the game loop
    while running:
        # check for events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x = (mouse_x - grid_offset[0]) / cell_size;
                y = (mouse_y - grid_offset[1]) / cell_size;
               
                if selected_node is None:
                    try :
                        n = guess.nodes[x][y]
                        if n.type == ISLAND:
                            selected_node = n
                            #Ship(selected_node)
                    except IndexError:
                        pass
                else:
                    try :
                        n = guess.nodes[x][y]
                    except IndexError:
                        n = None
    
                    if (not n is None) and (n.type == ISLAND):
                        relation = guess.nodeRelations(n, selected_node)
                        print relation
    
                        if relation == 'connectable':
                            guess.connectNodes(n, selected_node)
                            selected_node = None
                        else:
                            if relation == 'saturated port':
                                guess.disconnectNodes(n, selected_node)
                                selected_node = None
                            elif relation == 'saturated':
                                guess.connectNodes(n, selected_node)
                                selected_node = None
                            else:
                                selected_node = n
                        updateStatus(guess)
                    else:
                        selected_node = None
    
        # draw the black background onto the surface
        drawBackground(windowSurface, background)        
        
        windowSurface.blit(bridgeSurface, (0,0))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        x = (mouse_x - grid_offset[0]) / cell_size;
        y = (mouse_y - grid_offset[1]) / cell_size;
               
        
        drawString(windowSurface, str((x,y)),(20, WINDOWHEIGHT-60))
        
        all.update()
        sector.visible_sprites.draw(windowSurface)
        bridgeSurface = drawGrid(windowSurface, guess, bridgeSurface)
        pygame.display.update()
        mainClock.tick(40)
    
    if game_state == 'won':
        print 'Solution found'
    elif game_state == 'running':
        print 'Invalid game state'

    running = True
    while running:
        # check for events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        mainClock.tick(40)

if __name__ == "__main__":
    main()