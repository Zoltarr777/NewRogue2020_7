from DisjointSet import DisjointSet

from random import randrange

import tile_types



FLOOR = 1
WALL = 0

def _join_adjacent_tiles(x, y, game_map, ds):

    directions = [-1, 0, 1]

    for i in directions:

        for j in directions:

            if game_map[x+i][y+j] == FLOOR:
                if (i != 0) or (j != 0):

                    root = ds.find((x, y))

                    current = (x+i, y+j)

                    ds.union(root, ds.find(current))



def _create_sets(game_map, width, height):

    ds = DisjointSet()

    for x in range(0, width):

        for y in range(0, height):

            if game_map[x][y] == FLOOR:
                ds.find((x, y))

                _join_adjacent_tiles(x, y, game_map, ds)

    return ds

                

                

def _tunnel(pt1, pt2, game_map, ds):

    current_pt = pt1

    while ds.find(current_pt) != ds.find(pt2):

        direction = [pt2[0]-current_pt[0], pt2[1]-current_pt[1]]

        for i in [0, 1]:

            direction[i] = min(max(-1, direction[i]), 1)

        rand = randrange(0, 3)
        if rand == 0:
            direction[0] = 0
        elif rand == 1:
            direction[1] = 0

        current_pt = (current_pt[0] + direction[0], current_pt[1] + direction[1])
        x = current_pt[0]
        y = current_pt[1]

        if game_map[int(x)][int(y)] == FLOOR:

            root1 = ds.find(pt1)

            root2 = ds.find(current_pt)

            if root1 != root2:

                ds.union(root1, root2)

                return

        else:

            game_map[int(x)][int(y)] = FLOOR

            ds.union(ds.find(pt1), current_pt)

       

    



def connect_map(game_map, width, height):

    ds = _create_sets(game_map, width, height)

    center = (width/2, height/2)

    roots = ds.split_sets().keys()

    for root in roots:

        _tunnel(root, center, game_map, ds)
