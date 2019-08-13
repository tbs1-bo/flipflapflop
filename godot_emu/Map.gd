extends Node2D

var width
var height
var tilemap
var server

const PORT = 10101

const YELLOW = 49  # ascii 1

# Called when the node enters the scene tree for the first time.
func _ready():
	tilemap = $TileMap

	init_width_height()
	clear_display()

	print("listening on port ", PORT)
	server = TCP_Server.new()
	server.listen(PORT)

func init_width_height():
	var screen_size = get_viewport_rect().size
	width = int(screen_size.x / (tilemap.cell_size.x * tilemap.scale.x))
	height = int(screen_size.y / (tilemap.cell_size.y * tilemap.scale.y))
	
func clear_display():
	for x in range(width):
		for y in range(height):
			tilemap.set_cell(x, y, 0)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if server.is_connection_available():
		var conn = server.take_connection()
		var bs = conn.get_data(conn.get_available_bytes())
		process_bytes(bs[1])
		

func process_bytes(bytes):
	var x = 0
	var y = 0
	
	for b in bytes:
		tilemap.set_cell(x, y, b == YELLOW)
		
		x += 1
		if x >= width:
			x = 0
			y += 1


func _on_Config_size_changed(w, h, sc):
	clear_display()
	width = w
	height = h
	tilemap.scale.x = sc
	tilemap.scale.y = sc
	clear_display()
