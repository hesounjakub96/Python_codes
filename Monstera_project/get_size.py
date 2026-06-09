import numpy as np
import cv2
import matplotlib.pyplot as plt


class LeafAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path

        self.img_bgr = cv2.imread(file_path)
        if self.img_bgr is None:
            raise Exception(f"Obrázek nebyl nalezen: {file_path}")
        self.img_rgb = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2RGB)
        self.hsv = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2HSV)

        self.board_mask, self.blue_mask = self._find_background()
        self.foreground_mask = self._detect_items_on_background()

        self.reference_square = self._detect_reference_square()
        self.pixels_per_cm = self._calculate_pixels_per_cm()

        self.rotation_matrix = self._get_rotation_matrix()
        self.rotated_mask = cv2.warpAffine(
            self.foreground_mask, self.rotation_matrix,
            (self.foreground_mask.shape[1], self.foreground_mask.shape[0])
        )

        self._analyze_leaf_contours()

    def _find_background(self) -> tuple[np.ndarray, np.ndarray]:
        k7 = np.ones((7, 7), np.uint8)
        blue_mask = cv2.inRange(self.hsv, np.array(
            [90, 50, 50]), np.array([130, 255, 255]))
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, k7)

        contours_blue, _ = cv2.findContours(
            blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours_blue:
            raise Exception(f"Nebyla nalezena podložka  ({self.file_path}).")

        board_contour = max(contours_blue, key=cv2.contourArea)
        board = np.zeros_like(blue_mask)
        cv2.drawContours(board, [board_contour], -1, 255, thickness=cv2.FILLED)
        return board, blue_mask

    def _detect_items_on_background(self) -> np.ndarray:
        k5 = np.ones((5, 5), np.uint8)
        foreground_mask = cv2.bitwise_and(
            cv2.bitwise_not(self.blue_mask), self.board_mask)
        return cv2.morphologyEx(foreground_mask, cv2.MORPH_CLOSE, k5)

    def _detect_reference_square(self) -> np.ndarray:
        k5 = np.ones((5, 5), np.uint8)
        black_mask = cv2.inRange(self.hsv, np.array(
            [0, 0, 0]), np.array([180, 255, 60]))
        black_mask = cv2.bitwise_and(black_mask, self.board_mask)
        black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, k5)

        contours_black, _ = cv2.findContours(
            black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        square_contours = []
        for cnt in contours_black:
            if cv2.contourArea(cnt) < 5000 or cv2.contourArea(cnt) > 150000:
                continue
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)

            if len(approx) == 4:
                _, _, w_r, h_r = cv2.boundingRect(approx)
                if 0.8 < (w_r / float(h_r)) < 1.2:
                    square_contours.append(approx)

        if not square_contours:
            raise Exception(
                f"Nebyl nalezen referenční čtverec ({self.file_path}).")
        return max(square_contours, key=cv2.contourArea)

    def _calculate_pixels_per_cm(self) -> float:
        _, (w_sq, h_sq), _ = cv2.minAreaRect(self.reference_square)
        avg_side_px = (w_sq + h_sq) / 2.0
        return avg_side_px / 5.0

    def _get_rotation_matrix(self) -> np.ndarray:
        _, _, angle = cv2.minAreaRect(self.reference_square)
        if angle < -45:
            angle += 90
        elif angle > 45:
            angle -= 90
        h, w = self.foreground_mask.shape[:2]
        return cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)

    def _analyze_leaf_contours(self):
        self.contours_rot, hierarchy = cv2.findContours(
            self.rotated_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        if not self.contours_rot or hierarchy is None:
            raise Exception("Nebyl nalezen list  ({self.file_path}).")

        self.hierarchy = hierarchy[0]
        self.leaf_idx = max(range(len(self.contours_rot)),
                            key=lambda i: cv2.contourArea(self.contours_rot[i]))
        self.leaf_contour = self.contours_rot[self.leaf_idx]

    def get_size(self) -> tuple[float, float]:
        _, _, width_px, height_px = cv2.boundingRect(self.leaf_contour)
        width_cm = width_px / self.pixels_per_cm
        height_cm = height_px / self.pixels_per_cm
        return round(width_cm, 2), round(height_cm, 2)

    def get_number_of_fenestration(self) -> int:
        inner_count, outer_count, _, _, _ = self._process_fenestration_details()
        return inner_count, max(0, outer_count - 1)

    def _process_fenestration_details(self):
        inner_points = []
        outer_count = 0
        discarded_points = []
        outer_notches_points = []

        for i, h_info in enumerate(self.hierarchy):
            if h_info[3] == self.leaf_idx:
                area = cv2.contourArea(self.contours_rot[i])
                M = cv2.moments(self.contours_rot[i])
                if 100 < area < 10000:
                    if M["m00"] != 0:
                        inner_points.append(
                            (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                elif area > 10000:
                    outer_notches_points.append(
                        (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))
                    outer_count += 1

        hull_indices = cv2.convexHull(self.leaf_contour, returnPoints=False)
        if len(hull_indices) > 3:
            defects = cv2.convexityDefects(self.leaf_contour, hull_indices)
            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    bod = tuple(self.leaf_contour[f][0])
                    if d / 256.0 > 100:
                        outer_count += 1
                        outer_notches_points.append(bod)
                    else:
                        discarded_points.append(bod)

        return len(inner_points), outer_count, inner_points, outer_notches_points, discarded_points

    def visualize(self):
        rotated_img = cv2.warpAffine(
            self.img_rgb, self.rotation_matrix, (self.img_rgb.shape[1], self.img_rgb.shape[0]))
        debug_img = rotated_img.copy()

        width_cm, height_cm = self.get_size()
        inner_fenestration, outer_fenestration = self.get_number_of_fenestration()
        _, _, inner_pts, outer_pts, disc_pts = self._process_fenestration_details()

        cv2.drawContours(debug_img, [self.leaf_contour], -1, (0, 255, 0), 2)
        x, y, w_px, h_px = cv2.boundingRect(self.leaf_contour)
        cv2.rectangle(debug_img, (x, y), (x + w_px, y + h_px), (255, 0, 0), 3)

        for bod in disc_pts:
            cv2.drawMarker(debug_img, bod, (0, 255, 0),
                           markerType=cv2.MARKER_TILTED_CROSS, markerSize=20, thickness=3)
        for bod in inner_pts:
            cv2.circle(debug_img, bod, 15, (255, 0, 0), -1)
        for bod in outer_pts:
            cv2.circle(debug_img, bod, 15, (0, 0, 255), -1)

        texts = [f"Width: {width_cm:.2f} cm", f"Height: {height_cm:.2f} cm",
                 f"Outer: {outer_fenestration}", f"Inner: {inner_fenestration}"]
        for i, text in enumerate(texts):
            cv2.putText(debug_img, text, (120, 120 + i * 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 0), 3)

        plt.figure(figsize=(10, 14))
        plt.imshow(debug_img)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    FILE = "pic1.jpg"
    analyzer = LeafAnalyzer(FILE)

    width, height = analyzer.get_size()
    inner, outer = analyzer.get_number_of_fenestration()

    print(f"Width: {width}")
    print(f"Height: {height}")
    print(f"Inner fenestrations: {inner}")
    print(f"Outer fenestration: {outer}")

    analyzer.visualize()
