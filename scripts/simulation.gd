extends Node

signal back

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("DATA/Game/game.json")

@export_group("Players")
@export var playerInstance: PackedScene
@export var playerInfos: PackedScene

@export_group("Players Infos")
@export var man_sprite: Texture2D
@export var woman_sprite: Texture2D
@export var dead_sprite: Texture2D

var our_class: Array[Classmate] = [
	Classmate.new("Ines", false), 
	Classmate.new("Kowsi", true), 
	Classmate.new("Valentin", true), 
	Classmate.new("Aziz", true), 
	Classmate.new("Sokhna", false), 
	Classmate.new("Leo", true), 
	Classmate.new("Edgar", true), 
	Classmate.new("Etienne", true), 
	Classmate.new("Nicolas", true), 
	Classmate.new("Gausse", true), 
	Classmate.new("Zineb", false), 
	Classmate.new("Ryad", true), 
	Classmate.new("Alan", true), 
	Classmate.new("Lucas", true), 
	Classmate.new("Quentin", true), 
	Classmate.new("Alex", true), 
	Classmate.new("Augusto", true), 
	Classmate.new("Matheo", true), 
	Classmate.new("Leo", true), 
	Classmate.new("Mounir", true), 
	Classmate.new("Hedi", true), 
	Classmate.new("Boris", true)]

var _game_intructions: Array
var _nb_days: int
var _current_day: int = 0

var players: Array[Player] = []
var nb_players: int
var finished_players: int

func _ready():
	if !OS.has_feature("standalone"): # if NOT exported version
		json_path = ProjectSettings.globalize_path("res://DATA/Game/game.json")
	
	$PlayersInfos.hide()
	$World/TileMap.visible = false
	$WorldUI.hide()

func show_simulation():
	clear_simulation_data()
	$PlayersInfos.show()
	$World/TileMap.visible = true
	$WorldUI.show()
	
func hide_simulation():
	clear_simulation_data()
	$PlayersInfos.hide()
	$World/TileMap.visible = false
	$WorldUI.hide()
	back.emit()

func clear_simulation_data():
	for p in players:
		p.player.queue_free()
		p.player_infos.queue_free()
	players.clear()

func new_simulation():
	
	var json_as_text = FileAccess.get_file_as_string(json_path)
	var json_as_dict = JSON.parse_string(json_as_text)
	
	'''if json_as_dict:
		print(json_as_dict)
	else:
		print("no json")
		#return'''
	
	clear_simulation_data()
	
	var initial_state = json_as_dict["initial_state"]
	
	nb_players = len(initial_state["colony"]["players"])
	
	_update_ui(initial_state["world"], initial_state["colony"], 1)
	_update_wreck_ui(initial_state["wreck"])
	
	for i in range(nb_players):
		_setup_player(i)
	
	_game_intructions = json_as_dict["turns"]
	_nb_days = len(_game_intructions)
	
	_run_simulation_morning()

func _setup_player(i: int):
	var p = _create_player(i)
	var p_i = _create_player_infos(i)
	var player = Player.new(p, p_i)
	_update_player_objects(p_i, player.objects)
	
	p.id = i
	
	if nb_players != len(our_class):
		p.sex = "m" if player.sex else "w"
		p_i.get_node("PlayerOverview").texture = man_sprite if player.sex else woman_sprite
	else:
		p.sex = "m" if our_class[i].sex else "w"
		p_i.get_node("PlayerOverview").texture = man_sprite if our_class[i].sex else woman_sprite
	
	players.append(player)

func _create_player(p):
	var player = playerInstance.instantiate()
	
	var player_spawn_location = $World/SpawnPath/SpawnPoints
	player_spawn_location.progress_ratio = p * 1.0 / nb_players #randf()
	player.position = player_spawn_location.position
	
	if player_spawn_location.rotation >= -PI / 4 and player_spawn_location.rotation < PI / 4:
		player.idle = "idle_down_"
	elif player_spawn_location.rotation >= PI / 4 and player_spawn_location.rotation < 3 * PI / 4:
		player.idle = "idle_left_"
	elif player_spawn_location.rotation >= 3 * PI / 4 or player_spawn_location.rotation <= -3 * PI / 4:
		player.idle = "idle_up_"
	else:
		player.idle = "idle_right_"
	
	player.get_node("ID").text = str(p + 1) if nb_players != len(our_class) else our_class[p].name
	
	$World.add_child(player)
	
	player.wreck_searched.connect(_wreck_searched)
	player.finished_action.connect(_player_finished)
	
	return player
	
