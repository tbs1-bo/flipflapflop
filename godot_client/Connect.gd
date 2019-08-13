extends Control


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


func _on_Button_pressed():
	#var fff = preload("res://fff.tscn").instance()
	get_tree().change_scene("res://fff.tscn")
	#add_child(fff)
	hide()
