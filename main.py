import tcod
import copy
import entity_factories
import color
from engine import Engine
from procgen import generate_dungeon, generate_cave_map
from random import randint

try:
	map_type = int(input("What map type do you want?\n(1 (rooms) or 2 (caves))\n>"))
except:
	print("Error: Input not an interger. Rooms selected . . .")
	map_type = 1

if map_type not in (1, 2):
	print("Error: Input not valid. Caves selected . . .")
	map_type = 1

def main() -> None:
	screen_width = 80
	screen_height = 50

	map_width = screen_width
	map_height = screen_height - 7

	room_max_size = 10
	room_min_size = 6
	max_rooms = 100

	max_monsters_per_room = 2
	max_monsters_per_cave = 30

	#tileset = tcod.tileset.load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
	tileset = tcod.tileset.load_tilesheet("terminal32x32.png", 16, 16, tcod.tileset.CHARMAP_CP437)

	
	player = copy.deepcopy(entity_factories.player)
	engine = Engine(player=player)

	if map_type == 1:
		engine.game_map = generate_dungeon(
			max_rooms=max_rooms,
			room_min_size=room_min_size,
			room_max_size=room_max_size,
			map_width=map_width,
			map_height=map_height,
			max_monsters_per_room=max_monsters_per_room,
			engine=engine,
		)
		engine.update_fov()

	elif map_type == 2:
		engine.game_map = generate_cave_map(
			map_width=map_width,
			map_height=map_height,
			max_monsters_per_cave=max_monsters_per_cave,
			engine=engine,
		)
		engine.update_fov()

	engine.message_log.add_message(
		"Welcome adventurer, to a new dungeon!", color.welcome_text
	)

	with tcod.context.new_terminal(
		screen_width,
		screen_height,
		tileset=tileset,
		title="New Roguelike 2020 Version 2",
		vsync=True,
	) as context:
		root_console = tcod.Console(screen_width, screen_height, order="F")
		while True:
			root_console.clear()
			engine.event_handler.on_render(console=root_console)
			context.present(root_console)
			
			engine.event_handler.handle_events(context)


if __name__ == "__main__":
	main()


