import engine.sector as sector
import random, sys
import inspect
import hashi_play
from engine.ship import Ship
from engine.hashi_load import *

WATER = 0
BRIDGE = 1
ISLAND = 2

planet_speed = 10

class Happy(object):
    yes = 0
    neutral = 1
    no = 2

#FAKE_SEED = 0
def randint(b, e):
    #v = [10,10,0,8,1,10]
    #global FAKE_SEED
    #res = v[FAKE_SEED]
    #FAKE_SEED+=1
    res = random.randint(b,e)
    return res

class Grid(object):
    def __init__(self, w, h):
        self.width = w;
        self.height = h;
        self.nodes = [[Node() for x in range(w)] for x in range(h)]
        self.cx = 0
        self.cy = 0
        self.it = 0
        self.icount = 0

    def __str__(self):
        return "Grid ["+str(self.width)+","+str(self.height)+"]"

    def as_string(self, show_solution = False, show_start = False):
        result = ''
        for x in range(0,self.width):
            for y in range(0,self.height):
                if (show_start and x==self.cx and y==self.cy):
                    result += 'X'
                    continue
                n = self.nodes[x][y]
                if (n.type == WATER or n.type == BRIDGE and not show_solution):
                    result += '-'
                elif (n.type == ISLAND):
                    result += str(n.getNum())
                else:
                    result += '*'
                
            result += '\n'
        return result

    def display(self):
        print(self.as_string(True))

    def saveToFile(self,fname):
        f = open(fname+'.hashi', 'w')
        f.write(self.as_string())

    def placeStartIsland(self):
        iteration = 0
        out = False
        self.icount = 1
        while (not out):
            iteration += 1
            x = randint(0,self.width-1)
            y = randint(0,self.height-1)
            n = self.nodes[x][y]
            if (n.type == WATER):
                    n.type = ISLAND
                    self.cx = x
                    self.cy = y
                    out = True
            if (iteration >200):
                out = True

    def connectBridge(self,x,y):
        a = self.nodes[x][y]
        b = self.nodes[self.cx][self.cy]
        if (a.type != ISLAND or b.type != ISLAND):
            return False
        
        dx=0
        dy=0

        if self.cx > x:
            if (a.right < 2 and b.left < 2):
                a.right += 1
                b.left += 1
                dx=1
            else:
                return False
        elif self.cx < x:
            if (b.right < 2 and a.left < 2):
                b.right += 1
                a.left += 1
                dx=-1
            else:
                return False
        elif self.cy < y:
            if (a.down < 2 and b.up < 2):
                a.down += 1
                b.up += 1 
                dy=-1
            else:
                return False  
        elif self.cy > y:
            if (b.down < 2 and a.up < 2):
                b.down += 1
                a.up += 1
                dy=1
            else:
                return False
        else:
            return False

        x+=dx
        y+=dy
        while x!=self.cx or y!=self.cy:
            self.nodes[x][y].type = BRIDGE
            self.nodes[x][y].bridges+=1
            if (x==self.cx):
                self.nodes[x][y].direction = 'h'
            x+=dx
            y+=dy
        return True
        
    def attachRandomIsland(self):
        if self.it >= 8000:
            return True


        direction = randint(0,3)
        ok = False
        ox = self.cx
        oy = self.cy
        dx = 0
        dy = 0

        if (direction==0 and self.cy>0):
            dist = randint(1,self.cy)
            dy = -1
            ok = True

        if (direction==1 and self.cy<self.height-1):
            dist = randint(1,self.height - self.cy-1)
            dy = 1
            ok = True

        if (direction==2 and self.cx>0):
            dist = randint(1,self.cx)
            dx = -1
            ok = True
        if (direction==3 and self.cx<self.width-1):
            dist = randint(1,self.width - self.cx-1)
            dx = 1
            ok = True

        if (ok==False):
            return False

        tot = dist
        #print("dist = "+str(dist))

        while ok==True:
            nx = self.cx + dx
            ny = self.cy + dy

            if (self.nodes[nx][ny].type == BRIDGE):
                direction = 'h'
                if (dy == 0):
                    direction = 'v'
                if (direction != self.nodes[nx][ny].direction):
                    self.it+=1
                    ok=False
                else:
                    self.cx = nx
                    self.cy = ny
            else:
                self.cx = nx
                self.cy = ny
            
            if self.nodes[nx][ny].type == ISLAND:
                ok = False
                
            tot-=1
            if tot<=0 and self.nodes[nx][ny].type == WATER:
                self.it = 0
                ok=False

        if self.cx == ox and self.cy == oy:
            return False
            
        n = self.nodes[self.cx][self.cy]

        if (n.type == WATER):
            self.nodes[self.cx][self.cy].type = ISLAND
            self.icount +=1
        elif (n.type == BRIDGE):
            raise SyntaxError

        return self.connectBridge(ox,oy)
        
