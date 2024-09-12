import cv2
import numpy as np
import sys

#Parameters to tweak the cropping. All of them have to be odd numbers.
gaussian_blur = (1, 1) # if not capturing the face but just a forehead for example, then increment the blur to capture more
threshold = 13 #the highest the threshold, the more strict. Lower it to capture more details (hair for example)
morph_kernel = (9, 9) # no idea, tweak when the other two are not enough

# ML model stuff for face recognition
prototxt_path = 'deploy.prototxt'
model_path = 'res_ssd_300Dim.caffeModel'

def getFaceDimensions(detections, i, height, width):
    dimensions = detections[0, 0, i, 3:7]
    startX = int(dimensions[0] * width)
    startY = int(dimensions[1] * height)
    endX = int(dimensions[2] * width)
    endY = int(dimensions[3] * height)
    return (startY, endY, startX, endX)

def getContoursAndGrayFace(faceRoi):
    gray_face = cv2.cvtColor(faceRoi, cv2.COLOR_BGR2GRAY)
    blurred_face = cv2.GaussianBlur(gray_face, gaussian_blur, 0)
    thresh_face = cv2.adaptiveThreshold(blurred_face, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, threshold, 5)
    contours, _ = cv2.findContours(thresh_face, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return (contours, gray_face)

def drawMask(grayFace, largestContour):
    mask = np.zeros_like(grayFace)
    cv2.drawContours(mask, [largestContour], -1, (255), thickness=cv2.FILLED)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask

def drawFinalImage(height, width, startY, endY, startX, endX, faceContour, mask):
    finalImage = np.zeros((height, width, 4), dtype=np.uint8)
    finalMask = np.zeros((height, width), dtype=np.uint8)
    finalMask[startY:endY, startX:endX] = mask
    finalImage[startY:endY, startX:endX, :3] = faceContour
    finalImage[startY:endY, startX:endX, 3] = finalMask[startY:endY, startX:endX]
    return finalImage

picturePath = sys.argv[1]
outputPath = sys.argv[2]
if not picturePath:
    picturePath = 'pic.jpeg'
if not outputPath:
    outputPath = 'cropped-face.png'

picture = cv2.imread(picturePath)
(height, width) = picture.shape[:2]

face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

blob = cv2.dnn.blobFromImage(picture, 1.0, (300, 300), (104.0, 177.0, 123.0))
face_net.setInput(blob)

detections = face_net.forward()

for i in range(0, detections.shape[2]):
    confidence = detections[0, 0, i, 2]

    if confidence > 0.5:
        (startY, endY, startX, endX) = getFaceDimensions(detections, i, height, width)
        faceRegion = picture[startY:endY, startX:endX]
        (contours, grayFace) = getContoursAndGrayFace(faceRegion)

        if contours:
            largestContour = max(contours, key=cv2.contourArea)
            mask = drawMask(grayFace, largestContour)
            mask_3channel = cv2.merge([mask, mask, mask])
            faceContour = cv2.bitwise_and(faceRegion, mask_3channel)
            new_height = endY - startY
            new_width = endX - startX
            finalImage = drawFinalImage(new_height + 1, new_width + 1, 0, new_height, 0, new_width, faceContour, mask)
            cv2.imwrite(outputPath, finalImage)
