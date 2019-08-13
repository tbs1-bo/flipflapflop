extends Node2D

signal size_changed

# Called when the node enters the scene tree for the first time.
#func _ready():
#	pass

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass

func _on_Button_pressed():
	var width = int($Panel/LineEditWidth.text)
	var height = int($Panel/LineEditHeight.text)
	var scale = $Panel/HSliderScale.value
	self.visible = false
	emit_signal("size_changed", width, height, scale)

func _on_HSliderScale_value_changed(value):
	$Panel/LabelScale.text = "scale %s" % value
