import numpy as np
import cv2 as cv
from hilbertcurve.hilbertcurve import HilbertCurve

def main():
	img = cv.imread("lion s.jpg")
	rows,cols,channels = img.shape
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

	img_scaled = cv.resize(img, (side_length, side_length), interpolation = cv.INTER_CUBIC)
	cv.imshow("image scaled",img_scaled)
	cv.waitKey(0)
	
	img_rot = cv.rotate(img_scaled,cv.ROTATE_90_CLOCKWISE)
	print(img_rot.shape)
	cv.imshow("image rot",img_rot)
	cv.waitKey(0)
	
	working_curve = HilbertCurve(order,2)
	coords_list = []
	mhstep = (side_length**2 // 1536)
	if mhstep < 1:
		mhstep = 1
	print(mhstep)
	mh = -1
	for i in range(0, side_length**2):
		coords = working_curve.coordinates_from_distance(i)
		if (i % mhstep) == 0:
			mh += 1
		
		img_rot[coords[0],coords[1]] = microhue(mh)
	
	cv.imshow("image rotated",img_rot)
	cv.waitKey(0)
	
	img_unrot = cv.rotate(img_rot,cv.ROTATE_90_COUNTERCLOCKWISE)
	cv.imshow("image unrot",img_unrot)
	cv.imwrite("image unrot.png",img_unrot)
	cv.waitKey(0)
	cv.destroyAllWindows()

# Returns a BGR list with a specified "microhue" between 0 and 1536
def microhue(mh):
	mh = mh % 1536
	if mh < 256:
		return [0, (mh%256), 255]
	elif mh < 512:
		return [0, 255, (255-(mh%256))]
	elif mh < 768:
		return [(mh%256), 255, 0]
	elif mh < 1024:
		return [255, (255-(mh%256)), 0]
	elif mh < 1280:
		return [255, 0, (mh%256)]
	else:
		return [(255-(mh%256)), 0, 255]

main()