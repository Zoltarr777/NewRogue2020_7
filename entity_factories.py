from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(
	char="@", 
	color=(255, 255, 255), 
	name="Player", 
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=100, defense=2, power=5),
)

limb = Actor(
	char="~", 
	color=(255, 0, 0), 
	name="Crawling Limb",
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=5, defense=0, power=3),
)

ghoul = Actor(
	char="g", 
	color=(196, 233, 223), 
	name="Ghoul", 
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=10, defense=0, power=4),
)

wraith = Actor(
	char="W", 
	color=(43, 148, 118), 
	name="Wraith", 
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=16, defense=1, power=5),
)











