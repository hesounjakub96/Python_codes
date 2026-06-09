import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread("pic1.jpg")
if img is None:
    raise Exception("Obrázek nebyl nalezen.")

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # převod do RGB
# hue,sat,val -- H vrátí barvu nehledě na stín
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

k5 = np.ones((5, 5), np.uint8)  # pomocné pro budoucí odstarnění šumu
k7 = np.ones((7, 7), np.uint8)

blue_mask = cv2.inRange(hsv, np.array([90, 50, 50]), np.array(
    [130, 255, 255]))  # np.array jsou světlá a tmavá modrá v BGR
# vyšistí šum který je menší než 7x7 pixelů (kernel7)
blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, k7)

contours_blue, _ = cv2.findContours(
    blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if not contours_blue:
    raise Exception("Nebyla nalezena podložka.")

board_contour = max(contours_blue, key=cv2.contourArea)  # hranice podložky
board_mask = np.zeros_like(blue_mask)
cv2.drawContours(board_mask, [board_contour], -1, 255, thickness=cv2.FILLED)

# vybere to co je na podložce ale není modré
foreground_mask = cv2.bitwise_and(cv2.bitwise_not(blue_mask), board_mask)
foreground_mask = cv2.morphologyEx(
    foreground_mask, cv2.MORPH_CLOSE, k5)  # jemnější čištění (kernel5)

black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array(
    [180, 255, 60]))  # nalezne černý čtverec (černá až modrá)
# černá část na modré masce
black_mask = cv2.bitwise_and(black_mask, board_mask)
black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, k5)  # jemné čistění

contours_black, _ = cv2.findContours(
    black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

square_contours = []
for cnt in contours_black:
    # budeme ignorovat černé oblasti navíc
    if cv2.contourArea(cnt) < 5000 or cv2.contourArea(cnt) > 150000:
        continue
    peri = cv2.arcLength(cnt, True)  # obvod uzavřeného obrazce
    approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)

    if len(approx) == 4:  # počet vrcholů - čtyřuhelník
        x_sq, y_sq, w_r, h_r = cv2.boundingRect(approx)
        # poměr stran by měl vyjít 1.. fotka může být na křivo tak dáme toleranci
        if 0.8 < (w_r / float(h_r)) < 1.2:
            square_contours.append(approx)

if not square_contours:
    raise Exception("Nebyl nalezen referenční čtverec.")

# spočteme úhel natočení na základě největšího čtverce
largest_square = max(square_contours, key=cv2.contourArea)
_, (w_sq, h_sq), angle = cv2.minAreaRect(largest_square)

# "první" hrana čtverce může být natočená celkem libovolně, takže jí otočíme tak aby směřovala přibližně ve směru x
if angle < -45:
    angle += 90
elif angle > 45:
    angle -= 90

(h, w) = img_rgb.shape[:2]
rotation_matrix = cv2.getRotationMatrix2D(
    (w // 2, h // 2), angle, 1.0)  # matice rotace

rotated_img = cv2.warpAffine(
    img_rgb, rotation_matrix, (w, h))  # aplikujeme na pic
rotated_mask = cv2.warpAffine(foreground_mask, rotation_matrix, (w, h))

# Používáme RETR_TREE, abychom získali i hierarchii (vnitřní díry)
contours_rot, hierarchy = cv2.findContours(
    rotated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
)

if not contours_rot or hierarchy is None:
    raise Exception("Po otočení nebyl nalezen list.")

hierarchy = hierarchy[0]  # Zploštění matice hierarchie

# Najdeme index největší kontury (samotný list)
leaf_idx = max(range(len(contours_rot)),
               key=lambda i: cv2.contourArea(contours_rot[i]))
leaf_contour = contours_rot[leaf_idx]

x, y, width_px, height_px = cv2.boundingRect(leaf_contour)

# Měřítko z již otočeného referenčního čtverce
avg_side_px = (w_sq + h_sq) / 2.0
pixels_per_cm = avg_side_px / 5.0

# Přepočtení pixelů na cm
width_cm = width_px / pixels_per_cm
height_cm = height_px / pixels_per_cm

pocet_vnitrnich = 0
pocet_zarezu = 0

vnitrni_body = []
zarezy_body = []
zahozene_body = []

for i, h_info in enumerate(hierarchy):
    if h_info[3] == leaf_idx:
        area = cv2.contourArea(contours_rot[i])
        if area > 100:
            pocet_vnitrnich += 1
            M = cv2.moments(contours_rot[i])
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                vnitrni_body.append((cx, cy))

hull_indices = cv2.convexHull(leaf_contour, returnPoints=False)

if len(hull_indices) > 3:
    defects = cv2.convexityDefects(leaf_contour, hull_indices)

    if defects is not None:
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            hloubka_px = d / 256.0

            nejhlubsi_bod = tuple(leaf_contour[f][0])

            if hloubka_px > 100:
                pocet_zarezu += 1
                zarezy_body.append(nejhlubsi_bod)
            else:
                zahozene_body.append(nejhlubsi_bod)

celkovy_pocet_der = pocet_vnitrnich + max(0, pocet_zarezu - 1)

print(f"Vnitřní: {pocet_vnitrnich}, Všechny zářezy (včetně stonku): {pocet_zarezu} -> Výsledek: {celkovy_pocet_der}")


debug_img = rotated_img.copy()
cv2.drawContours(debug_img, [leaf_contour], -1, (0, 255, 0), 2)
cv2.rectangle(debug_img, (x, y), (x + width_px, y + height_px), (255, 0, 0), 3)


# 1. Zahozené body (Zelené křížky) - pro ladění
for bod in zahozene_body:
    cv2.drawMarker(debug_img, bod, (0, 255, 0),
                   markerType=cv2.MARKER_TILTED_CROSS, markerSize=20, thickness=3)

# 2. Vnitřní díry (Modré plné tečky)
for bod in vnitrni_body:
    cv2.circle(debug_img, bod, 10, (255, 0, 0), -1)

# 3. Vnější zářezy (Červené plné tečky)
for bod in zarezy_body:
    cv2.circle(debug_img, bod, 10, (0, 0, 255), -1)

texty = [
    f"Width: {width_cm:.2f} cm",
    f"Height: {height_cm:.2f} cm",
    f"Holes: {celkovy_pocet_der}"
]

for i, text in enumerate(texty):
    cv2.putText(
        debug_img,
        text,
        (120, 120 + i * 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        4,
        (255, 255, 0),
        3,
    )

plt.figure(figsize=(10, 14))
plt.imshow(debug_img)
plt.axis("off")
plt.show()
