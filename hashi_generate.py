import random
import sys
from engine.hashi import randint, Grid, Node, WATER, BRIDGE, ISLAND

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

