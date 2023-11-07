extends Control

signal simulationBackButton
signal start_simulation

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_time_h_slider_value_changed(value):
	get_node("TimeHSlider/TimeValue").text = str(value)
	Engine.time_scale = value


func _on_back_button_pressed():
	pass # Replace with function body.


func _on_start_button_pressed():
	start_simulation.emit()
