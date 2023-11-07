extends Node


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


func show_main_menu():
	get_node("MainMenu").show()

func hide_main_menu():
	get_node("MainMenu").hide()
