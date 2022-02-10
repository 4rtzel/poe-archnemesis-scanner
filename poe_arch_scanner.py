import sys
from configparser import ConfigParser
import tkinter as tk
from typing import Callable, Any, Tuple, List, Dict

import cv2
import numpy as np
from PIL import ImageTk, Image, ImageGrab

COLOR_BG = 'grey19'
COLOR_FG_WHITE = 'snow'
COLOR_FG_GREEN = 'green3'
COLOR_FG_ORANGE = 'orange2'
FONT_BIG = ('Consolas', '14')
FONT_SMALL = ('Consolas', '9')

class ArchnemesisItemsMap:
    """
    Holds the information about all archnemesis items, recipes, images and map them together
    """
    def __init__(self, scale: float):
        # Put everything into the list so we could maintain the display order
        self._arch_items = [
            ('Kitava-Touched', ['Tukohama-Touched', 'Abberath-Touched', 'Corrupter', 'Corpse Detonator']),
            ('Innocence-Touched', ['Lunaris-Touched', 'Solaris-Touched', 'Mirror Image', 'Mana Siphoner']),
            ('Shakari-Touched', ['Entangler', 'Soul Eater', 'Drought Bringer']),
            ('Abberath-Touched', ['Flame Strider', 'Frenzied', 'Rejuvenating']),
            ('Tukohama-Touched', ['Bonebreaker', 'Executioner', 'Magma Barrier']),
            ('Brine King-Touched', ['Ice Prison', 'Storm Strider', 'Heralding Minions']),
            ('Arakaali-Touched', ['Corpse Detonator', 'Entangler', 'Assassin']),
            ('Solaris-Touched', ['Invulnerable', 'Magma Barrier', 'Empowered Minions']),
            ('Lunaris-Touched', ['Invulnerable', 'Frost Strider', 'Empowered Minions']),
            ('Effigy', ['Hexer', 'Malediction', 'Corrupter']),
            ('Empowered Elements', ['Evocationist', 'Steel-Infused', 'Chaosweaver']),
            ('Crystal-Skinned', ['Permafrost', 'Rejuvenating', 'Berserker']),
            ('Invulnerable', ['Sentinel', 'Juggernaut', 'Consecrator']),
            ('Corrupter', ['Bloodletter', 'Chaosweaver']),
            ('Mana Siphoner', ['Consecrator', 'Dynamo']),
            ('Storm Strider', ['Stormweaver', 'Hasted']),
            ('Mirror Image', ['Echoist', 'Soul Conduit']),
            ('Magma Barrier', ['Incendiary', 'Bonebreaker']),
            ('Evocationist', ['Flameweaver', 'Frostweaver', 'Stormweaver']),
            ('Corpse Detonator', ['Necromancer', 'Incendiary']),
            ('Flame Strider', ['Flameweaver', 'Hasted']),
            ('Soul Eater', ['Soul Conduit', 'Necromancer', 'Gargantuan']),
            ('Ice Prison', ['Permafrost', 'Sentinel']),
            ('Frost Strider', ['Frostweaver', 'Hasted']),
            ('Treant Horder', ['Toxic', 'Sentinel', 'Steel-Infused']),
            ('Temporal Bubble', ['Juggernaut', 'Hexer', 'Arcane Buffer']),
            ('Entangler', ['Toxic', 'Bloodletter']),
            ('Drought Bringer', ['Malediction', 'Deadeye']),
            ('Hexer', ['Chaosweaver', 'Echoist']),
            ('Executioner', ['Frenzied', 'Berserker']),
            ('Rejuvenating', ['Gargantuan', 'Vampiric']),
            ('Necromancer', ['Bombardier', 'Overcharged']),
            ('Trickster', ['Overcharged', 'Assassin', 'Echoist']),
            ('Assassin', ['Deadeye', 'Vampiric']),
            ('Empowered Minions', ['Necromancer', 'Executioner', 'Gargantuan']),
            ('Heralding Minions', ['Dynamo', 'Arcane Buffer']),
            ('Arcane Buffer', []),
            ('Berserker', []),
            ('Bloodletter', []),
            ('Bombardier', []),
            ('Bonebreaker', []),
            ('Chaosweaver', []),
            ('Consecrator', []),
            ('Deadeye', []),
            ('Dynamo', []),
            ('Echoist', []),
            ('Flameweaver', []),
            ('Frenzied', []),
            ('Frostweaver', []),
            ('Gargantuan', []),
            ('Hasted', []),
            ('Incendiary', []),
            ('Juggernaut', []),
            ('Malediction', []),
            ('Opulent', []),
            ('Overcharged', []),
            ('Permafrost', []),
            ('Sentinel', []),
            ('Soul Conduit', []),
            ('Steel-Infused', []),
            ('Stormweaver', []),
            ('Toxic', []),
            ('Vampiric', [])
        ]
        self._images = dict()
        self._update_images(scale)

    def _update_images(self, scale):
        self._scale = scale
        for item, _ in self._arch_items:
            self._images[item] = dict()
            image = self._load_image(item, scale)
            self._image_size = image.size
            self._images[item]['scan-image'] = self._create_scan_image(image)
            # Convert the image to Tk image because we're going to display it
            self._images[item]['display-image'] = ImageTk.PhotoImage(image=image)
            image = image.resize((30, 30))
            self._images[item]['display-small-image'] = ImageTk.PhotoImage(image=image)

    def _load_image(self, item: str, scale: float):
        image = Image.open(f'pictures/{item}.png')
        # Scale the image according to the input parameter
        return image.resize((int(image.width * scale), int(image.height * scale)))

    def _create_scan_image(self, image):
        # Remove alpha channel and replace it with predefined background color
        background = Image.new('RGBA', image.size, (10, 10, 32))
        image_without_alpha = Image.alpha_composite(background, image)
        scan_template = cv2.cvtColor(np.array(image_without_alpha), cv2.COLOR_RGB2BGR)
        w, h, _ = scan_template.shape

        # Crop the image to help with scanning
        return scan_template[int(h * 1.0 / 10):int(h * 2.3 / 3), int(w * 1.0 / 6):int(w * 5.5 / 6)]


    def get_scan_image(self, item):
        return self._images[item]['scan-image']

    def get_display_image(self, item):
        return self._images[item]['display-image']

    def get_display_small_image(self, item):
        return self._images[item]['display-small-image']

    def items(self):
        for item, _ in self._arch_items:
            yield item

    def recipes(self):
        for item, recipe in self._arch_items:
            if recipe:
                yield (item, recipe)

    @property
    def image_size(self):
        return self._image_size

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, scale: float) -> None:
        self._update_images(scale)


