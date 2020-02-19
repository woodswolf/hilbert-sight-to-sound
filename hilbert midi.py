import numpy as np
import cv2 as cv
from hilbertcurve.hilbertcurve import HilbertCurve

def main():
	img = cv.imread("lion 8x8 alt.jpg", cv.IMREAD_GRAYSCALE)
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
	
	sound_step_size = (64 / ((2**order)**2))
	print(order)
	print(sound_step_size)

	img_scaled = cv.resize(img, (side_length, side_length), interpolation = cv.INTER_CUBIC)
	cv.imshow("image scaled",img_scaled)
	cv.waitKey(0)
	
	img_rot = cv.rotate(img_scaled,cv.ROTATE_90_CLOCKWISE)
	print(img_rot.shape)
	cv.imshow("image rot",img_rot)
	cv.waitKey(0)
	
	# time signature and tempo, then instrument settings for all channels
	midi = b"\x00\xFF\x58\x04\x04\x02\x18\x08" + b"\x00\xFF\x51\x03\x07\xA1\x20"
	# change instruments on all tracks to square wave
	midi += (b"\x00\xC0\x50" + b"\x00\xC1\x50" + b"\x00\xC2\x50" + b"\x00\xC3\x50" + \
		b"\x00\xC4\x50" + b"\x00\xC5\x50" + b"\x00\xC6\x50" + b"\x00\xC7\x50" + \
		b"\x00\xC8\x50" + b"\x00\xC9\x50" + b"\x00\xCA\x50" + b"\x00\xCB\x50" + \
		b"\x00\xCC\x50" + b"\x00\xCD\x50" + b"\x00\xCE\x50" + b"\x00\xCF\x50")
	# add pitch bend to channels
	midi += (b"\x00\xE0\x00\x40" + b"\x00\xE1\x00\x41" + b"\x00\xE2\x00\x42" + b"\x00\xE3\x00\x43" + \
		b"\x00\xE4\x00\x44" + b"\x00\xE5\x00\x45" + b"\x00\xE6\x00\x46" + b"\x00\xE7\x00\x47" + \
		b"\x00\xE8\x00\x48" + b"\x00\xE9\x00\x49" + b"\x00\xEA\x00\x4A" + b"\x00\xEB\x00\x4B" + \
		b"\x00\xEC\x00\x4C" + b"\x00\xED\x00\x4D" + b"\x00\xEE\x00\x4E" + b"\x00\xEF\x00\x4F")
	midi_off = b""
	
	print(midi)
	
	working_curve = HilbertCurve(order,2)
	for i in range(0, side_length**2):
		coords = working_curve.coordinates_from_distance(i)
		note = 32 + (sound_step_size * i)
		note_fraction = note - int(note)
		note_channel = int(note_fraction * 16)
		print(note)
		volume = img_rot[coords[0],coords[1]] // 2
		print(volume)
		
		note_on_channel = 144 + note_channel # generates the value of a byte of the form "\x9X" - note on event on channel X
		note_off_channel = 128 + note_channel # ditto for "\x8X" - note off event on channel X
		
		note_and_volume = int(note).to_bytes(1,byteorder="big") + int(volume).to_bytes(1,byteorder="big")
		
		midi += b"\x00" + note_on_channel.to_bytes(1,byteorder="big") + note_and_volume
		if i == 0:
			midi_off += b"\x7F"
		else:
			midi_off += b"\x00"
		midi_off += note_off_channel.to_bytes(1,byteorder="big") + note_and_volume
	
	# add note-offs and end of track
	midi += midi_off + b"\x00\xFF\x2F\x00"
	midi_header = "MThd".encode("ascii") + b"\x00\x00\x00\x06" + b"\x00\x01" + b"\x00\x01" + b"\x00\x01" + \
		"MTrk".encode("ascii") + len(midi).to_bytes(4,byteorder="big")
	
	with open("lion.midi", "wb") as midi_file:
		midi_file.write(midi_header + midi)
	cv.waitKey(0)
	cv.destroyAllWindows()

main()