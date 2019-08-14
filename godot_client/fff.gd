extends Node2D

var peer: StreamPeerTCP
const DEFAULT_PORT = 10101
var display_size
var tmap

func connect_to(host):
	print("connect to %s on port %s" % [host, DEFAULT_PORT])
	peer = StreamPeerTCP.new()
	var err = peer.connect_to_host(host, DEFAULT_PORT)
	if err != OK:
		printerr("Unable to connect")

# Called when the node enters the scene tree for the first time.
func _ready():
	tmap = $TileMap

func init_display(width, height):
	for x in range(width):
		for y in range(height):
			tmap.set_cell(x, y, 0)

	display_size = Vector2(width, height)

func _input(event):
	if not self.visible:
		return
		
	if event is InputEventMouseButton and event.pressed:
		var tile_pos = tmap.world_to_map(event.position)
		var old_tile = tmap.get_cellv(tile_pos)
		tmap.set_cellv(tile_pos, 1-old_tile)
		send_to_server()

func send_to_server():
	# TODO iterate over tiles
	var data = '10101'
	print("sending ", data)
	peer.put_data(data.to_ascii())

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
