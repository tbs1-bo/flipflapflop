extends Node2D

var width
var height
var tilemap
var server

const PORT = 10101

const YELLOW = 49  # ascii 1

# Called when the node enters the scene tree for the first time.
func _ready():
	tilemap = get_node("TileMap")
	var screen_size = get_viewport_rect().size
	width = screen_size.x / tilemap.cell_size.x
	height = screen_size.y / tilemap.cell_size.y
	clear_display()

	print("listening on port ", PORT)
	server = TCP_Server.new()
	server.listen(PORT)
	
func clear_display():
	for x in range(width):
		for y in range(height):
			tilemap.set_cell(x, y, 0)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if server.is_connection_available():
		print("conn available")
		var conn = server.take_connection()
		print("bytes available ", conn.get_available_bytes())
		var bs = conn.get_data(conn.get_available_bytes())
		print("bytes ", bs, len(bs))
		process_bytes(bs[1])
		

func process_bytes(bytes):
	var x = 0
	var y = 0
	
	for b in bytes:
		print("byte ", b)
		print("xy ", x, " ", y)
		
		tilemap.set_cell(x, y, b == YELLOW)
		
		x += 1
		if x >= width:
			x = 0
			y += 1

func _on_Button_pressed():
	var cell
	for x in range(4):
		cell = tilemap.get_cell(x, 0)
		print("x ", x, " cell ", cell, 
		      " type ", typeof(tilemap), " invalid ", cell == TileMap.INVALID_CELL)
		tilemap.set_cell(x, 2, cell)
		
