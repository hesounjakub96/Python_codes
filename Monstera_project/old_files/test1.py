import cv2
import matplotlib.pyplot as plt

img_bgr = cv2.imread("pic1.jpg")
if img_bgr is None:
    raise Exception("Obrázek nebyl nalezen.")

img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

plt.figure(figsize=(15, 8))

plt.subplot(1, 4, 1)
plt.imshow(img_bgr)
plt.title("BGR")
plt.axis("off")

plt.subplot(1, 4, 2)
plt.imshow(img_rgb)
plt.title("RGB")
plt.axis("off")

plt.subplot(1, 4, 3)
plt.imshow(img_hsv)
plt.title("HSV")
plt.axis("off")

plt.subplot(1, 4, 4)
plt.imshow(img_hsv[:, :, 0], cmap="hsv")
plt.title("Pouze H")
plt.axis("off")

plt.tight_layout()
plt.show()
