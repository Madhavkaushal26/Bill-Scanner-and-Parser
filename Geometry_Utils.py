import numpy as np
import cv2
from scipy.spatial import distance as dist

def order_points(pts):
    # pts is a 4×2 array like [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] 

    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :] 

    leftMost = xSorted[:2, :] #first 2 elements which are left most points
    rightMost = xSorted[2:, :]#last 2 elements which are righ most points
 
    # now, sort the left-most coordinates according to their y-coordinates so we can grab the top-left and bottom-left points, respectively
    #same things as xsorted but ab rather than x we considering y oordinates

    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
 
    # now that we have the top-left coordinate,
    # we are finding the dist of both the right points from the Top left point 
    #because this will give 2 dist, the higher would be bottom right and lesser one would be top right cause uk diagonal = more dist than side
    da = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    
    (br, tr) = rightMost[np.argsort(da)[::-1], :] #the argsort returns indices that would sort Da in ascending order.then doing [::-1] makes it descending

    # return the coordinates in top-left, top-right,bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype = "float32")


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct the set of destination points to obtain a "birds eye view",
    #  (i.e. top-down view) of the image
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst) # calculates how to map the 4 corners from the original image to the straightened rectangle
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # uses that mapping to "warp" the original image — stretching/skewing it so the selected area becomes a top-down, rectangular view

    # return the warped image
    return warped

def translate(image, x, y):
	# Define the translation matrix and perform the translation
	M = np.float32([[1, 0, x], [0, 1, y]])
	shifted = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

	# Return the translated image
	return shifted

def rotate(image, angle, center = None, scale = 1.0):
	# Grab the dimensions of the image
	(h, w) = image.shape[:2] #same as (image.shape[1], image.shape[0])

	# If the center is None, initialize it as the center of the image
	if center is None:
		center = (w / 2, h / 2)

	# Perform the rotation
	M = cv2.getRotationMatrix2D(center, angle, scale)
	rotated = cv2.warpAffine(image, M, (w, h))

	# Return the rotated image
	return rotated

def resize(image, width = None, height = None, inter = cv2.INTER_AREA):
	# initialize the dimensions of the image to be resized and
	# grab the image size
	dim = None
	(h, w) = image.shape[:2]

	# if both the width and height are None, then return the
	# original image
	if width is None and height is None:
		return image

	# check to see if the width is None
	if width is None:
		# calculate the ratio of the height and construct the
		# dimensions
		r = height / float(h)
		dim = (int(w * r), height)

	# otherwise, the height is None
	else:
		# calculate the ratio of the width and construct the
		# dimensions
		r = width / float(w)
		dim = (width, int(h * r))

	# resize the image
	resized = cv2.resize(image, dim, interpolation = inter)

	# return the resized image
	return resized