func _create_player_infos(p):
	var player = playerInfos.instantiate()
	player.get_node("ID").text = str(p + 1) if nb_players != len(our_class) else our_class[p].name
	$PlayersInfos.add_child(player)
	return player

func _run_simulation_morning():
	var day = _game_intructions[_current_day]
	
	# Actions
	finished_players = 0
	for a in day["actions"]:
		_go_to_point(players[int(a["player_id"])], int(a["action_id"]))

func _player_finished():
	finished_players += 1
	if finished_players == nb_players:
		_run_simulation_evening()

func _wreck_searched(id: int):
	# Objects
	var state = _game_intructions[_current_day]["night_state"]
	var players_states = state["colony"]["players"]
	_update_player_objects(players[int(players_states[id]["number"])].player_infos, [players_states[id]["has_bucket"], players_states[id]["has_fishing_rod"], players_states[id]["has_axe"]])
	_update_wreck_ui(state["wreck"])

func _run_simulation_evening():
	var day = _game_intructions[_current_day]
	
	# UI
	var state = day["night_state"]
	_update_ui(state["world"], state["colony"], day["day"])
	
	# UI Players
	var players_states = state["colony"]["players"]
	for p in players_states:
		if p["state"] == 0:
			# Die
			players[int(p["number"])].player_infos.get_node("PlayerOverview").texture = dead_sprite
	
	# Next day
	await get_tree().create_timer(randf_range(3.0, 5.0)).timeout
	_current_day += 1
	_run_simulation_morning()

func _update_player_objects(player_infos, objects: Array[bool]):
	for i in range(0, len(player_infos.get_node("ObjectsContainer").get_children())):
		player_infos.get_node("ObjectsContainer").get_child(i).modulate = Color(int(objects[i]), int(objects[i]), int(objects[i]))

func _go_to_point(player: Player, point: int):
	player.player.go_to_point($World.destinations[point])

func _update_ui(world, colony, day):
	var weather: String
	match int(world["weather"]):
		0:
			weather = "Ciel bleu"
		1:
			weather = "Nuageux"
		2:
			weather = "Pluvieux"
		3:
			weather = "Tempête"
		_:
			weather = "Inconnue"
			
	$WorldUI/Day/CurrentDay.text = str(day)
	$WorldUI/Climate/CurrentClimate.text = weather
	$WorldUI/Ressources/W_Water.text = str(world["water"])
	$WorldUI/Ressources/W_Food.text = str(world["food"])
	$WorldUI/Ressources/W_Wood.text = str(world["wood"])
	$WorldUI/Ressources/C_Water.text = str(colony["water"])
	$WorldUI/Ressources/C_Food.text = str(colony["food"])
	$WorldUI/Ressources/C_Wood.text = str(colony["wood"])
	$WorldUI/Ressources/N_Water.text = str(nb_players)
	$WorldUI/Ressources/N_Food.text = str(nb_players)

func _update_wreck_ui(wreck):
	$WorldUI/Objects/BucketNumber.text = str(wreck["buckets"])
	$WorldUI/Objects/FishingRodNumber.text = str(wreck["fishing_rods"])
	$WorldUI/Objects/AxeNumber.text = str(wreck["axes"])

class Player:
	var alive: bool = true
	var sex: bool
	var player
	var player_infos
	var objects: Array[bool] = [false, false, false]
	
	func _init(p, p_infos):
		player = p
		player_infos = p_infos
		sex = true if randf() >= 0.5 else false

class Classmate:
	var name: String
	var sex: bool
	
	func _init(name, sex):
		self.name = name
		self.sex = sex
