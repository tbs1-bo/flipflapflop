extends Node2D

var tmap: TileMap
const STEP_SIZE = 50  # pixels

# Called when the node enters the scene tree for the first time.
func _ready():
	tmap = $Map/TileMap
	var err = get_tree().connect("screen_resized", self, "_on_screen_resized")
	if err != OK:
		printerr("Unable to connect")

func _on_screen_resized():
	$Label.visible = true

	var map = $Map
	var w = map.width
	var h = map.height
	$Label.text = "size: %s x %s" % [w, h]
	
	$TimerHideLabel.start()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if Input.is_action_pressed('ui_left'):
		tmap.position.x -= STEP_SIZE * delta
	if Input.is_action_pressed('ui_right'):
		tmap.position.x += STEP_SIZE * delta
	if Input.is_action_pressed('ui_up'):
		tmap.position.y -= STEP_SIZE * delta
	if Input.is_action_pressed('ui_down'):
		tmap.position.y += STEP_SIZE * delta

func _input(event):
	if event.is_action_pressed('ui_select') or event is InputEventMouseButton:
		$Config.visible = true
		
	if event.is_action_pressed("ui_cancel"):
		tmap.position = Vector2(0, 0)
		tmap.scale = Vector2(1, 1)

	if event.is_action_pressed("ui_page_up"):
		tmap.scale += Vector2(1, 1)
	if event.is_action_pressed("ui_page_down"):
		tmap.scale = Vector2(max(1, tmap.scale.x - 1), 
							 max(1, tmap.scale.y - 1))

func _on_Timer_timeout():
	$Label.visible = false
