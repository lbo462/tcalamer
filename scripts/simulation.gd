extends Node

signal back

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("DATA/Game/game.json")

@export_group("Players")
@export var playerInstance: PackedScene
@export var playerInfos: PackedScene

@export_group("Players Infos")
@export var man_sprite: Image
@export var woman_sprite: Image
@export var dead_sprite: Image

#var names: Array[String] = ["Ines", "Kowsi", "Valentin", "Aziz", "Sokhna", "Leo", "Edgar", "Etienne", "Nicolas", "Gausse", "Zineb", "Ryad", "Alan", "Lucas", "Quentin", "Alex", "Augusto", "Matheo", "Leo", "Mounir", "Hedi", "Boris"]
#var sexes: Array[bool] = [false, true, true, true, false, true, true, true, true, true, false, true, true, true, true, true, true, true, true, true, true, true]

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

var players: Array[Player] = []
var nbPlayers: int
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
	
	nbPlayers = len(initial_state["colony"]["players"])
	
	_setup_ui(initial_state["world"], initial_state["colony"], initial_state["wreck"], 1)
	
	for i in range(nbPlayers):
		_setup_player(i)

func run_simulation():
	finished_players

func _setup_ui(world, colony, wreck, day):
	$WorldUI/Day/CurrentDay.text = str(day)
	$WorldUI/Climate/CurrentClimate.text = str(world["weather"])
	$WorldUI/Ressources/W_Water.text = str(world["water"])
	$WorldUI/Ressources/W_Food.text = str(world["food"])
	$WorldUI/Ressources/W_Wood.text = str(world["wood"])
	$WorldUI/Ressources/C_Water.text = str(colony["water"])
	$WorldUI/Ressources/C_Food.text = str(colony["food"])
	$WorldUI/Ressources/C_Wood.text = str(colony["wood"])
	$WorldUI/Ressources/N_Water.text = str(nbPlayers)
	$WorldUI/Ressources/N_Food.text = str(nbPlayers)
	$WorldUI/Ressources/N_Wood.text = str(nbPlayers * 3)
	$WorldUI/Objects/BucketNumber.text = str(wreck["buckets"])
	$WorldUI/Objects/FishingRodNumber.text = str(wreck["fishing_rods"])
	$WorldUI/Objects/AxeNumber.text = str(wreck["axes"])

func _setup_player(i):
	var p = _create_player(i)
	var p_i = _create_player_infos(i)
	var player = Player.new(p, p_i)
	players.append(player)
	
	if nbPlayers != len(our_class):
		p.sex = "m" if player.sex else "w"
	else:
		p.sex = "m" if our_class[i].sex else "w"
	
	_go_to_point(player, randi_range(0, 3))

func _create_player(p):
	var player = playerInstance.instantiate()
	
	var player_spawn_location = $World/SpawnPath/SpawnPoints
	player_spawn_location.progress_ratio = p * 1.0 / nbPlayers #randf()
	player.position = player_spawn_location.position
	
	if player_spawn_location.rotation >= -PI / 4 and player_spawn_location.rotation < PI / 4:
		player.idle = "idle_down_"
	elif player_spawn_location.rotation >= PI / 4 and player_spawn_location.rotation < 3 * PI / 4:
		player.idle = "idle_left_"
	elif player_spawn_location.rotation >= 3 * PI / 4 or player_spawn_location.rotation <= -3 * PI / 4:
		player.idle = "idle_up_"
	else:
		player.idle = "idle_right_"
	
	player.get_node("ID").text = str(p + 1) if nbPlayers != len(our_class) else our_class[p].name
	
	$World.add_child(player)
	
	return player
	
func _create_player_infos(p):
	var player = playerInfos.instantiate()
	player.get_node("ID").text = str(p + 1) if nbPlayers != len(our_class) else our_class[p].name
	$PlayersInfos.add_child(player)
	return player

func _go_to_point(player, point):
	player.player.go_to_point($World.destinations[point])

class Player:
	var alive: bool = true
	var sex: bool
	var player
	var player_infos
	var has_bucket: bool = false
	var has_fishing_rod: bool = false
	var has_axe: bool = false
	
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
