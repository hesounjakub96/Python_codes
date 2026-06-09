import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread("pic1.jpg")
if img is None:
    raise Exception("Obrázek 'pic1.jpg' nebyl nalezen.")

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_blue = np.array([90, 50, 50])
upper_blue = np.array([130, 255, 255])
blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

kernel_7 = np.ones((7, 7), np.uint8)
blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel_7)
blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel_7)

contours_blue, _ = cv2.findContours(
    blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if len(contours_blue) == 0:
    raise Exception("Nebyla nalezena modrá oblast")

board_contour = max(contours_blue, key=cv2.contourArea)

board_mask_precise = np.zeros(blue_mask.shape, dtype=np.uint8)
cv2.drawContours(board_mask_precise, [
                 board_contour], -1, 255, thickness=cv2.FILLED)
isolated_board = cv2.bitwise_and(img_rgb, img_rgb, mask=board_mask_precise)

foreground_mask = cv2.bitwise_not(blue_mask)
foreground_mask = cv2.bitwise_and(foreground_mask, board_mask_precise)

kernel_5 = np.ones((5, 5), np.uint8)
foreground_mask = cv2.morphologyEx(foreground_mask, cv2.MORPH_OPEN, kernel_5)
foreground = cv2.bitwise_and(
    isolated_board, isolated_board, mask=foreground_mask)

fig, ax = plt.subplots(1, 3, figsize=(18, 6))

ax[0].imshow(img_rgb)
ax[0].set_title("Orig")
ax[0].axis("off")

ax[1].imshow(foreground_mask, cmap="gray")
ax[1].set_title("Mask")
ax[1].axis("off")

ax[2].imshow(foreground)
ax[2].set_title("Result")
ax[2].axis("off")

plt.tight_layout()
plt.show()
