extends Node2D

signal size_changed

# Called when the node enters the scene tree for the first time.
#func _ready():
#	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


func _on_Button_pressed():
	var width = int($LineEditWidth.text)
	var height = int($LineEditHeight.text)
	var scale = $HSliderScale.value
	self.visible = false
	emit_signal("size_changed", width, height, scale)
	
