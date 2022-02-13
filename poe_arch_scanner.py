import sys
from dataclasses import dataclass
from configparser import ConfigParser

import win32gui
from win32clipboard import *

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Any, Tuple, List, Dict

import cv2
import numpy as np
from PIL import ImageTk, Image, ImageGrab

COLOR_BG = 'grey19'
COLOR_FG_WHITE = 'snow'
COLOR_FG_GREEN = 'green3'
COLOR_FG_LIGHT_GREEN = 'DarkOliveGreen3'
COLOR_FG_ORANGE = 'orange2'
FONT_BIG = ('Consolas', '14')
FONT_SMALL = ('Consolas', '9')

@dataclass
class RecipeItemNode:
    item: str
    components: list

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
        self._small_image_size = 30
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
            image = image.resize((self._small_image_size, self._small_image_size))
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

    def get_subtree_for(self, item: str):
        tree = RecipeItemNode(item, [])
        nodes = [tree]
        while len(nodes) > 0:
            node = nodes.pop(0)
            children = self._get_item_components(node.item)
            if len(children) > 0:
                node.components = [RecipeItemNode(c, []) for c in children]
                nodes.extend(node.components)
        return tree

    def get_parent_recipes_for(self, item: str) -> []:
        parents = list()
        for parent, components in self._arch_items:
            if item in components:
                parents.append(parent)
        return parents

    def _get_item_components(self, item) -> List[str]:
        return next(l for x, l in self._arch_items if x == item)

    @property
    def image_size(self):
        return self._image_size

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, scale: float) -> None:
        self._update_images(scale)

    @property
    def small_image_size(self):
        return self._small_image_size

@dataclass
class PoeWindowInfo:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    client_width: int = 0
    client_height: int = 0
    title_bar_height: int = 0

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

