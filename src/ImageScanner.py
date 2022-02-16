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
        total_w = round(info.height * 0.619)
        h = w = round(total_w * 0.655)
        x = info.x + int(total_w / 2 - w / 2)
        y = info.y + int(info.height * 0.301)

        # maybe there is a better place to put this, but we don't want to keep looking up the files
        items_map._update_images(int(w / 8))

        self._scanner_window_size = (x, y, w, h)
        self._image_src = info.src
        self._items_map = items_map
        self._confidence_threshold = 0.5
        self._over_scan = 5

        # hack: these ones looks like background or skull to algorithm
        self._score_mult = dict()
        self._score_mult['Mana Siphoner'] = 0.85
        self._score_mult['Kitava-Touched'] = 0.9
        self._score_mult['Shakari-Touched'] = 0.9
        self._score_mult['Ice Prison'] = 0.85 # similar to mana siphoner
        self._score_mult['Temporal Bubble'] = 0.9 # similar to skull, be last resort
        self._score_mult['Berserker'] = 0.95 # background too dark
        self._score_mult['Echoist'] = 0.93 # background too dark

    def matchInThread(self, screen, template, mask):
        return cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)

    def scanList(self) -> List[List[Tuple[str, float, int]]]:
        bbox = (
            self._scanner_window_size[0] - self._over_scan,
            self._scanner_window_size[1] - self._over_scan,
            self._scanner_window_size[0] + self._scanner_window_size[2] + self._over_scan,
            self._scanner_window_size[1] + self._scanner_window_size[3] + self._over_scan
        )
        if self._image_src:
            screen = self._image_src.crop(box=bbox)
        else:
            screen = ImageGrab.grab(bbox=bbox)

        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        confidencelist = [ [ None for x in range(8) ] for y in range(8) ]
        width = int(self._scanner_window_size[2] / 8) - 1

        futures = dict()

        with ThreadPoolExecutor(max_workers=max(1, os.cpu_count() - 4)) as e:
            for item in self._items_map.items():
                template, mask = self._items_map.get_scan_image(item)
                futures[e.submit(self.matchInThread, screen, template, mask)] = item
            
            for thread in as_completed(futures):
                item = futures[thread]
                score_mult = self._score_mult[item] if item in self._score_mult else 1
                
                # hack: algorithm bad at blue since background
                item_confidence_mod = 1 if item != "Brine King-Touched" else 0.97
                item_confidence_mod = item_confidence_mod if item != "Mana Siphoner" else 0.94
                item_confidence_mod = item_confidence_mod if item != "Ice Prison" else 0.94

                heat_map = thread.result()

                findings = np.where(heat_map >= self._confidence_threshold * item_confidence_mod)
                if len(findings[0]) > 0:
                    for (x, y) in zip(findings[1], findings[0]):
                        confidence = heat_map[y][x] * score_mult / item_confidence_mod
                        ax = int((x + self._over_scan) / width)
                        ay = int((y + self._over_scan) / width)
                        if confidencelist[ay][ax] is None or confidencelist[ay][ax][1] < confidence:
                            # print(f'at {ax}x{ay} found {item} @ {confidence} {"overriden" if confidencelist[ay][ax] else ""}')
                            confidencelist[ay][ax] = (item, confidence, width)
        
        return confidencelist

    def scan(self) -> Dict[str, List[Tuple[int, int, int, int]]]:
        confidencelist = self.scanList()
        results = dict()

        for y in range(8):
            for x in range(8):
                item = confidencelist[y][x]
                if item is not None:
                    if item[0] not in results:
                        results[item[0]] = []
                    results[item[0]].append((x, y, item[2], item[2]))

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