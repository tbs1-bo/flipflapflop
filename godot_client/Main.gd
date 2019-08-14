extends Control

var fff
var line_edit_ip
var line_edit_width
var line_edit_height
var config

# Called when the node enters the scene tree for the first time.
func _ready():
	fff = $fff
	line_edit_ip = $MarginContainer/VBoxContainer/HBoxContainerConnection/LineEditIpAdress
	line_edit_width = $MarginContainer/VBoxContainer/HBoxContainerSize/LineEditWidth
	line_edit_height = $MarginContainer/VBoxContainer/HBoxContainerSize/LineEditHeight
	config = $MarginContainer

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _on_ButtonConnect_pressed():
	config.hide()
	fff.set_host(line_edit_ip.text)
	fff.init_display(int(line_edit_width.text),
					  int(line_edit_height.text))
	fff.visible = true