class UIOverlay:
    """
    Overlay window using tkinter '-topmost' property
    """
    def __init__(self, root, info: PoeWindowInfo, items_map: ArchnemesisItemsMap, image_scanner: ImageScanner):
        self._window_info = info
        self._items_map = items_map
        self._image_scanner = image_scanner
        self._root = root
        self._scan_results_window = None
        self._recipe_browser_window = None
        self._recipe_browser_current_root = ''
        self._tooltip_window = None
        self._highlight_windows_to_show = list()
        self._scan_results_window_saved_position = (-1, 0)

        self._settings = Settings(root, items_map, image_scanner)
        self._create_controls()

        self._root.configure(bg='')
        self._root.overrideredirect(True)
        self._root.geometry(f'+{info.x + 5}+{info.y + info.title_bar_height + 5}')
        self._root.wm_attributes('-topmost', True)
        self._root.deiconify()

    @staticmethod
    def create_toplevel_window(bg=''):
        w = tk.Toplevel()
        w.configure(bg=bg)
        # Hide window outline/controls
        w.overrideredirect(True)
        # Make sure the window is always on top
        w.wm_attributes('-topmost', True)
        return w

    def _create_controls(self) -> None:
        l = tk.Button(self._root, text='[X]', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        l.bind('<Button-1>', sys.exit)
        l.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        l.grid(row=0, column=0)

        settings = tk.Button(self._root, text='Settings', fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        settings.bind('<Button-1>', lambda _: self._settings.show())
        settings.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        settings.grid(row=0, column=1)

        self._scan_label_text = tk.StringVar(self._root, value='Scan')
        self._scan_label = tk.Button(self._root, textvariable=self._scan_label_text, fg=COLOR_FG_GREEN, bg=COLOR_BG, font=FONT_SMALL)
        self._scan_label.bind("<Button-1>", self._scan)
        self._scan_label.bind('<B3-Motion>', lambda event: self._drag(self._root, -5, -5, event))
        self._scan_label.grid(row=0, column=2)

    def _drag(self, window, offset_x: int, offset_y: int, event) -> Tuple[int, int]:
        x = offset_x + event.x + window.winfo_x()
        y = offset_y + event.y + window.winfo_y()
        window.geometry(f'+{x}+{y}')
        return (x, y)

    def _scan(self, _) -> None:
        self._scan_label_text.set('Scanning...')
        self._root.update()
        results = self._image_scanner.scan()
        if len(results) > 0:
            recipes = list()
            for item, recipe in self._items_map.recipes():
                screen_items = [results.get(x) for x in recipe]
                if all(screen_items) or self._settings.should_display_unavailable_recipes():
                    recipes.append((item, [x[0] for x in screen_items if x is not None], item in results, all(screen_items)))

            self._show_scan_results(results, recipes)

            self._scan_label_text.set('Hide')
            self._scan_label.bind('<Button-1>', self._hide)
        else:
            self._hide(None)

    def _hide(self, _) -> None:
        if self._scan_results_window is not None:
            self._scan_results_window.destroy()
        if self._recipe_browser_window is not None:
            self._recipe_browser_window.destroy()
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._clear_highlights(None)
        self._scan_label_text.set('Scan')
        self._scan_label.bind('<Button-1>', self._scan)

    def _show_scan_results(self, results: Dict[str, List[Tuple[int, int]]], recipes: List[Tuple[str, List[Tuple[int, int]], bool, bool]]) -> None:
        self._scan_results_window = UIOverlay.create_toplevel_window()
        x, y = self._scan_results_window_saved_position
        if x == -1:
            x = self._window_info.x + int(self._window_info.client_width / 3)
            y = self._window_info.y + self._window_info.title_bar_height
        self._scan_results_window.geometry(f'+{x}+{y}')

        last_column = 0
        if self._settings.should_display_inventory_items():
            last_column = self._show_inventory_list(results)
        self._show_recipes_list(results, recipes, last_column + 2)

    def _show_inventory_list(self, results: Dict[str, List[Tuple[int, int]]]) -> int:
        row = 0
        column = 0

        for item in self._items_map.items():
            inventory_items = results.get(item)
            if inventory_items is not None:
                row, column = self._show_image_and_label(item, results, inventory_items, COLOR_FG_WHITE, f'x{len(inventory_items)} {item}', True, row, column)
        return column

    def _show_recipes_list(self, results: Dict[str, List[Tuple[int, int]]], recipes: List[Tuple[str, List[Tuple[int, int]], bool, bool]], column: int) -> None:
        row = 0

        for item, inventory_items, exists_in_inventory, available in recipes:
            if exists_in_inventory:
                if available:
                    fg = COLOR_FG_GREEN
                else:
                    fg = COLOR_FG_LIGHT_GREEN
            else:
                if available:
                    fg = COLOR_FG_ORANGE
                else:
                    fg = COLOR_FG_WHITE
            row, column = self._show_image_and_label(item, results, inventory_items, fg, item, available, row, column)

    def _show_image_and_label(self, item: str, results: Dict[str, List[Tuple[int, int]]], inventory_items: Tuple[int, int], highlight_color: str, label_text: str, highlight, row: int, column: int) -> Tuple[int, int]:
        image = tk.Label(self._scan_results_window, image=self._items_map.get_display_small_image(item), bg=COLOR_BG, pady=5)
        if highlight:
            image.bind('<Enter>', lambda _, arg=inventory_items, color=highlight_color: self._highlight_items_in_inventory(arg, color))
            image.bind('<Leave>', self._clear_highlights)
        image.bind('<Button-1>', lambda _, arg1=item, arg2=results: self._show_recipe_browser_tree(arg1, arg2))
        image.bind('<B3-Motion>', self._scan_results_window_drag_and_save)
        image.grid(row=row, column=column)
        tk.Label(self._scan_results_window, text=label_text, font=FONT_BIG, fg=highlight_color, bg=COLOR_BG).grid(row=row, column=column + 1, sticky='w', padx=5)
        row += 1
        if row % 10 == 0:
            column += 2
            row = 0
        return (row, column)

    def _scan_results_window_drag_and_save(self, event) -> None:
        self._scan_results_window_saved_position = self._drag(self._scan_results_window, -5, -5, event)

    def _show_recipe_browser_tree(self, item: str, results: Dict[str, List[Tuple[int, int]]]) -> None:
        if self._recipe_browser_window is not None:
            self._recipe_browser_window.destroy()
        self._destroy_tooltip_and_clear_highlights(None)
        # If the user clicks on the current root then close the tree
        if self._recipe_browser_current_root == item:
            return
        self._recipe_browser_current_root = item
        self._recipe_browser_window = UIOverlay.create_toplevel_window()
        self._recipe_browser_window.geometry(f'+{self._scan_results_window.winfo_x()}+{self._scan_results_window.winfo_y() + self._scan_results_window.winfo_height() + 40}')

        tree = self._items_map.get_subtree_for(item)
        if self._settings.should_copy_recipe_to_clipboard():
            self._copy_tree_items_to_clipboard(tree)

        def draw_tree(node, row, column):
            children_column = column
            for c in node.components:
                children_column = draw_tree(c, row + 2, children_column)
            columnspan = max(1, children_column - column)
            if node.item in results:
                bg = COLOR_FG_GREEN
            else:
                bg = COLOR_BG
            l = tk.Label(self._recipe_browser_window, image=self._items_map.get_display_small_image(node.item), bg=bg, relief=tk.SUNKEN)
            l.bind('<Button-1>', lambda _, arg1=node.item, arg2=results: self._show_recipe_browser_tree(arg1, arg2))
            l.bind('<B3-Motion>', lambda event: self._drag(self._recipe_browser_window, -5, -5, event))
            l.bind('<Enter>', lambda _, arg1=self._recipe_browser_window, arg2=results.get(node.item), arg3=node.item: self._create_tooltip_and_highlight(arg1, arg2, arg3))
            l.bind('<Leave>', self._destroy_tooltip_and_clear_highlights)
            l.grid(row=row, column=column, columnspan=columnspan)
            if len(node.components) > 0:
                f = tk.Frame(self._recipe_browser_window, bg=COLOR_BG, width=(self._items_map.small_image_size + 4) * columnspan, height=3)
                f.grid(row=row + 1, column=column, columnspan=columnspan)
            return children_column + 1
        total_columns = draw_tree(tree, 1, 0)
        for c in range(total_columns):
            self._recipe_browser_window.grid_columnconfigure(c, minsize=self._items_map.small_image_size)
        # Show parents on row 0
        parents = [RecipeItemNode(p, []) for p in self._items_map.get_parent_recipes_for(item)]
        if len(parents) > 0:
            tk.Label(self._recipe_browser_window, text='Used in:', bg=COLOR_BG, fg=COLOR_FG_GREEN, font=FONT_BIG).grid(row=0, column=0)
            for column, p in enumerate(parents):
                # Reuse the same function for convenience
                draw_tree(p, 0, column + 1)

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

    def _create_tooltip_and_highlight(self, window, inventory_items, text) -> None:
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._tooltip_window = UIOverlay.create_toplevel_window()
        self._tooltip_window.geometry(f'+{window.winfo_x()}+{window.winfo_y() - 40}')
        tk.Label(self._tooltip_window, text=text, font=FONT_BIG, bg=COLOR_BG, fg=COLOR_FG_GREEN).pack()

        if inventory_items is not None:
            self._highlight_items_in_inventory(inventory_items, COLOR_FG_GREEN)

    def _copy_tree_items_to_clipboard(self, tree):
        if len(tree.components) > 0:
            search_string = '|'.join((str(x.item) for x in tree.components))
        else:
            search_string = tree.item

        OpenClipboard()
        EmptyClipboard()
        SetClipboardText('^('+search_string+')')
        CloseClipboard()

    def _destroy_tooltip_and_clear_highlights(self, _) -> None:
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
        self._clear_highlights(None)

    def run(self) -> None:
        self._root.mainloop()


class Settings:
    def __init__(self, root, items_map, image_scanner):
        self._root = root
        self._items_map = items_map
        self._image_scanner = image_scanner
        self._window = None

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
        b = s.get('display_unavailable_recipes')
        self._display_unavailable_recipes = True if b is not None and b == 'True' else False
        b = s.get('copy_recipe_to_clipboard')
        self._copy_recipe_to_clipboard = True if b is not None and b == 'True' else False


    def show(self) -> None:
        if self._window is not None:
            return
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
        c.grid(row=3, column=0, columnspan=2)
        if self._display_inventory_items:
            c.select()

        c = tk.Checkbutton(self._window, text='Display unavailable recipes', command=self._update_display_unavailable_recipes)
        c.grid(row=4, column=0, columnspan=2)
        if self._display_unavailable_recipes:
            c.select()

        c = tk.Checkbutton(self._window, text='Copy recipe to clipboard', command=self._update_copy_recipe_to_clipboard)
        c.grid(row=5, column=0, columnspan=2)
        if self._copy_recipe_to_clipboard:
            c.select()

    def _close(self) -> None:
        if self._window is not None:
            self._window.destroy()
        self._window = None

    def _save_config(self) -> None:
        self._config['settings']['scanner_window'] = str(self._image_scanner.scanner_window_size)
        self._config['settings']['image_scale'] = str(self._items_map.scale)
        self._config['settings']['confidence_threshold'] = str(self._image_scanner.confidence_threshold)
        self._config['settings']['display_inventory_items'] = str(self._display_inventory_items)
        self._config['settings']['display_unavailable_recipes'] = str(self._display_unavailable_recipes)
        self._config['settings']['copy_recipe_to_clipboard'] = str(self._copy_recipe_to_clipboard)
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

    def _update_display_unavailable_recipes(self) -> None:
        self._display_unavailable_recipes = not self._display_unavailable_recipes
        self._save_config()

    def _update_copy_recipe_to_clipboard(self) -> None:
        self._copy_recipe_to_clipboard = not self._copy_recipe_to_clipboard
        self._save_config()

    def should_display_inventory_items(self) -> bool:
        return self._display_inventory_items

    def should_display_unavailable_recipes(self) -> bool:
        return self._display_unavailable_recipes

    def should_copy_recipe_to_clipboard(self) -> bool:
        return self._copy_recipe_to_clipboard

def show_warning(text: str) -> None:
    messagebox.showwarning('poe-archnemesis-scanner', text)

def show_error_and_die(text: str) -> None:
    # Dealing with inconveniences as Perl would
    messagebox.showerror('poe-archnemesis-scanner', text)
    sys.exit()

def get_poe_window_info() -> PoeWindowInfo:
    info = PoeWindowInfo()
    hwnd = win32gui.FindWindow(None, 'Path of Exile')
    if hwnd == 0:
        show_error_and_die('Path of Exile is not running.')

    x0, y0, x1, y1 = win32gui.GetWindowRect(hwnd)
    info.x = x0
    info.y = y0
    info.width = x1 - x0
    info.height = y1 - y0
    x0, y0, x1, y1 = win32gui.GetClientRect(hwnd)
    info.client_width = x1 - x0
    info.client_height = y1 - y0

    if info.client_width == 0 or info.client_height == 0:
        show_warning("Unable to detect Path of Exile resolution. Make sure it isn't running in the Fullscreen mode.\n\nThe tool will use your screen resolution for calculations instead.")
        screen = ImageGrab.grab()
        info.x = 0
        info.y = 0
        info.width, info.height = screen.size
        info.client_width, info.client_height = screen.size
    info.title_bar_height = info.height - info.client_height
    return info

def calculate_default_scale(info: PoeWindowInfo) -> float:
    """
    TODO: validate the math for non 16:9 resolutions (e.g. ultrawide monitors)
    """

    # Assume that all source images have 78x78 size
    source_image_height = 78.0

    # Take 0.91 as a golden standard for 2560x1440 resolution and calculate
    # scales for other resolutions based on that
    constant = 1440.0 / (source_image_height * 0.91)
    scale = info.client_height / (source_image_height * constant)

    return scale

# Create root as early as possible to initialize some modules (e.g. ImageTk)
root = tk.Tk()
root.withdraw()

info = get_poe_window_info()

items_map = ArchnemesisItemsMap(calculate_default_scale(info))

image_scanner = ImageScanner(info, items_map)

overlay = UIOverlay(root, info, items_map, image_scanner)
overlay.run()
