from collections import defaultdict
import numpy as np
import cv2

from typing import Dict, List, Tuple
from ArchnemesisItemsMap import ArchnemesisItemsMap
from DataClasses import PoeWindowInfo
from PIL import ImageGrab
from constants import INVENTORY_SIZE


class ImageScanner:
    """
    Implements scanning algorithm with OpenCV. Maintans the scanning window to speed up the scanning.
    """
    def __init__(self, info: PoeWindowInfo, items_map: ArchnemesisItemsMap, args):
        self._args = args
        # I wasn't able to find the actual function that would give me the right sizes so
        # I got these numbers empirically. They are far from perfect, but should work for most
        # resolutions. Probably the better way is to have a mapping for all resolutions
        # and their inventory window sizes, and fallback to these calculations only when needed.
        width_and_height = round(info.client_height * 0.407)
        high_res_compensation = 7
        if info.client_height >= 1440:
            # This is my awful attempt to fix the calculations for high resolutions.
            high_res_compensation = round(info.client_height * 0.006)
        x = args.scanner_window_x if args.scanner_window_x != -1 else info.x + int(info.client_height * 0.115) - high_res_compensation
        y = args.scanner_window_y if args.scanner_window_y != -1 else info.y + (info.height - info.client_height) + int(info.client_height * 0.313) + high_res_compensation
        w = args.scanner_window_width if args.scanner_window_width != -1 else width_and_height
        h = args.scanner_window_height if args.scanner_window_height != -1 else width_and_height
        self._scanner_window_size = (
            x,
            y,
            w,
            h
        )
        print(f'Scanner window: x={x}, y={y}, width={w}, height={h}')

        self._slot_size = width_and_height / INVENTORY_SIZE
        self._items_map = items_map
        self._confidence_threshold = 0.88

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
        if self._args.show_capture_image:
            cv2.imshow('', screen)
            cv2.waitKey(0)

        results = defaultdict(list)

        slots = [[None for _ in range(INVENTORY_SIZE)] for _ in range(INVENTORY_SIZE)]

        for item in self._items_map.items():
            template = self._items_map.get_scan_image(item)
            heat_map = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

            findings = np.where(heat_map >= self._confidence_threshold)
            if len(findings[0]) > 0:
                rectangles = []
                ht, wt = template.shape[0], template.shape[1]
                for (x, y) in zip(findings[1], findings[0]):
                     # Add every box to the list twice in order to retain single (non-overlapping) boxes
                    rectangles.append([int(x), int(y), int(wt), int(ht)])
                    rectangles.append([int(x), int(y), int(wt), int(ht)])

                rectangles, _ = cv2.groupRectangles(rectangles, 1, 0.1)
                for (x, y) in [(rect[0], rect[1]) for rect in rectangles]:
                    column = int(x / self._slot_size)
                    row = int(y / self._slot_size)
                    confidence = heat_map[y][x]
                    if slots[row][column] is None or slots[row][column][1] < confidence:
                        slots[row][column] = (item, confidence, x, y)
        total_items_found = 0
        for row in range(INVENTORY_SIZE):
            for column in range(INVENTORY_SIZE):
                if slots[row][column] is not None:
                    print(f'row={row+1}, column={column+1}, item={slots[row][column][0]}, confidence={slots[row][column][1]}')
                    results[slots[row][column][0]].append((slots[row][column][2], slots[row][column][3]))
                    total_items_found += 1
                else:
                    print(f'row={row+1}, column={column+1} is empty')
        print(f'Items found: {total_items_found}/{INVENTORY_SIZE * INVENTORY_SIZE}')
        return results

    @property
    def scanner_window_size(self) -> Tuple[int, int, int, int]:
        return self._scanner_window_size

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value) -> None:
        self._confidence_threshold = value
