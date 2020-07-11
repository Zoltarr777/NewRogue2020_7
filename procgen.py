from __future__ import annotations
from typing import Iterator, Tuple, List, TYPE_CHECKING
import random
import entity_factories
from game_map import GameMap
import tile_types
import tcod
import numpy as np
import scipy.signal
import time
from connect_map import connect_map

if TYPE_CHECKING:
	from engine import Engine
	from entity import Entity

class RectangularRoom:
	def __init__(self, x: int, y: int, width: int, height: int):
		self.x1 = x
		self.y1 = y
		self.x2 = x + width
		self.y2 = y + height

	@property
	def center(self) -> Tuple[int, int]:
		center_x = int((self.x1 + self.x2) / 2)
		center_y = int((self.y1 + self.y2) / 2)

		return center_x, center_y

	@property
	def inner(self) -> Tuple[slice, slice]:
		#Return the inner area of this room as a 2D array index

		return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

	def intersects(self, other: RectangularRoom) ->bool:
		#Returns true if this room overlaps with another
		return (
			self.x1 <= other.x2
			and self.x2 >= other.x1
			and self.y1 <= other.y2
			and self.y2 >= other.y1
		)

def place_entities(
	room: RectangularRoom, dungeon: GameMap, maximum_monsters: int,
) -> None:
	number_of_monsters = random.randint(0, maximum_monsters)

	for i in range(number_of_monsters):
		x = random.randint(room.x1 + 1, room.x2 - 1)
		y = random.randint(room.y1 + 1, room.y2 - 1)

		if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
			if random.random() < 0.4:
				entity_factories.ghoul.spawn(dungeon, x, y)
			elif 0.4 < random.random() < 0.9:
				entity_factories.limb.spawn(dungeon, x, y)
			else:
				entity_factories.wraith.spawn(dungeon, x, y)


