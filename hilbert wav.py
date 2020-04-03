import numpy as np
import cv2 as cv
import sys
import wave
import math
import itertools
import struct
from hilbertcurve.hilbertcurve import HilbertCurve

# SCRIPT VARIABLES
# Input File: The image that you want to convert to sound.
# Output File: The output .wav file.
# Starting Note: The bottom-most note of the output sound. Default is 110Hz (A2 in standard tuning)
# Octaves: The number of octaves above the starting note that the sound should span. Default is 6 (i.e. highest frequency as 7040Hz (A8))
# Sample Rate: The number of samples per second. Default is 44100 (average WAV file)
# Duration: Amount of time you want it to last. Default is 5 seconds

def get_inputs():
	# get input file and output file names
	while True:
		input_file_name = input("Enter the name of the input image file: ").strip()
		if input_file_name == "":
			input_file = "lion 32x32.jpg"
			output_file = "lion 32x32.wav"
			break
		elif input_file_name.find(".") != -1:
			input_file = input_file_name
			output_file = input_file_name[:(input_file_name.find(".")+1)] + "wav"
			break
		else:
			print("Please enter the name of the image file, including the extension (.jpg, .png, etc.)")
	
	# get starting note
	while True:
		input_starting_note = input("Enter the starting frequency (leave blank for default - A2/110Hz): ").strip()
		if input_starting_note == "":
			starting_note = 110.0
			break
		else:
			try:
				starting_note = float(input_starting_note)
			except ValueError:
				print("Please enter a number.")
				continue
			
			if starting_note > 0:
				break
			else:
				print("Please enter a positive number.")
	
	# get octaves
	while True:
		input_octaves = input("Enter the number of octaves (leave blank for default - 6): ").strip()
		if input_octaves == "":
			octaves = 6.0
			break
		else:
			try:
				octaves = float(input_octaves)
			except ValueError:
				print("Please enter a number.")
				continue
			
			if octaves > 0:
				break
			else:
				print("Please enter a positive number.")
	
	# get sample rate
	while True:
		input_sample_rate = input("Enter the sample rate (leave blank for default - 44100): ").strip()
		if input_sample_rate == "":
			sample_rate = 44100
			break
		else:
			try:
				sample_rate = int(input_sample_rate)
			except ValueError:
				print("Please enter an integer.")
				continue
			
			if sample_rate > 0:
				break
			else:
				print("Please enter a positive integer.")
	
	# get duration
	while True:
		input_duration = input("Enter the desired duration in seconds (leave blank for default - 5): ").strip()
		if input_duration == "":
			duration = 5.0
			break
		else:
			try:
				duration = float(input_duration)
			except ValueError:
				print("Please enter a number.")
				continue
			
			if duration > 0:
				break
			else:
				print("Please enter a positive number.")
	
	main(input_file, output_file, starting_note, octaves, sample_rate, duration)

# tone generator
def tone(frequency, amplitude, sample_rate, start_sample=0):
	samplenum = start_sample
	if amplitude > 1.0:
		amplitude = 1.0
	elif amplitude < 0.0:
		amplitude = 0.0
	while True:
		sample = (float(amplitude) * math.sin(2*math.pi * float(frequency) * (float(samplenum)/float(sample_rate))))
		yield sample
		samplenum += 1

# totals the output of every generator for every sample
def tonesamples(sample_count, tones):
	samples = []
	for i in range(0,sample_count):
		if (i+1)%10 == 0:
			print("Generating sample {0} of {1} - {2:.2f}% completed".format((i+1), sample_count, (((i+1)/sample_count)) * 100))
		total = 0
		for tone in tones:
			total += next(tone)
		# converts sample to 16 bit integer in range [-32767,32767]
		total = int((total / float(len(tones)) * 32767.0))
		samples.append(total)
	return samples

def main(input_file, output_file, starting_note, octaves, sample_rate, duration):
	img = cv.imread(input_file, cv.IMREAD_GRAYSCALE)
	rows,cols = img.shape
	smaller_dim = 0
	if rows < cols:
		smaller_dim = rows
	else:
		smaller_dim = cols

	order = 0
	while True:
		if 2**order > smaller_dim:
			order -= 1
			break
		order += 1
	side_length = 2**order
	
	sound_step_size = octaves/((side_length**2) - 1)
	print(order)
	print(sound_step_size)

	img_scaled = cv.resize(img, (side_length, side_length), interpolation = cv.INTER_CUBIC)
	cv.waitKey(0)
	
	img_rot = cv.rotate(img_scaled,cv.ROTATE_90_CLOCKWISE)
	print(img_rot.shape)
	cv.waitKey(0)
	
	tones_list = []
	working_curve = HilbertCurve(order,2)
	for i in range(0, side_length**2):
		coords = working_curve.coordinates_from_distance(i)
		# log base 2 of starting note plus logarithmic increment
		note_log = math.log2(starting_note) + (sound_step_size * i)
		# convert back to non-logarithm
		frequency = 2**note_log
		volume = (img_rot[coords[0],coords[1]] / 255.0)
		print("Point {0} ({1},{2}): {3:.5f}Hz at {4:.2f}% volume".format(i+1,coords[0],coords[1],frequency,volume*100))
		tones_list.append(tone(frequency,volume,sample_rate))
	
	sample_count = int(sample_rate * duration)
	samples_list = tonesamples(sample_count,tones_list)
	
	with wave.open(output_file,"wb") as wave_file:
		# set params for WAV file: 1 channel, 16bit (2 byte) precision, sample rate, number of samples, no compression, not compressed
		wave_file.setparams((1,2,sample_rate,sample_count,"NONE","not compressed"))
		samplenum = 1
		for i in samples_list:
			if (samplenum)%100 == 0:
				print("Writing sample {0} of {1} - {2:.2f}% completed".format(samplenum, sample_count, ((samplenum/sample_count) * 100)))
			wave_file.writeframes(struct.pack("h", i))
			samplenum += 1
		wave_file.close()
	print("Done!")

get_inputs()