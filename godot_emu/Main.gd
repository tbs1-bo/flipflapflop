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
		

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		map.position = Vector2(0, 0)
		map.scale = Vector2(1, 1)

	if event.is_action_pressed("ui_page_up"):
		map.scale.x += 1
		map.scale.y += 1
	if event.is_action_pressed("ui_page_down"):
		map.scale.x = max(1, map.scale.x - 1)
		map.scale.y = max(1, map.scale.y - 1)
