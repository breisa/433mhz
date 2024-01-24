#!/usr/bin/env python3
import argparse
import time
import json

def store(path, data):
    with open(path, 'w') as file:
        json.dump(data, file)

def load(path):
	with open(path, 'r') as file:
		return json.load(file)

def record(file, pin, recordlen):
	import pigpio
	gpio = pigpio.pi()

	record_edges = False
	edges = []

	def handle_edge(pin, level, useconds):
		if (record_edges and useconds > start_time):
			edges.append((level, useconds))

	gpio.set_pull_up_down(pin, pigpio.PUD_DOWN)
	gpio.set_mode(pin, pigpio.INPUT)
	gpio.callback(pin, pigpio.EITHER_EDGE, handle_edge)

	start_time = gpio.get_current_tick()
	record_edges = True
	time.sleep(recordlen)
	record_edges = False
	stop_time = gpio.get_current_tick()

	gpio.stop()

	# ensure the recording starts and ends with 0
	if (len(edges) >= 2):
		if (edges[0][0] == 0):
			edges = edges[1:]
		if (edges[-1][0] == 1):
			edges = edges[:-1]

	if (len(edges) < 2):
		print('no signal received, please check input pin and wiring')
	else:
		print(f'recorded {len(edges)} edges in {round(recordlen*1000)}ms ({len(edges)/recordlen} edges/secod)')
		assert edges[0][0] == 1
		assert edges[-1][0] == 0
		signal = []
		last_time = start_time
		for level, useconds in edges:
			time_diff = useconds - last_time
			match level:
				case 1:
					signal.append((0, time_diff))
				case 0:
					signal.append((1, time_diff))
			last_time = useconds
		signal.append((0, stop_time - last_time))
		store(file, signal)
		print(f'wrote {len(signal)} symbols to \'{file}\'')

def send_signal(gpio, pin, data):
	# create waveform
	waveform = []
	for state, duration in data:
		match state:
			case 1:
				waveform.append(pigpio.pulse(1<<pin, 0, duration))
			case 0:
				waveform.append(pigpio.pulse(0, 1<<pin, duration))
	gpio.wave_clear()
	gpio.wave_add_generic(waveform)
	signal = gpio.wave_create()
	# transmit waveform once
	gpio.wave_send_once(signal)
	time.sleep(1.5 * gpio.wave_get_micros()/1_000_000)
	gpio.wave_tx_stop()
	gpio.wave_clear()

def send(file, pin):
	import pigpio

	data = load(file)

	gpio = pigpio.pi()
	gpio.set_mode(pin, pigpio.OUTPUT)
	print(f'sending {len(data)} symbols of signal from \'{file}\'...', end='', flush=True)
	
	# create waveform
	waveform = []
	for state, duration in data:
		match state:
			case 1:
				waveform.append(pigpio.pulse(1<<pin, 0, duration))
			case 0:
				waveform.append(pigpio.pulse(0, 1<<pin, duration))
	gpio.wave_clear()
	gpio.wave_add_generic(waveform)
	signal = gpio.wave_create()

	# transmit waveform once
	gpio.wave_send_once(signal)
	time.sleep(1.5 * gpio.wave_get_micros()/1_000_000)
	gpio.wave_tx_stop()
	gpio.wave_clear()

	print(' done')
	gpio.stop()

def plot(file):
	import matplotlib.pyplot as pyplot
	# create rectangular curve for signal
	signal = load(file)
	dots = []
	time = 0
	for state, duration in signal:
		dots.append((time, state))
		time += duration
		dots.append((time, state))
	x, y = zip(*dots)
	# plot signal
	pyplot.figure(num=file)
	pyplot.xlabel('microseconds')
	pyplot.ylabel('amplitude')
	pyplot.plot(x, y)
	pyplot.show()


def create_argument_parser():
	parser = argparse.ArgumentParser()
	modes = parser.add_mutually_exclusive_group(required=True)
	modes.add_argument('--record', metavar='GPIO', type=int, choices=range(0,31),
		help='record a signal on gpio pin GPIO and store it in FILE')
	modes.add_argument('--plot', action='store_true', default=False,
		help='plot the signal stored in FILE')
	modes.add_argument('--send', metavar='GPIO', type=int, choices=range(0,31),
		help='replay the signal stored in FILE on gpio pin GPIO')
	parser.add_argument('--recordlen', metavar='MS', type=int, default=250,
		help='amount of milliseconds to record (defaults to 250ms)')
	parser.add_argument('FILE', help='the json file to load or store a signal')
	return parser

def main():
	arg_parser = create_argument_parser()
	args = arg_parser.parse_args()
	if (args.record is not None):
		if (args.recordlen < 100 or args.recordlen > 10_000):
			print('recordlen should be between 100ms and 10s')
		else:
			record(args.FILE, args.record, args.recordlen/1000)
	elif (args.plot):
		plot(args.FILE)
	elif (args.send is not None):
		send(args.FILE, args.send)
	else:
		arg_parser.print_help()

if __name__ == '__main__':
	main()