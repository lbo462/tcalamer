extends AnimatedSprite2D

signal finished_action
signal wreck_searched

@onready var spawn_coord: Vector2 = position
@onready var _last_position: Vector2 = position

var idle: String = "idle_down"
var sex: String = "m"
var id: int

var _destination: PathFollow2D = null

var _speed: float
var _progress: float = 0
var _start_point: Vector2
var _dist_to_path: Vector2

var _current_position: Vector2 = Vector2.ZERO
var _delta_position: Vector2 = Vector2.ZERO

enum DIRECTION {IDLE, UP, DOWN, RIGHT, LEFT}
var _direction: DIRECTION = DIRECTION.UP

enum MOVE_SET {TO_PATH, TO_DEST, GOING_BACK, TO_COLONY}
var _movement: MOVE_SET = MOVE_SET.TO_PATH

var _is_waiting: bool = false

func _process(delta):
	#print(delta_position)
	if _destination == null:
		if _direction != DIRECTION.IDLE:
			_direction = DIRECTION.IDLE
			play(idle + sex)
		return
	animate_player()
	move(delta)

func animate_player():
	_current_position = position
	
	_delta_position = _current_position - _last_position
	if !_is_waiting:
		if _delta_position.x >= _delta_position.y:
			if _delta_position.x >= 0:
				if _direction != DIRECTION.RIGHT:
					_direction = DIRECTION.RIGHT
					play("right_" + sex)
			else:
				if _direction != DIRECTION.LEFT:
					_direction = DIRECTION.LEFT
					play("left_" + sex)
		elif _delta_position.x < _delta_position.y:
			if _delta_position.y >= 0:
				if _direction != DIRECTION.DOWN:
					_direction = DIRECTION.DOWN
					play("down_" + sex)
			else:
				if _direction != DIRECTION.UP:
					_direction = DIRECTION.UP
					play("up_" + sex)
	else:
		play(_destination.get_parent().get_parent().destinations_idle_animations[_destination.get_parent().get_parent().destinations.find(_destination)] + sex)
	
	_last_position = _current_position

func move(delta):
	match _movement:
		MOVE_SET.TO_PATH:
			if abs(position.x - _start_point.x) > 0.1 or abs(position.y - _start_point.y) > 0.1:
				position = clamp(position + _dist_to_path * delta, spawn_coord, _start_point) if spawn_coord < _start_point else clamp(position + _dist_to_path * delta, _start_point, spawn_coord) #lerp(position, _start_point, 0.5)
			else:
				_movement = MOVE_SET.TO_DEST
		MOVE_SET.TO_DEST:
			_progress = clamp(_progress + _speed * delta, 0, 1)
			_destination.progress_ratio = _progress
			position = _destination.position
			if _destination.progress_ratio >= 0.99:
				if _is_waiting:
					return
				else:
					_is_waiting = true
					await get_tree().create_timer(randf_range(2.0, 3.0)).timeout
					_is_waiting = false
					if _destination.name.contains("Wreck"):
						wreck_searched.emit(id)
						print(id)
					_movement = MOVE_SET.GOING_BACK
		MOVE_SET.GOING_BACK:
			_progress = clamp(_progress - _speed * delta, 0, 1)
			_destination.progress_ratio = _progress
			position = _destination.position
			if _destination.progress_ratio <= 0.01:
				_dist_to_path = spawn_coord - _start_point
				_movement = MOVE_SET.TO_COLONY
		MOVE_SET.TO_COLONY:
			if abs(position.x - spawn_coord.x) > 0.1 or abs(position.y - spawn_coord.y) > 0.1:
				position = clamp(position + _dist_to_path * delta, spawn_coord, _start_point) if spawn_coord < _start_point else clamp(position + _dist_to_path * delta, _start_point, spawn_coord)
			else:
				_destination = null
				_movement = MOVE_SET.TO_PATH
				finished_action.emit()

func go_to_point(dest):
	await get_tree().create_timer(randf_range(0.1, 1.0)).timeout
	_speed = randf_range(0.2, 0.4)
	_destination = dest
	_progress = 0
	_destination.progress_ratio = _progress
	_start_point = _destination.position
	_dist_to_path = _start_point - spawn_coord
