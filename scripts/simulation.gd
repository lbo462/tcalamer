extends Node

var DIR = OS.get_executable_path().get_base_dir()
var json_path = DIR.path_join("JSON/<name>.json")

@export_group("Players")
@export var playerInstance: PackedScene
@export var playerInfos: PackedScene

var players: Array[Player] = []
var nbPlayers: int = 10
var ressources: int = 500
var objects: int = 1
var base_water_amount: int = 3
var base_food_amount: int = 3
var wood_amount: int = 10

func _ready():
	if !OS.has_feature("standalone"): # if NOT exported version
		json_path = ProjectSettings.globalize_path("res://JSON/<name>.json")
		
	get_node("PlayersInfos").hide()
	get_node("World/TileMap").visible = false
	get_node("WorldUI").hide()

func show_simulation():
	clear_simulation_data()
	get_node("PlayersInfos").show()
	get_node("World/TileMap").visible = true
	get_node("WorldUI").show()
	
func hide_simulation():
	get_node("PlayersInfos").hide()
	get_node("World/TileMap").visible = false
	get_node("WorldUI").hide()

func clear_simulation_data():
	for p in players:
		p.player.queue_free()
		p.player_infos.queue_free()
	players.clear()

func new_simulation():
	
	var json_as_text = FileAccess.get_file_as_string(json_path)
	var json_as_dict = JSON.parse_string(json_as_text)
	
	if json_as_dict:
		print(json_as_dict)
	else:
		print("no json")
		#return
	
	clear_simulation_data()
	
	_setup_ui(ressources, ressources, ressources, objects, objects, objects)
	
	for i in range(nbPlayers):
		_setup_players(i)

func _setup_ui(water, food, wood, bucket, fishing_rode, axe):
	get_node("WorldUI/Day/CurrentDay").text = "1"
	get_node("WorldUI/Ressources/W_Water").text = str(water)
	get_node("WorldUI/Ressources/W_Food").text = str(food)
	get_node("WorldUI/Ressources/W_Wood").text = str(wood)
	get_node("WorldUI/Ressources/C_Water").text = str(nbPlayers * base_water_amount)
	get_node("WorldUI/Ressources/C_Food").text = str(nbPlayers * base_food_amount)
	get_node("WorldUI/Ressources/C_Wood").text = "0"
	get_node("WorldUI/Ressources/N_Water").text = str(nbPlayers)
	get_node("WorldUI/Ressources/N_Food").text = str(nbPlayers)
	get_node("WorldUI/Ressources/N_Wood").text = str(nbPlayers * wood_amount)
	get_node("WorldUI/Objects/BucketNumber").text = str(bucket)
	get_node("WorldUI/Objects/FishingRodeNumber").text = str(fishing_rode)
	get_node("WorldUI/Objects/AxeNumber").text = str(axe)

func _setup_players(i):
	var p = _create_player(i)
	var p_i = _create_player_infos(i)
	var player = Player.new()
	player.setup(p, p_i)
	players.append(player)
	_go_to_point(player, randi_range(0, 3))

func _create_player(p):
	var player = playerInstance.instantiate()
	
	var player_spawn_location = get_node("World/SpawnPath/SpawnPoints")
	player_spawn_location.progress_ratio = p * 1.0 / nbPlayers #randf()
	player.position = player_spawn_location.position
	
	if player_spawn_location.rotation >= -PI / 4 and player_spawn_location.rotation < PI / 4:
		player.idle = "idle_down"
	elif player_spawn_location.rotation >= PI / 4 and player_spawn_location.rotation < 3 * PI / 4:
		player.idle = "idle_left"
	elif player_spawn_location.rotation >= 3 * PI / 4 or player_spawn_location.rotation <= -3 * PI / 4:
		player.idle = "idle_up"
	else:
		player.idle = "idle_right"
	
	player.get_node("ID").text = str(p + 1)
	
	get_node("World").add_child(player)
	
	return player
	
func _create_player_infos(p):
	var player = playerInfos.instantiate()
	player.get_node("ID").text = str(p + 1)
	get_node("PlayersInfos").add_child(player)
	return player

func _go_to_point(player, point):
	player.player.go_to_point(get_node("World").destinations[point])

class Player:
	var alive = true
	var player
	var player_infos
	var has_bucket = false
	var has_fishing_rode = false
	var has_axe = false
	
	func setup(p, p_infos):
		player = p
		player_infos = p_infos
