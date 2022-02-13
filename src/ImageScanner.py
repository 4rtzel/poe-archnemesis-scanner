import numpy as np
import cv2

from typing import Dict, List, Tuple
from ArchnemesisItemsMap import ArchnemesisItemsMap
from DataClasses import PoeWindowInfo
from PIL import ImageGrab


class ImageScanner:
    """
    Implements scanning algorithm with OpenCV. Maintans the scanning window to speed up the scanning.
    """
    def __init__(self, info: PoeWindowInfo, items_map: ArchnemesisItemsMap):
        self._scanner_window_size = (
            info.x,
            info.y + int(info.client_height / 4),
            int(info.client_width / 3),
            int(info.client_height * 2 / 3)
        )
        self._items_map = items_map
        self._confidence_threshold = 0.94

    def scan(self) -> Dict[str, List[Tuple[int, int]]]:
        bbox = (
            self._scanner_window_size[0],
            self._scanner_window_size[1],
            self._scanner_window_size[0] + self._scanner_window_size[2],
            self._scanner_window_size[1] + self._scanner_window_size[3]
        )
        screen = ImageGrab.grab(bbox=bbox)
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        results = dict()

        for item in self._items_map.items():
            template = self._items_map.get_scan_image(item)
            heat_map = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, confidence, _, (x, y) = cv2.minMaxLoc(heat_map)
            print(f'Best match for {item}: x={x}, y={y} confidence={confidence}', 'too low' if confidence < self._confidence_threshold else '')
            findings = np.where(heat_map >= self._confidence_threshold)
            if len(findings[0]) > 0:
                rectangles = []
                ht, wt = template.shape[0], template.shape[1]
                for (x, y) in zip(findings[1], findings[0]):
                     # Add every box to the list twice in order to retain single (non-overlapping) boxes
                    rectangles.append([int(x), int(y), int(wt), int(ht)])
                    rectangles.append([int(x), int(y), int(wt), int(ht)])

                rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.1)
                results[item] = [(rect[0], rect[1]) for rect in rectangles]
        print(results)
        return results

    @property
    def scanner_window_size(self) -> Tuple[int, int, int, int]:
        return self._scanner_window_size

    @scanner_window_size.setter
    def scanner_window_size(self, value: Tuple[int, int, int, int]) -> None:
        self._scanner_window_size = value

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value) -> None:
        self._confidence_threshold = value