def tunnel_between(
	start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
	#Return L-shaped tunnel between these points
	x1, y1 = start
	x2, y2 = end
	if random.random() < 0.5: #50% chance
		#move horizontally then vertically
		corner_x, corner_y = x2, y1
	else:
		#move vertically, then horizontally
		corner_x, corner_y = x1, y2

	#generate coordinates for the tunnel
	for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
		yield x, y
	for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
		yield x, y


def generate_dungeon(
	max_rooms: int,
	room_min_size: int,
	room_max_size: int,
	map_width: int,
	map_height: int,
	max_monsters_per_room: int,
	engine: Engine,
) -> GameMap:

	player = engine.player
	#Fill map area with floor tiles
	dungeon = GameMap(engine, map_width, map_height, entities=[player])

	rooms: List[RectangularRoom] = []

	for r in range(max_rooms):
		#randomize room sizes within bounds
		room_width = random.randint(room_min_size, room_max_size)
		room_height = random.randint(room_min_size, room_max_size)

		#randomize room coordinates within bounds
		x = random.randint(0, dungeon.width - room_width - 1)
		y = random.randint(0, dungeon.height - room_height - 1)

		#carve out room at location
		new_room = RectangularRoom(x, y, room_width, room_height)

		#if room intersects with another room, skip this one
		if any(new_room.intersects(other_room) for other_room in rooms):
			continue

		#set room tiles to floor
		dungeon.tiles[new_room.inner] = tile_types.floor

		center_of_last_room_x, center_of_last_room_y = new_room.center

		#set player spawn point
		if len(rooms) == 0:
			player.place(*new_room.center, dungeon)
		else:
			for x, y in tunnel_between(rooms[-1].center, new_room.center):
				dungeon.tiles[x, y] = tile_types.floor

		place_entities(new_room, dungeon, max_monsters_per_room)

		#add rooms to list
		rooms.append(new_room)

	return dungeon


def place_entities_in_cave(cave_map: GameMap, maximum_monsters: int) -> None:
	min_monsters_per_cave = int(maximum_monsters / 3)
	number_of_monsters = random.randint(min_monsters_per_cave, maximum_monsters)

	for i in range(number_of_monsters):
		x = random.randint(1, cave_map.width - 1)
		y = random.randint(1, cave_map.height - 1)

		while cave_map.tiles[x][y] == tile_types.wall:
			x = random.randint(1, cave_map.width - 1)
			y = random.randint(1, cave_map.height - 1)

		if not any(entity.x == x and entity.y == y for entity in cave_map.entities):
			if random.random() < 0.4:
				entity_factories.ghoul.spawn(cave_map, x, y)
			elif 0.4 < random.random() < 0.9:
				entity_factories.limb.spawn(cave_map, x, y)
			else:
				entity_factories.wraith.spawn(cave_map, x, y)


def print_cave_to_terminal(matrix):

	WALL = 0
	FLOOR = 1

	cave_str = ""
	
	for j in range(matrix.shape[1]):
		for i in range(matrix.shape[0]):
			char = "#" if matrix[i][j] == WALL else "."
			#print(char, end='')
			cave_str += char

		#print()
		cave_str += "\n"
	print(cave_str)

def generate_cave_map(
	map_width: int, 
	map_height: int, 
	max_monsters_per_cave: int, 
	engine: Engine,
):

	player = engine.player

	cave_map = GameMap(engine, map_width, map_height, entities=[player])

	new_map = np.ones((cave_map.width, cave_map.height), dtype=np.uint8, order="F")

	print("\nInitialization")
	print("Fill map with floor tiles . . .")
	print_cave_to_terminal(new_map)
	time.sleep(0.75)

	WALL = 0
	FLOOR = 1
	fill_prob = 0.45
	generations = 7
	lower_bound = 5
	upper_bound = 7
	clear_floor_val = 5

	for i in range(cave_map.width):
		for j in range(cave_map.height):
			choice = random.uniform(0, 1)
			new_map[i][j] = WALL if choice < fill_prob else FLOOR

	print("\nGeneration: 0")
	print("Fill map with {0}% wall tiles . . .".format(fill_prob * 100))
	print_cave_to_terminal(new_map)
	time.sleep(0.75)

	for generation in range(generations):
		for i in range(cave_map.width):
			for j in range(cave_map.height):
				submap = new_map[max(i - 1, 0):min(i + 2, new_map.shape[0]), max(j - 1, 0):min(j + 2, new_map.shape[1])]
				wallcount_1away = len(np.where(submap.flatten() == WALL)[0])
				submap = new_map[max(i - 2, 0):min(i + 3, new_map.shape[0]), max(j - 2, 0):min(j + 3, new_map.shape[1])]
				wallcount_2away = len(np.where(submap.flatten() == WALL)[0])

				if generation < (generations - 4): # if gen is 3 or less
					if wallcount_1away >= lower_bound or wallcount_2away <= upper_bound:
						new_map[i][j] = WALL
					else:
						new_map[i][j] = FLOOR

				elif generation == (generations - 4): # if gen is 4
					if wallcount_1away >= clear_floor_val:
						new_map[i][j] = WALL
					else:
						new_map[i][j] = FLOOR

				elif generation == (generations - 3): # if gen is 5
					if wallcount_1away == 1:
						new_map[i][j] = FLOOR

				elif generation == (generations - 2): # if gen is 7
					if i == 0 or j == 0 or i == cave_map.width - 1 or j == cave_map.height - 1:
						new_map[i][j] = WALL

				elif generation == (generations - 1): # if gen is 6
					if wallcount_1away >= 7:
						new_map[i][j] = WALL

		if generation < (generations - 4): # if gen is 2 or less
			print("\nGeneration: " + str(generation + 1))
			print("Run Cellular Automata 4/7 Rule . . .")
			print_cave_to_terminal(new_map)
			time.sleep(0.75)
		
		elif generation == (generations - 4): # if gen is 3
			print("\nGeneration: " + str(generation + 1))
			print("Clean up tiles in open areas to turn into caves . . .")
			print_cave_to_terminal(new_map)
			time.sleep(0.75)
		
		elif generation == (generations - 3): # if gen is 4
			print("\nGeneration: " + str(generation + 1))
			print("Turn any single point wall tiles into floor . . .")
			print_cave_to_terminal(new_map)
			time.sleep(0.75)

		elif generation == (generations - 2): # if gen is 5
			print("\nGeneration: " + str(generation + 1))
			print("Make a boundary around the map . . .")
			print_cave_to_terminal(new_map)
			time.sleep(0.75)

		elif generation == (generations - 1): # if gen is 6
			print("\nGeneration: " + str(generation + 1))
			print("Turn any single or double floor tiles into walls . . .")
			print_cave_to_terminal(new_map)
			time.sleep(0.75)

	connect_map(new_map, cave_map.width, cave_map.height)
	print("\nGeneration: " + str(generations + 1))
	print("Connect all separated caves together . . .")
	print_cave_to_terminal(new_map)
	time.sleep(0.75)

	print("\nCave map generation complete.")

	cave_map.tiles = np.where(new_map, tile_types.floor, tile_types.wall)

	player_x = random.randint(1, cave_map.width - 1)
	player_y = random.randint(1, cave_map.height - 1)

	while cave_map.tiles[player_x][player_y] == tile_types.wall:
		player_x = random.randint(1, cave_map.width - 1)
		player_y = random.randint(1, cave_map.height - 1)

	player.place(player_x, player_y, cave_map)

	place_entities_in_cave(cave_map, max_monsters_per_cave)

	return cave_map