class Node(object):
    def __init__(self):
        self.type = WATER
        self.bridges = 0
        self.direction = 'v'
        self.up = 0
        self.left = 0
        self.right = 0
        self.down = 0
         

    def getNum(self):
        return self.up + self.left + self.right + self.down
    
    def __str__(self):
        if (self.type == ISLAND):
            return "<"+str(self.down)+"O"+str(self.up)+">"+"^"+str(self.left)+"V"+str(self.right)
        else:
            return "-"

    def __repr__(self):
        return self.__str__()

class GuessGrid(object):
    def __init__(self, grid):
        self.truth = grid
        self.width = grid.width;
        self.height = grid.height;
        self.nodes = [[GuessNode(grid.nodes[x][y], x, y) for x in range(self.width)] for y in range(self.height)]
        self.center = self.getRandomIsland()

    def getRandomIsland(self):
        n = randint(1,self.truth.icount)
        count = 0
        for row in self.nodes:
                for node in row:
                    if node.type == ISLAND:
                        count+=1
                        if count == n:
                            return node
        raise Exception('Could not find an island in grid\n> count='+str(count)+'\n  n='+str(n)+'\n  icount='+str(self.truth.icount))

    def updateHappiness(self, node=None):
        if node is None :
            for row in self.nodes:
                for n in row:
                    n.flooded = False
            self.updateHappiness(self.center)
            for row in self.nodes:
                for n in row:
                    if n.getNum() < (n.up+n.left+n.right+n.down):
                        n.happiness = Happy.no
                    else:
                        n.happiness = Happy.neutral
                        if n.flooded == True and n.getNum() == (n.up+n.left+n.right+n.down):
                            n.happiness = Happy.yes
            self.center.happiness = Happy.yes
        else:
            if node.flooded == False:
                node.flooded = True
                neighbours = []
                if node.up > 0:
                    neighbours += [self.getNextIsland(node.x, node.y,v=1)]
                if node.down > 0:
                    neighbours += [self.getNextIsland(node.x, node.y,v=-1)]
                if node.left > 0:
                    neighbours += [self.getNextIsland(node.x, node.y,h=-1)]
                if node.right > 0:
                    neighbours += [self.getNextIsland(node.x, node.y,h=1)]
                for pos in neighbours :
                    self.updateHappiness(pos)

        '''
        On screen up == node logic left
        On screen down == node logic right
        On screen left == node logic down
        On screen right == node logic up
    
        And then inverted x & y for nodes table
        '''

    def getNextIsland(self,x,y,h=0,v=0):
        nx = x
        ny = y
        found = False

        while not found:
            nx += h
            ny += v
            n = self.nodes[ny][nx]
            if n.type == ISLAND:
                return n


    def checkTruth(self):
        for array in self.nodes:
            for node in [n for n in array if n.type == ISLAND]:
                if node.happiness != Happy.yes:
                    return False
        return True

    def nodesConnectable(self,n1,n2):
        return True
        #TODO: incorporate force connections
        #if self.nodeRelations(n1,n2) == 'connectable':
        #    return True
        #else:
        #    return False
    
    def disconnectNodes(self, n1, n2):
        a = n2
        b = n1
        x = n2.x
        y = n2.y
        cx = n1.x
        cy = n1.y

        dx=0
        dy=0

        if cx > x:
            a.right = 0
            b.left = 0
            dx=1
        elif cx < x:
            b.right = 0
            a.left = 0
            dx=-1
        elif cy < y:
            a.down = 0
            b.up = 0
            dy=-1
        elif cy > y:
            b.down = 0
            a.up = 0
            dy=1
            
        x+=dx
        y+=dy
        it = 0
        while x!=cx or y!=cy:
            it +=1
            if it > 800:
                raise Exception('Overiterate safeguard error')
            cur = self.nodes[y][x]
            if cur.type == BRIDGE:
                cur.bridges=0
                cur.type = WATER
            x+=dx
            y+=dy
    
        return True

    def connectNodes(self, n1, n2):
        if not self.nodesConnectable(n1, n2):
            return False
        else:
            a = n2
            b = n1
            x = n2.x
            y = n2.y
            cx = n1.x
            cy = n1.y

            dx=0
            dy=0
    
            if cx > x:
                if (a.right < 2 and b.left < 2):
                    a.right += 1
                    b.left += 1
                    dx=1
            elif cx < x:
                if (b.right < 2 and a.left < 2):
                    b.right += 1
                    a.left += 1
                    dx=-1
            elif cy < y:
                if (a.down < 2 and b.up < 2):
                    a.down += 1
                    b.up += 1 
                    dy=-1
            elif cy > y:
                if (b.down < 2 and a.up < 2):
                    b.down += 1
                    a.up += 1
                    dy=1
            
            x+=dx
            y+=dy
            it = 0
            while x!=cx or y!=cy:
                it +=1
                if it > 800:
                    raise Exception('Overiterate safeguard error')

                self.nodes[y][x].type = BRIDGE
                self.nodes[y][x].bridges+=1
                if (x==cx):
                    self.nodes[y][x].direction = 'h'
                else:
                    self.nodes[y][x].direction = 'v'
                x+=dx
                y+=dy
    
            return True

    def nodeRelations(self, n1, n2):
        x1 = n1.x
        y1 = n1.y
        x2 = n2.x
        y2 = n2.y

        _equals = 'equals'
        _outOfReach = 'out of reach'
        _connectable = 'connectable'
        _blockedByIsland = 'blocked by island'
        _blockedByBridge = 'blocked by bridge'
        _saturatedPort = 'saturated port'
        _saturated = 'saturated'


        if (n1 is n2):
            return _equals

        dx=0
        dy=0
        not_enough_ports = False
        if x2 > x1:
            dx=1
            if not (n1.right < 2 and n2.left < 2):
                not_enough_ports = True
        elif x2 < x1:
            dx=-1
            if not (n2.right < 2 and n1.left < 2):
                not_enough_ports = True

        if y2 < y1:
            dy=-1
            if not (n1.down < 2 and n2.up < 2):
                not_enough_ports = True  
        elif y2 > y1:
            dy=1
            if not (n2.down < 2 and n1.up < 2):
                not_enough_ports = True


        if dx != 0 and dy != 0:
            return _outOfReach

        saturated = False
        if n1.getNum() <= n1.up + n1.down + n1.right + n1.left:
            saturated = True
        if n2.getNum() <= n2.up + n2.down + n2.right + n2.left:
            saturated = True

        ok = True
        cx = x1
        cy = y1

        it = 0
        
        while ok==True:
            it +=1

            nx = cx + dx
            ny = cy + dy

            if (self.nodes[ny][nx].type == BRIDGE):
                direction = 'h'
                if (dy == 0):
                    direction = 'v'
                #if (direction != self.nodes[ny][nx].direction) or self.nodes[ny][nx].bridges == 2 :
                if (direction != self.nodes[ny][nx].direction):
                    return _blockedByBridge
                else:
                    cx = nx
                    cy = ny
            else:
                cx = nx
                cy = ny

            if self.nodes[ny][nx].type == ISLAND:
                
                if nx == x2 and ny == y2:
                    if not_enough_ports:
                        return _saturatedPort
                    elif saturated:
                        return _saturated
                    else:
                        return _connectable
                else:
                    return _blockedByIsland
            if it > 600:
                ok = False
        
        raise Exception('Overiterate safeguard error')

