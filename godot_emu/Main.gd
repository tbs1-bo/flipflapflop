extends Node2D

var tmap: TileMap
var lbl: Label
const STEP_SIZE = 5  # pixels

# Called when the node enters the scene tree for the first time.
func _ready():
	print('starting')
	tmap = get_node("Map/TileMap")
	lbl = get_node("Label")
	get_tree().connect("screen_resized", self, "_on_screen_resized")

func _on_screen_resized():
	lbl.visible = true

	var map = get_node("Map")
	var w = map.width
	var h = map.height
	lbl.text = "size: %s x %s" % [w, h]
	get_node("TimerHideLabel").start()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if Input.is_action_pressed('ui_left'):
		tmap.position.x -= STEP_SIZE
	if Input.is_action_pressed('ui_right'):
		tmap.position.x += STEP_SIZE
	if Input.is_action_pressed('ui_up'):
		tmap.position.y -= STEP_SIZE
	if Input.is_action_pressed('ui_down'):
		tmap.position.y += STEP_SIZE

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		tmap.position = Vector2(0, 0)
		tmap.scale = Vector2(1, 1)

	if event.is_action_pressed("ui_page_up"):
		tmap.scale.x += 1
		tmap.scale.y += 1
	if event.is_action_pressed("ui_page_down"):
		tmap.scale.x = max(1, tmap.scale.x - 1)
		tmap.scale.y = max(1, tmap.scale.y - 1)


func _on_Timer_timeout():
	lbl.visible = false