class ImageScanner:
    """
    Implements scanning algorithm with OpenCV. Maintans the scanning window to speed up the scanning.
    """
    def __init__(self, screen_width: int, screen_height: int, items_map: ArchnemesisItemsMap):
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._scanner_window_size = (0, int(self._screen_height / 4), int(self._screen_width / 3), int(self._screen_height * 2 / 3))
        self._items_map = items_map
        self._confidence_threshold = 0.94

    def scan(self) -> Dict[str, List[Tuple[int, int]]]:
        bbox = (self._scanner_window_size[0], self._scanner_window_size[1], self._scanner_window_size[0] + self._scanner_window_size[2], self._scanner_window_size[1] + self._scanner_window_size[3])
        screen = ImageGrab.grab(bbox=bbox)
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        results = dict()

        for item in self._items_map.items():
            heat_map = cv2.matchTemplate(screen, self._items_map.get_scan_image(item), cv2.TM_CCOEFF_NORMED)
            _, confidence, _, (x, y) = cv2.minMaxLoc(heat_map)
            print(f'Best match for {item}: x={x}, y={y} = {confidence}')
            findings = np.where(heat_map >= self._confidence_threshold)
            if len(findings[0]) > 0:
                results[item] = [(findings[1][i], findings[0][i]) for i in range(len(findings[0]))]
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

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height


