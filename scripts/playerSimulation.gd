extends AnimatedSprite2D

@onready var spawn_coord: Vector2 = position
@onready var _last_position: Vector2 = position

var idle: String = "idle_down"

var _destination: PathFollow2D = null

var _speed: float = randf_range(0.0035, 0.0075) # 0.0075
var _progress: float = 0
var _start_point: Vector2

var _current_position: Vector2 = Vector2.ZERO
var _delta_position: Vector2 = Vector2.ZERO

enum DIRECTION {IDLE_UP, IDLE_DOWN, IDLE_RIGHT, IDLE_LEFT, UP, DOWN, RIGHT, LEFT}
var _direction: DIRECTION = DIRECTION.IDLE_UP

enum MOVE_SET {TO_PATH, TO_DEST, GOING_BACK, TO_COLONY}
var _movement: MOVE_SET = MOVE_SET.TO_PATH

func _process(delta):
	#print(delta_position)
	if _destination == null:
		play(idle)
		return
	animate_player()
	move()

func animate_player():
	_current_position = position
	
	_delta_position = _current_position - _last_position
	if _delta_position.x >= _delta_position.y:
		if _delta_position.x >= 0:
			if _direction != DIRECTION.RIGHT:
				_direction = DIRECTION.RIGHT
				play("right")
		else:
			if _direction != DIRECTION.LEFT:
				_direction = DIRECTION.LEFT
				play("left")
	else:
		if _delta_position.y >= 0:
			if _direction != DIRECTION.DOWN:
				_direction = DIRECTION.DOWN
				play("down")
		else:
			if _direction != DIRECTION.UP:
				_direction = DIRECTION.UP
				play("up")
	
	_last_position = _current_position

func move():
	match _movement:
		MOVE_SET.TO_PATH:
			if abs(position.x - _start_point.x) > 0.1 or abs(position.y - _start_point.y) > 0.1:
				position = lerp(position, _start_point, 0.5)
			else:
				_movement = MOVE_SET.TO_DEST
		MOVE_SET.TO_DEST:
			_progress = clamp(_progress + _speed, 0, 1)
			_destination.progress_ratio = _progress
			position = _destination.position
			if _destination.progress_ratio >= 0.99:
				_movement = MOVE_SET.GOING_BACK
		MOVE_SET.GOING_BACK:
			_progress = clamp(_progress - _speed, 0, 1)
			_destination.progress_ratio = _progress
			position = _destination.position
			if _destination.progress_ratio <= 0.01:
				_movement = MOVE_SET.TO_COLONY
		MOVE_SET.TO_COLONY:
			if abs(position.x - spawn_coord.x) > 0.1 or abs(position.y - spawn_coord.y) > 0.1:
				position = lerp(position, spawn_coord, 0.1)
			else:
				_destination = null
				_movement = MOVE_SET.TO_PATH

func go_to_point(dest):
	_destination = dest
	_progress = 0
	_destination.progress_ratio = _progress
	_start_point = _destination.position
