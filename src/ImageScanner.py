from concurrent.futures import ThreadPoolExecutor, as_completed
import os
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
        total_w = round(info.height * 0.62)
        h = w = round(total_w * 0.65)
        x = info.x + round(total_w / 2) - round(w / 2) - 1
        y = info.y + round((info.height - 5) * 0.3035) - 1

        items_map._update_images(int(w / 8) - 1) # maybe there is a better place to put this, but we don't want to keep looking up the files

        self._scanner_window_size = (x, y, w, h)
        self._image_src = info.src
        self._items_map = items_map
        self._confidence_threshold = 0.88

    def matchInThread(self, screen, template, mask):
        return cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)


    def scan(self) -> Dict[str, List[Tuple[int, int, int, int]]]:
        bbox = (
            self._scanner_window_size[0],
            self._scanner_window_size[1],
            self._scanner_window_size[0] + self._scanner_window_size[2],
            self._scanner_window_size[1] + self._scanner_window_size[3]
        )
        if self._image_src:
            screen = self._image_src.crop(box=bbox)
        else:
            screen = ImageGrab.grab(bbox=bbox)
        # screen.save("test/screenshot.png")
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        confidencelist = [ [ None for x in range(8) ] for y in range(8) ]
        width = int(self._scanner_window_size[2] / 8) - 1

        futures = dict()

        with ThreadPoolExecutor(max_workers=max(1, os.cpu_count() - 4)) as e:
            for item in self._items_map.items():
                template, mask, mult = self._items_map.get_scan_image(item)
                futures[e.submit(self.matchInThread, screen, template, mask)] = (item, mult)
            
            for thread in as_completed(futures):
                item, mult = futures[thread]
                heat_map = thread.result()

                findings = np.where(heat_map >= self._confidence_threshold * mult)
                if len(findings[0]) > 0:
                    for (x, y) in zip(findings[1], findings[0]):
                        confidence = heat_map[y][x] * mult
                        axf = x / width
                        ayf = y / width
                        ax = int(x / width)
                        ay = int(y / width)
                        if confidencelist[ay][ax] is None or confidencelist[ay][ax][1] < confidence:
                            print(f'at {axf}x{ayf} found {item} @ {confidence} {"overriden" if confidencelist[ay][ax] else ""}')
                            confidencelist[ay][ax] = (item, confidence)

        results = dict()

        for y in range(8):
            for x in range(8):
                item = confidencelist[y][x]
                if item is not None:
                    if item[0] not in results:
                        results[item[0]] = []
                    results[item[0]].append((x, y, width, width))

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