class UIOverlay:
    """
    Overlay window using tkinter '-topmost' property
    """
    def __init__(self, root, items_map: ArchnemesisItemsMap, image_scanner: ImageScanner):
        self._items_map = items_map
        self._image_scanner = image_scanner
        self._root = root
        self._scan_results_window = None
        self._highlight_windows_to_show = list()

        self._settings = Settings(root, items_map, image_scanner)
        self._create_controls()

        self._root.configure(bg='')
        self._root.overrideredirect(True)
        self._root.geometry("+5+5")
        self._root.wm_attributes("-topmost", True)

    @staticmethod
    def create_toplevel_window(bg=''):
        w = tk.Toplevel()
        w.configure(bg=bg)
        # Hide window outline/controls
        w.overrideredirect(True)
        # Make sure the window is always on top
        w.wm_attributes("-topmost", True)
        return w

    def _create_controls(self) -> None:
        l = tk.Button(self._root, text='[X]', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        l.bind('<Button-1>', sys.exit)
        l.grid(row=0, column=0)

        settings = tk.Button(self._root, text='Settings', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        settings.bind('<Button-1>', lambda _: self._settings.show())
        settings.grid(row=0, column=1)

        self._scan_label_text = tk.StringVar(self._root, value='Scan')
        self._scan_label = tk.Button(self._root, textvariable=self._scan_label_text, fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        self._scan_label.bind("<Button-1>", self._scan)
        self._scan_label.grid(row=0, column=2)

    def _scan(self, _) -> None:
        self._scan_label_text.set('Scanning...')
        self._root.update()
        results = self._image_scanner.scan()
        if len(results) > 0:
            available_recipes = list()
            for item, recipe in self._items_map.recipes():
                screen_items = [results.get(x) for x in recipe]
                if all(screen_items):
                    available_recipes.append((item, [x[0] for x in screen_items], item in results))

            self._show_scan_results(results, available_recipes)

            self._scan_label_text.set('Hide')
            self._scan_label.bind('<Button-1>', self._hide)
        else:
            self._hide(None)

    def _hide(self, _) -> None:
        if self._scan_results_window is not None:
            self._scan_results_window.destroy()
        self._clear_highlights(None)
        self._scan_label_text.set('Scan')
        self._scan_label.bind('<Button-1>', self._scan)

    def _show_scan_results(self, results: Dict[str, List[Tuple[int, int]]], available_recipes: List[Tuple[str, List[Tuple[int, int]], bool]]) -> None:
        self._scan_results_window = UIOverlay.create_toplevel_window()
        x = int(self._image_scanner.screen_width / 3)
        self._scan_results_window.geometry(f'+{x}+0')

        last_column = 0
        if self._settings.should_display_inventory_items():
            last_column = self._show_inventory_list(results)
        self._show_available_recipes_list(available_recipes, last_column + 2)

    def _show_inventory_list(self, results: Dict[str, List[Tuple[int, int]]]) -> int:
        row = 0
        column = 0

        for item in self._items_map.items():
            inventory_items = results.get(item)
            if inventory_items is not None:
                row, column = self._show_image_and_label(item, inventory_items, COLOR_FG_WHITE, f'x{len(inventory_items)} {item}', row, column)
        return column


    def _show_available_recipes_list(self, available_recipes: List[Tuple[str, List[Tuple[int, int]], bool]], column: int) -> None:
        row = 0

        for item, inventory_items, exists_in_inventory in available_recipes:
            if exists_in_inventory:
                fg = COLOR_FG_GREEN
            else:
                fg = COLOR_FG_ORANGE
            row, column = self._show_image_and_label(item, inventory_items, fg, item, row, column)

    def _show_image_and_label(self, item, inventory_items: Tuple[int, int], highlight_color: str, label_text: str, row: int, column: int) -> Tuple[int, int]:
        image = tk.Label(self._scan_results_window, image=self._items_map.get_display_small_image(item), bg=COLOR_BG, pady=5)
        image.bind('<Enter>', lambda _, arg=inventory_items, color=highlight_color: self._highlight_items_in_inventory(arg, color))
        image.bind('<Leave>', self._clear_highlights)
        image.grid(row=row, column=column)
        tk.Label(self._scan_results_window, text=label_text, font=FONT_BIG, fg=highlight_color, bg=COLOR_BG).grid(row=row, column=column + 1, sticky='w', padx=5)
        row += 1
        if row % 10 == 0:
            column += 2
            row = 0
        return (row, column)

    def _highlight_items_in_inventory(self, inventory_items: List[Tuple[int, int]], color: str) -> None:
        self._highlight_windows_to_show = list()
        for (x, y) in inventory_items:
            x_offset, y_offset, _, _ = self._image_scanner.scanner_window_size
            x += x_offset
            y += y_offset
            width = int(self._items_map.image_size[0] * 0.7)
            height = int(self._items_map.image_size[1] * 0.7)
            w = UIOverlay.create_toplevel_window(bg=color)
            w.geometry(f'{width}x{height}+{x}+{y}')
            self._highlight_windows_to_show.append(w)

    def _clear_highlights(self, _) -> None:
        for w in self._highlight_windows_to_show:
            w.destroy()

    def run(self) -> None:
        self._root.mainloop()


class Settings:
    def __init__(self, root, items_map, image_scanner):
        self._root = root
        self._items_map = items_map
        self._image_scanner = image_scanner

        self._config = ConfigParser()
        self._config_file = 'settings.ini'

        self._config.read(self._config_file)
        if 'settings' not in self._config:
            self._config.add_section('settings')
        s = self._config['settings']

        scanner_window_size = s.get('scanner_window')
        if scanner_window_size is not None:
            self._image_scanner.scanner_window_size = tuple(map(int, scanner_window_size.replace('(', '').replace(')', '').replace(',', '').split()))
        self._items_map.scale = float(s.get('image_scale', self._items_map.scale))
        self._image_scanner.confidence_threshold = float(s.get('confidence_threshold', self._image_scanner.confidence_threshold))
        b = s.get('display_inventory_items')
        self._display_inventory_items = True if b is not None and b == 'True' else False


    def show(self) -> None:
        self._window = tk.Toplevel()

        self._window.geometry('+100+200')
        self._window.protocol('WM_DELETE_WINDOW', self._close)

        current_scanner_window = f'{self._image_scanner.scanner_window_size}'.replace('(', '').replace(')', '')
        v = tk.StringVar(self._window, value=current_scanner_window)
        self._scanner_window_entry = tk.Entry(self._window, textvariable=v)
        self._scanner_window_entry.grid(row=0, column=0)
        tk.Button(self._window, text='Set scanner window', command=self._update_scanner_window).grid(row=0, column=1)

        v = tk.DoubleVar(self._window, value=self._items_map.scale)
        self._scale_entry = tk.Entry(self._window, textvariable=v)
        self._scale_entry.grid(row=1, column=0)
        tk.Button(self._window, text='Set image scale', command=self._update_scale).grid(row=1, column=1)

        v = tk.DoubleVar(self._window, value=self._image_scanner.confidence_threshold)
        self._confidence_threshold_entry = tk.Entry(self._window, textvariable=v)
        self._confidence_threshold_entry.grid(row=2, column=0)
        tk.Button(self._window, text='Set confidence threshold', command=self._update_confidence_threshold).grid(row=2, column=1)

        c = tk.Checkbutton(self._window, text='Display inventory items', command=self._update_display_inventory_items)
        c.grid(row=3, column=0)
        if self._display_inventory_items:
            c.select()

    def _close(self) -> None:
        self._window.destroy()

    def _save_config(self) -> None:
        self._config['settings']['scanner_window'] = str(self._image_scanner.scanner_window_size)
        self._config['settings']['image_scale'] = str(self._items_map.scale)
        self._config['settings']['confidence_threshold'] = str(self._image_scanner.confidence_threshold)
        self._config['settings']['display_inventory_items'] = str(self._display_inventory_items)
        with open(self._config_file, 'w') as f:
            self._config.write(f)

    def _update_scanner_window(self) -> None:
        try:
            x, y, width, height = map(int, self._scanner_window_entry.get().replace(',', '').split())
        except ValueError:
            print('Unable to parse scanner window parameters')
            return

        scanner_window_to_show = UIOverlay.create_toplevel_window(bg='white')
        scanner_window_to_show.geometry(f'{width}x{height}+{x}+{y}')
        self._image_scanner.scanner_window_size = (x, y, width, height)
        scanner_window_to_show.after(200, scanner_window_to_show.destroy)
        self._save_config()

    def _update_scale(self) -> None:
        try:
            new_scale = float(self._scale_entry.get())
        except ValueError:
            print('Unable to parse image scale parameter')
            return
        self._items_map.scale = new_scale
        self._save_config()

    def _update_confidence_threshold(self) -> None:
        try:
            new_threshold = float(self._confidence_threshold_entry.get())
        except ValueError:
            print('Unable to parse confidence threshold parameter')
            return
        self._image_scanner.confidence_threshold = new_threshold
        self._save_config()

    def _update_display_inventory_items(self) -> None:
        self._display_inventory_items = not self._display_inventory_items
        self._save_config()

    def should_display_inventory_items(self) -> bool:
        return self._display_inventory_items


def calculate_default_scale(screen_width: int, screen_height: int) -> float:
    """
    TODO: validate the math for non 16:9 resolutions (e.g. ultrawide monitors)
    """

    # Assume that all source images have 78x78 size
    source_image_height = 78.0

    # Take 0.90 as a golden standard for 2560x1440 resolution and calculate
    # scales for other resolutions based on that
    constant = 1440.0 / (source_image_height * 0.91)
    scale = screen_height / (source_image_height * constant)

    return scale

# Create root as early as possible to initialize some modules (e.g. ImageTk)
root = tk.Tk()

# There are probably better ways to get screen resoultions but I'm lazy
screen = ImageGrab.grab()
SCREEN_WIDTH, SCREEN_HEIGHT = screen.size

items_map = ArchnemesisItemsMap(calculate_default_scale(SCREEN_WIDTH, SCREEN_HEIGHT))

image_scanner = ImageScanner(SCREEN_WIDTH, SCREEN_HEIGHT, items_map)

overlay = UIOverlay(root, items_map, image_scanner)
overlay.run()