def rotozoom_center(image, rect, angle, scale=1):
        """rotate an image while keeping its center"""
        rot_image = pygame.transform.rotozoom(image, angle, scale)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image,rot_rect
       
class Planet(pygame.sprite.DirtySprite):
    images = []
    planet_amount = 6

    def __init__(self, node):
        pygame.sprite.DirtySprite.__init__(self)
        self.node = node
        self.image_init = self.images[randint(0,self.planet_amount-1)]
        self.image = self.image_init
        self.add(self.container)
        planet_offset = hashi_play.grid_offset
        planet_pos = hashi_play.cellCenter([node.y,node.x])
        self.rect = self.image_init.get_rect(center = hashi_play.vectorAdd(planet_offset, planet_pos))
        self.frame = 0
        sector.visible_sprites.add(self)
        self.slowliness = randint(20,200)
        if randint(0,1) == 1:
            self.slowliness *=-1
        #self.dirty = 2

    def update(self):
        self.frame += 1 * planet_speed
        self.image,self.rect = rotozoom_center(self.image_init, self.rect, self.frame/self.slowliness, .2)
        #hashi_play.drawString(self.image, str(self.node.getNum()),hashi_play.cell_offset)


class Bubble(pygame.sprite.DirtySprite):
    animcycle = 6
    subSprites = 2
    images_happy = []
    images_sad = []

    def __init__(self, node):
        pygame.sprite.DirtySprite.__init__(self)
        self.node = node
        self.ships = []
        self.images = self.images_happy
        self.image = self.images[0]
        self.frame = 0
        self.add(Bubble.container)
        bubble_offset = hashi_play.vectorAdd([0,-hashi_play.cell_size/2],hashi_play.grid_offset)
        bubble_pos = hashi_play.cellCenter([node.y,node.x])
        self.rect = self.image.get_rect(center = hashi_play.vectorAdd(bubble_offset, bubble_pos))
        
    def show(self, visible):
        self.visible = visible
        if visible==1:
            sector.visible_sprites.add(self)
        else:
            sector.visible_sprites.remove(self)

    def spawnShips(self):
        self.ships.append(Ship(self.node))

    def update(self):

        if (self.node.happiness == Happy.no) and (self.visible == 0):
            self.show(1)
        elif (self.node.happiness == Happy.yes) and self.visible == 0:
            self.show(1)
            #self.spawnShips()            
        elif (self.node.happiness == Happy.neutral) and self.visible == 1:
            self.show(0)
            for ship in self.ships:
                ship.comeHome();
            self.ships = []

        if (self.images is self.images_happy):
            if (self.node.happiness != Happy.yes):
                self.images = self.images_sad
                for ship in self.ships:
                    ship.comeHome();
                self.ships = []
        elif (self.node.happiness != Happy.no and self.visible==1):
                if self.images != self.images_happy:
                    self.spawnShips()
                self.images = self.images_happy

        if (self.visible == 1):
            self.frame+=1
            self.image = self.images[self.frame//self.animcycle%self.subSprites]
        
class GuessNode(object):
    def __init__(self, node, x, y):
        self.x = x
        self.y = y
        if node.type == ISLAND:
            self.type = node.type
        else:
            self.type = WATER
        self.bridges = 0
        self.direction = 'h'
        self.up = 0
        self.left = 0
        self.right = 0
        self.down = 0
        self.node = node
        
        if self.type == ISLAND:
            self.happiness = Happy.neutral;
            self.flooded = False
            self.planet = Planet(self)
            self.bubble = Bubble(self)
    
    def __repr__(self):
        return str(self.x)+","+str(self.y)

    def checkTruth(self):
        if not self.up == self.node.up:
            return False
        if not self.left == self.node.left:
            return False
        if not self.right == self.node.right:
            return False
        if not self.down == self.node.down:
            return False
        return True


    def getNum(self):
        return self.node.getNum()

    class Params(object):
        def __init__(self):
            self.ids = []
            self.numbs = []
            
    def generateParam(self, var, name, way, res):
        if var==1 or (self.bridges == 1 and self.direction == way):
            res.ids += [name]
            res.numbs += [1]
        elif var==2 or (self.bridges == 2 and self.direction == way):
            res.ids += [name+'2']
            res.numbs += [2]

    def getBridgeParams(self):
        res = self.Params()

        self.generateParam(self.up, 'up', 'h', res)
        self.generateParam(self.down, 'down', 'h', res)
        self.generateParam(self.right, 'right', 'v', res)
        self.generateParam(self.left, 'left', 'v', res)

        return res







