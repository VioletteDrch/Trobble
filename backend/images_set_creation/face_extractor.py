import cv2
import numpy as np
from pathlib import Path

# Parameters to tweak the cropping. All of them have to be odd numbers.
gaussian_blur = (
1, 1)  # if not capturing the face but just a forehead for example, then increment the blur to capture more
threshold = 13  # the highest the threshold, the more strict. Lower it to capture more details (hair for example)
morph_kernel = (9, 9)  # no idea, tweak when the other two are not enough

# Paths to ML model stuff for face recognition
base_path = Path(__file__).resolve().parent
prototxt_path = base_path.joinpath('deploy.prototxt')
model_path = base_path.joinpath('res_ssd_300Dim.caffeModel')


def get_face_dimensions(detections, i, height, width):
    dimensions = detections[0, 0, i, 3:7]
    start_x = int(dimensions[0] * width)
    start_y = int(dimensions[1] * height)
    end_x = int(dimensions[2] * width)
    end_y = int(dimensions[3] * height)
    return start_y, end_y, start_x, end_x


def get_contours_and_gray_face(faceRoi):
    gray_face = cv2.cvtColor(faceRoi, cv2.COLOR_BGR2GRAY)
    blurred_face = cv2.GaussianBlur(gray_face, gaussian_blur, 0)
    thresh_face = cv2.adaptiveThreshold(blurred_face, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, threshold,
                                        5)
    contours, _ = cv2.findContours(thresh_face, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, gray_face


def draw_mask(gray_face, largest_contour):
    mask = np.zeros_like(gray_face)
    cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, morph_kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def draw_final_image(height, width, start_y, end_y, start_x, end_x, face_contour, mask):
    final_image = np.zeros((height, width, 4), dtype=np.uint8)
    final_mask = np.zeros((height, width), dtype=np.uint8)
    final_mask[start_y:end_y, start_x:end_x] = mask
    final_image[start_y:end_y, start_x:end_x, :3] = face_contour
    final_image[start_y:end_y, start_x:end_x, 3] = final_mask[start_y:end_y, start_x:end_x]
    return final_image


def extract_face(picture_path, output_path):
    print(picture_path)
    if not picture_path:
        picture_path = 'pic.jpeg'
    if not output_path:
        output_path = 'cropped-face.png'

    picture = cv2.imread(picture_path)
    (height, width) = picture.shape[:2]

    face_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    blob = cv2.dnn.blobFromImage(picture, 1.0, (300, 300), (104.0, 177.0, 123.0))
    face_net.setInput(blob)

    detections = face_net.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.5:
            (start_y, end_y, start_x, end_x) = get_face_dimensions(detections, i, height, width)
            face_region = picture[start_y:end_y, start_x:end_x]
            (contours, gray_face) = get_contours_and_gray_face(face_region)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                mask = draw_mask(gray_face, largest_contour)
                mask_3channel = cv2.merge([mask, mask, mask])
                face_contour = cv2.bitwise_and(face_region, mask_3channel)
                new_height = end_y - start_y
                new_width = end_x - start_x
                final_image = draw_final_image(new_height + 1, new_width + 1, 0, new_height, 0, new_width, face_contour,
                                            mask)
                cv2.imwrite(output_path, final_image)
