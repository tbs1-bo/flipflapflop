extends Node2D

# Declare member variables here. Examples:
# var a = 2
# var b = "text"

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func _input(event):
	if event is InputEventMouse:
		#print(event)
		var mousepos = event.position
		var mappos = $TileMap.world_to_map(mousepos)
		print("world %s \t map %s" % [mousepos, mappos])
		
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
