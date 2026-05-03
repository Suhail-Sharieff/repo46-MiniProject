import cv2
import numpy as np
import api

# Create a dummy image
img = np.zeros((100, 100, 3), dtype=np.uint8)
# Encode
api.encode_img_data(img, "hello", "test.png")
# Decode
img_png = cv2.imread("test.png")
print("PNG decode:", api.decode_img_data(img_png))

# Encode as JPG
api.encode_img_data(img, "hello", "test.jpg")
# Decode
img_jpg = cv2.imread("test.jpg")
print("JPG decode:", api.decode_img_data(img_jpg))
