extends Node2D

var peer: StreamPeerTCP
const DEFAULT_PORT = 10101

func connect_to(host):
	print("connect to %s" % host)
	peer = StreamPeerTCP.new()
	peer.connect_to_host(host, DEFAULT_PORT)

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

func _input(event):
	if not self.visible:
		return
		
	if event is InputEventMouse:
		#print(event)
		var mousepos = event.position
		var mappos = $TileMap.world_to_map(mousepos)
		print("world %s \t map %s" % [mousepos, mappos])
	
	if event is InputEventMouseButton and event.pressed:
		var tile_pos = $TileMap.world_to_map(event.position)
		var old_tile = $TileMap.get_cellv(tile_pos)
		$TileMap.set_cellv(tile_pos, 1-old_tile)
		
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
