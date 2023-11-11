extends Control

signal training_back_button
signal go_to_simulation

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("DATA/data.json")

var training_data

func _ready():
	hide_training_ui()
	
	if !OS.has_feature("standalone"): # if NOT exported version
		json_path = ProjectSettings.globalize_path("res://DATA/data.json")
	
	var json_as_text = FileAccess.get_file_as_string(json_path)
	if json_as_text:
		$SimulationButton.disabled = false
	else:
		$SimulationButton.disabled = true

func show_training_ui():
	show()

func hide_training_ui():
	hide()

func _on_back_button_pressed():
	hide_training_ui()
	training_back_button.emit()

func _on_train_button_pressed():
	_disable_buttons()
	train()

func _on_simulation_button_pressed():
	hide_training_ui()
	go_to_simulation.emit()

func train():
	training_data = {
		"number_of_players": get_node("Players/NbPlayersInput").value,
		"number_of_iterations": get_node("Iterations/NbIterationsInput").value,
		"wreck_probability": get_node("Objects/ProbabiliyValue").value,
		"bucket_amount": get_node("Objects/BucketNumber").value,
		"axe_amount": get_node("Objects/AxeNumber").value,
		"fishing_rod_amount": get_node("Objects/FishingRodNumber").value,
		"initial_water_level": get_node("Ressources/W_WaterNumber").value,
		"initial_food_amount": get_node("Ressources/W_FoodNumber").value,
		"initial_wood_amount": get_node("Ressources/W_WoodNumber").value,
		"amount_of_wood_per_player_to_leave": get_node("Ressources/L_WoodNumber").value,
		"amount_of_water_per_player_to_leave": get_node("Ressources/L_WaterNumber").value,
		"amount_of_food_per_player_to_leave": get_node("Ressources/L_FoodNumber").value,
		"amount_of_water_per_player_at_the_begining": get_node("Ressources/S_WaterNumber").value,
		"amount_of_food_per_player_at_the_begining": get_node("Ressources/S_FoodNumber").value,
		"amount_of_water_per_player_to_survive": get_node("Ressources/N_WaterNumber").value,
		"amount_of_food_per_player_to_survice": get_node("Ressources/N_FoodNumber").value,
	}
	"""var training_data = {
		"players": get_node("Players/NbPlayersInput").value,
		"objects": {
			"bucket": get_node("Objects/BucketNumber").value,
			"fishing_rod": get_node("Objects/FishingRodNumber").value,
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
			},
			"leave": {
				"l_water": get_node("Ressources/L_WaterNumber").value,
				"l_food": get_node("Ressources/L_FoodNumber").value,
				"l_wood": get_node("Ressources/L_WoodNumber").value
			}
		}
	}"""
	
	#DirAccess.remove_absolute(pth_path)
	#OS.execute(interpreter_path, [script_path, JSON.stringify(training_data)])
	#_save_data()
	var headers = ["Content-Type: application/json"]
	$HTTPRequest.request_completed.connect(_on_request_completed)
	$HTTPRequest.request("http://localhost:8000/train", headers, HTTPClient.METHOD_POST, JSON.stringify(training_data))

func _on_request_completed(_result, response_code, _headers, _body):
	if response_code == 200:
		# var json = JSON.parse_string(body.get_string_from_utf8())
		_save_data()
		_activate_buttons()
	else:
		print("not ok")

func _save_data():
	var file = FileAccess.open(json_path, FileAccess.WRITE)
	file.store_line(JSON.stringify(training_data))

func _disable_buttons():
	$BackButton.disabled = true
	$TrainButton.disabled = true
	$SimulationButton.disabled = true

func _activate_buttons():
	$BackButton.disabled = false
	$TrainButton.disabled = false
	$SimulationButton.disabled = false
