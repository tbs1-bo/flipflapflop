extends Node2D

var map: TileMap
const STEP_SIZE = 5

# Called when the node enters the scene tree for the first time.
func _ready():
	print('starting')
	map = get_node("Map/TileMap")
	

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if Input.is_action_pressed('ui_left'):
		#print('left')
		map.position.x -= STEP_SIZE
	if Input.is_action_pressed('ui_right'):
		#print('right')
		map.position.x += STEP_SIZE
	if Input.is_action_pressed('ui_up'):
		map.position.y -= STEP_SIZE
	if Input.is_action_pressed('ui_down'):
		map.position.y += STEP_SIZE