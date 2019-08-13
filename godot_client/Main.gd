extends Control

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _on_ButtonConnect_pressed():
	$PanelConfig.hide()
	$fff.connect_to($PanelConfig/LineEditIpAdress.text)
	$fff.init_display(int($PanelConfig/LineEditWidth.text),
					  int($PanelConfig/LineEditHeight.text))
	$fff.visible = true
