extends Control

signal simulation_back_button
signal start_simulation

func _on_time_h_slider_value_changed(value):
	$TimeHSlider/TimeValue.text = str(value)
	Engine.time_scale = value

func _on_back_button_pressed():
	simulation_back_button.emit()


func _on_start_button_pressed():
	start_simulation.emit()
