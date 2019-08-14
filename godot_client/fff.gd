extends Node2D

var peer: StreamPeerTCP
const DEFAULT_PORT = 10101
var display_size
var tmap
var server_ip

func set_host(host):
	server_ip = host

func connect_to_server():
	print("connect to %s on port %s" % [server_ip, DEFAULT_PORT])
	peer = StreamPeerTCP.new()
	var err = peer.connect_to_host(server_ip, DEFAULT_PORT)
	if err != OK or peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
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
	connect_to_server()
	var data = ''
	for cellv in tmap.get_used_cells():
		data += str(tmap.get_cellv(cellv))
		
	#print("sending ", data)
	var err = peer.put_data(data.to_ascii())
	if err != OK:
		print("Unable to send data")
	#peer.disconnect_from_host()

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
