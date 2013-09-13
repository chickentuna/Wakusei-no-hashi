import random
import sys

WATER = 0
BRIDGE = 1
ISLAND = 2

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

    def method(self):
        pass

    def __str__(self):
        return "Grid ["+str(self.width)+","+str(self.height)+"]"

    def display(self):
        for x in range(0,self.width):
            for y in range(0,self.height):
                if (x==self.cx and y==self.cy):
                    sys.stdout.write('X')
                    continue
                n = self.nodes[x][y]
                if (n.type == WATER):
                    sys.stdout.write('-')
                elif (n.type == ISLAND):
                    sys.stdout.write(str(n.getNum()))
                else:
                    sys.stdout.write('*')
            sys.stdout.write('\n')

    def saveToFile(self,fname):
        f = open(fname+'.hashi', 'w')
        for x in range(0,self.width):
            for y in range(0,self.height):
                n = self.nodes[x][y]
                if (n.type == WATER or n.type == BRIDGE):
                    f.write('-')
                elif (n.type == ISLAND):
                    f.write(str(n.getNum()))
                #else:
                #    f.write('*')
            f.write('\n')


    def placeStartIsland(self):
        iteration = 0
        out = False

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

        '''print("dx = "+str(dx))
        print("dy = "+str(dy))'''

        tot = dist
        #print("dist = "+str(dist))

        while ok==True:
            nx = self.cx + dx
            ny = self.cy + dy

            '''print("dx = "+str(dx))
            print("dy = "+str(dy))'''

            if (self.nodes[nx][ny].type == BRIDGE):
                direction = 'h'
                if (dy == 0):
                    direction = 'v'
                if (direction != self.nodes[nx][ny].direction):
                    #print('Crosses bridge ('+direction+' v '+ self.nodes[nx][ny].direction+')')
                    #print(self.it)
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
        elif (n.type == BRIDGE):
            raise SyntaxError

        return self.connectBridge(ox,oy)
        
        '''print(dist)
        self.display()'''
        
        return True

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


def main():
    if len(sys.argv)>1:
        size = int(sys.argv[1])
    else:
        size = int(15)
    if len(sys.argv)>2:
        complexity = int(sys.argv[2])
    else:
        complexity = size*size/2
    g = Grid(size,size)
    g.placeStartIsland()
    for x in range(0,int(complexity)):    
        while not g.attachRandomIsland():
            pass
    g.display();
    g.saveToFile("out")


if __name__ == "__main__":
    main()

