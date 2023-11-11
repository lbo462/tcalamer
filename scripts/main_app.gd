extends Node

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("DATA/data.json")

func _ready():
	if !OS.has_feature("standalone"): # if NOT exported version
		json_path = ProjectSettings.globalize_path("res://DATA/data.json")
	
	var json_as_text = FileAccess.get_file_as_string(json_path)
	if json_as_text:
		$MainMenu/ButtonSimulation.disabled = false
	else:
		$MainMenu/ButtonSimulation.disabled = true

func show_main_menu():
	$MainMenu.show()

func hide_main_menu():
	$MainMenu.hide()

func _on_button_quit_pressed():
	get_tree().quit()
