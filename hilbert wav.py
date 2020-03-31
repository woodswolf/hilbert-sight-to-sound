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
input_file = "lion 32x32.jpg"
# Output File: The output .wav file.
output_file = "lion 32x32.wav"
# Starting Note: The bottom-most note of the output sound. Default is 110Hz (A2 in standard tuning)
starting_note = 110.0
# Octaves: The number of octaves above the starting note that the sound should span. Default is 6 (highest frequency as 7040Hz (A8)).
octaves = 6.0

# tone generator
def tone(frequency, amplitude, framerate=44100, start_sample=0):
	samplenum = start_sample
	if amplitude > 1.0:
		amplitude = 1.0
	elif amplitude < 0.0:
		amplitude = 0.0
	while True:
		sample = (float(amplitude) * math.sin(2*math.pi * float(frequency) * (float(samplenum)/float(framerate))))
		yield sample
		samplenum += 1

# totals the output of every generator for every sample
def tonesamples(sample_count, tones):
	samples = []
	for i in range(0,sample_count):
		if (i+1)%100 == 0:
			print("Generated sample " + str(i+1) + " of " + str(sample_count))
		total = 0
		for tone in tones:
			total += next(tone)
		# converts sample to 16 bit integer in range [-32767,32767]
		total = int((total / float(len(tones)) * 32767.0))
		samples.append(total)
	return samples

def main(input_file, output_file, starting_note, octaves):
	img = cv.imread(input_file, cv.IMREAD_GRAYSCALE)
	rows,cols = img.shape
	smaller_dim = 0
	if rows < cols:
		smaller_dim = rows
	else:
		smaller_dim = cols

	order = 0
	while True:
		if 2**order >= smaller_dim:
			break
		order += 1
	side_length = 2**order
	
	sound_step_size = octaves/(side_length**2)
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
		print(frequency)
		volume = (img_rot[coords[0],coords[1]] / 255.0)
		print(volume)
		tones_list.append(tone(frequency,volume))
	
	samples_list = tonesamples(220500,tones_list)
	with wave.open(output_file,"wb") as wave_file:
		wave_file.setparams((1,2,44100,220500,"NONE","not compressed"))
		samplenum = 1
		for i in samples_list:
			if (samplenum)%100 == 0:
				print("Writing sample " + str(samplenum) + " of " + str(len(samples_list)))
			wave_file.writeframes(struct.pack("h", i))
			samplenum += 1
		wave_file.close()
	print("Done!")

main()