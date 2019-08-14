extends Control

var fff
var config_panel

# Called when the node enters the scene tree for the first time.
func _ready():
	fff = $fff
	config_panel = $PanelConfig

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _on_ButtonConnect_pressed():
	config_panel.hide()
	fff.connect_to($PanelConfig/LineEditIpAdress.text)
	fff.init_display(int($PanelConfig/LineEditWidth.text),
					  int($PanelConfig/LineEditHeight.text))
	fff.visible = true
