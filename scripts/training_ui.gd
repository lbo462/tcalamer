extends Control

signal trainingBackButton

var DIR = OS.get_executable_path().get_base_dir()
var interpreter_path = DIR.path_join("PythonFiles/venv/bin/python3.10")
var script_path = DIR.path_join("PythonFiles/<name>.py")

func _ready():
	hide_training_ui()
	
	if !OS.has_feature("standalone"): # if NOT exported version
		interpreter_path = ProjectSettings.globalize_path("res://PythonFiles/venv/bin/python3.10")
		script_path = ProjectSettings.globalize_path("res://PythonFiles/<name>.py")

func show_training_ui():
	show()

func hide_training_ui():
	hide()

func _on_back_button_pressed():
	hide_training_ui()
	trainingBackButton.emit()

func _on_train_button_pressed():
	get_node("BackButton").disabled = true
	get_node("TrainButton").disabled = true
	train()

func train():
	var training_data = {
		"players": get_node("Players/NbPlayersInput").value,
		"objects": {
			"bucket": get_node("Objects/BucketNumber").value,
			"fishing_rode": get_node("Objects/FishingRodeNumber").value,
			"axe": get_node("Objects/AxeNumber").value,
			"probability": get_node("Objects/ProbabiliyValue").value
		},
		"ressources": {
			"world": {
				"w_water": get_node("Ressources/W_WaterNumber").value,
				"w_food": get_node("Ressources/W_FoodNumber").value,
				"w_wood": get_node("Ressources/W_WoodNumber").value
			},
			"start": {
				"s_water": get_node("Ressources/S_WaterNumber").value,
				"s_food": get_node("Ressources/S_FoodNumber").value,
			},
			"needs": {
				"n_water": get_node("Ressources/N_WaterNumber").value,
				"n_food": get_node("Ressources/N_FoodNumber").value,
				"n_wood": get_node("Ressources/N_WoodNumber").value
			},
			"leave": {
				"l_water": get_node("Ressources/L_WaterNumber").value,
				"l_food": get_node("Ressources/L_FoodNumber").value,
				"l_wood": get_node("Ressources/L_WoodNumber").value
			}
		}
	}
	
	#OS.execute(interpreter_path, [script_path, training_data])
