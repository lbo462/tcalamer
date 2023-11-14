extends Control

signal training_back_button
signal go_to_simulation

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("DATA/data.json")

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

func _on_save_button_pressed():
	_save_data(_get_game_data())

func _get_game_data():
	return {
		"number_of_players": get_node("Players/NbPlayersInput").value,
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
		"initial_water_surviving_factor": get_node("Ressources/S_WaterNumber").value,
		"initial_food_surviving_factor": get_node("Ressources/S_FoodNumber").value
	}

func train():
	var game_data = _get_game_data()
	var training_data = {
		"ge_params": game_data,
		"iter_amount": get_node("Iterations/NbIterationsInput").value
	}
	
	_save_data(game_data)
	
	var headers = ["Content-Type: application/json"]
	$HTTPRequest.request_completed.connect(_on_request_completed)
	$HTTPRequest.request("http://localhost:8000/train", headers, HTTPClient.METHOD_POST, JSON.stringify(training_data))

func _on_request_completed(_result, _response_code, _headers, _body):
	_activate_buttons()

func _save_data(game_data: Dictionary):
	var file = FileAccess.open(json_path, FileAccess.WRITE)
	file.store_line(JSON.stringify(game_data))

func _disable_buttons():
	$BackButton.disabled = true
	$TrainButton.disabled = true
	$SimulationButton.disabled = true
	$SaveButton.disabled = true

func _activate_buttons():
	$BackButton.disabled = false
	$TrainButton.disabled = false
	$SimulationButton.disabled = false
	$SaveButton.disabled = false
